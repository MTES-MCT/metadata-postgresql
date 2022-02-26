"""Administration des données de l'extension PostgreSQL PlumePg.

Pour regénérer la requête d'import des métadonnées communes:

    >>> query_from_shape()

Pour importer en local les modèles préconfigurés de PlumePg:

    >>> store_sample_templates()

Cette commande met à jour le fichier ``/plume/pg/data/templates.json``.

"""

import re
from psycopg2 import sql, connect
from json import dump

from rdflib.term import URIRef

from plume.rdf.namespaces import DCAT, SH, PlumeNamespaceManager
from plume.rdf.utils import abspath
from plume.rdf.properties import class_properties
from plume.pg.queries import query_get_categories, query_template_tabs
from plume.pg.tests.connection import ConnectionString

nsm = PlumeNamespaceManager()

def table_from_shape(no_cast=False):
    """Renvoie une représentation du schéma SHACL sous forme de table.
    
    Le résultat correspond au contenu de la table
    ``z_plume.meta_shared_categorie`` de l'extension PostgreSQL
    PlumePg, en vue de la mise à jour de celle-ci.
    
    Les valeurs nécessitant une conversion explicite de
    type sont représentées par des tuples dont le premier élément
    est ``'cast'``, le second la valeur, le troisième le type.
    
    Parameters
    ----------
    no_cast : bool, default False
        Si ``True``, les valeurs qui auraient nécessité une
        conversion explicite de type seront représentées
        comme les autres et non par des tuples contenant
        l'information sur le type. Un tel résulat ne pourra
        être utilisé pour construire une requête SQL, mais peut
        avoir d'autres usages.
    
    Returns
    -------
    list of tuples
    
    """
    categories = []
    _table_from_shape(categories, DCAT.Dataset, no_cast=no_cast)
    return categories
    
def _table_from_shape(categories, rdfclass, path=None, no_cast=False):
    properties, predicates = class_properties(rdfclass=rdfclass,
        nsm=nsm, base_path=path)
    for prop in properties:
        prop_dict = prop.prop_dict
        kind = prop_dict.get('kind')
        datatype = prop_dict.get('datatype')
        order_idx = prop_dict.get('order_idx')
        sources = prop_dict.get('sources')
        geo_tools = prop_dict.get('geo_tools')
        compute = prop_dict.get('compute')
        rowspan = prop_dict.get('rowspan')
        category = (
            prop.n3_path,
            prop.origin,
            prop_dict.get('label'),
            prop_dict.get('description'),
            prop_dict.get('transform') or ('url' \
                if kind in (SH.IRI, SH.BlankNodeOrIRI) else None),
            kind == SH.BlankNode,
            datatype.n3(nsm) if datatype else None,
            bool(prop_dict.get('is_long_text')),
            rowspan.toPython() if rowspan is not None else None,
            prop_dict.get('placeholder'),
            prop_dict.get('input_mask'),
            prop_dict.get('is_multiple', False),
            bool(prop_dict.get('unilang')),
            prop_dict.get('is_mandatory', False),
            [str(s) for s in sources] if sources else None,
            ('cast', geo_tools, 'z_plume.meta_geo_tool[]') if geo_tools \
                and not no_cast else geo_tools,
            ('cast', compute, 'z_plume.meta_compute[]') if compute \
                and not no_cast else compute,
            order_idx[1] if order_idx else None
            )
            # lorsqu'il est nécessaire de caster la valeur, on
            # donne à category un tuple ('cast', valeur, 'nom du type'),
            # comme pour geo_tools
        categories.append(category)
        if kind in (SH.BlankNode, SH.BlankNodeOrIRI):
            _table_from_shape(categories, prop_dict.get('rdfclass'),
                path=prop.path, no_cast=no_cast)

def query_from_shape():
    """Génère la requête permettant de reconstituer la table des catégories communes de PgPlume.

    À l'usage de l'extension PostgreSQL PgPlume. L'utilisation de cette
    fonction requiert une connexion PostgreSQL (paramètres saisis
    dynamiquement).

    Returns
    -------
    str
        Requête ``INSERT`` sur la table ``z_plume.meta_categorie``
        de l'extension (qui mettra à jour la partition
        ``z_plume.meta_shared_categorie``).
    
    """
    connection_string = ConnectionString()
    
    t = table_from_shape()

    conn = connect(connection_string)
    s = sql.SQL("""INSERT INTO z_plume.meta_categorie (
        path, origin, label, description, special,
        is_node, datatype, is_long_text, rowspan,
        placeholder, input_mask, is_multiple, unilang,
        is_mandatory, sources, geo_tools, compute,
        template_order
    ) VALUES
    {} ;""").format(
        sql.SQL(",\n    ").join(
            [ sql.SQL("({})").format(
                sql.SQL(", ").join(
                    [ sql.SQL("{}::{}").format(sql.Literal(e[1]), sql.SQL(e[2])) 
                        if isinstance(e, tuple) and e[0] == 'cast'
                        else sql.Literal(e) for e in v ]
                    )
                ) for v in t ]
            )
        ).as_string(conn)
    conn.close()
    
    print(s)
    return s

def store_sample_templates():
    """Importe depuis PostgreSQL et écrit dans le fichier dédié les modèles pré-configurés de PlumePg.
    
    """
    connection_string = ConnectionString()
    data = {}
    conn = connect(connection_string)
    with conn:
        with conn.cursor() as cur:
            cur.execute('DROP EXTENSION IF EXISTS plume_pg ; CREATE EXTENSION plume_pg')
            cur.execute('SELECT * FROM z_plume.meta_import_sample_template()')
            cur.execute('SELECT array_agg(tpl_label ORDER BY priority) FROM z_plume.meta_template')
            labels = cur.fetchone()[0]
            for label in labels:
                cur.execute('SELECT * FROM z_plume.meta_template WHERE tpl_label = %s',
                    (label,))
                conditions = cur.fetchone()
                cur.execute(
                    query_get_categories(),
                    (label,)
                    )
                categories = cur.fetchall()
                cur.execute(
                    query_template_tabs(),
                    (label,)
                    )
                tabs = cur.fetchall()
                data[label] = {'categories': categories, 'tabs': tabs, 'conditions': conditions}
            cur.execute('DROP EXTENSION plume_pg ; CREATE EXTENSION plume_pg')
    conn.close()
    with open(abspath('pg/data/templates.json'), 'w',
        encoding='utf-8') as dest:
        dump(data, dest, ensure_ascii=False, indent=4)

