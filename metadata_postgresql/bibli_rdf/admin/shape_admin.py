"""
Utilitaires pour la maintenance du schéma SHACL décrivant les métadonnées communes.

"""

from rdflib import Graph, URIRef
from rdflib.namespace import NamespaceManager

from metadata_postgresql.bibli_rdf.rdf_utils import load_shape


def table_from_shape(
    mList=None, mPath=None, mNSManager=None,
    mTargetClass=URIRef("http://www.w3.org/ns/dcat#Dataset")
    ):
    """Représentation du schéma SHACL sous forme de table.
    
    ARGUMENTS
    ---------
    Néant.
    NB. mList, mPath, etc. servent aux appels récursifs, ils n'ont
    aucunement vocation à être renseignés manuellement.
    
    RESULTAT
    --------
    Une liste de tuples correspondant aux enregistrements de la table
    z_metadata.meta_shared_categorie hors champ serial (en vue de la
    mise à jour de celle-ci).
    """
    if mList is None:
        mList = []
    
    shape = load_shape()
    
    nsm = mNSManager or shape.namespace_manager
    
    q_tp = shape.query(
        """
        SELECT
            ?property ?name ?kind
            ?class ?order ?widget ?descr
            ?default ?min ?max
            ?placeholder ?rowspan ?mask
        WHERE
            { ?u sh:targetClass ?c .
              ?u sh:property ?x .
              ?x sh:path ?property .
              ?x sh:name ?name .
              ?x sh:nodeKind ?kind .
              ?x sh:order ?order .
              OPTIONAL { ?x snum:widget ?widget } .
              OPTIONAL { ?x sh:class ?class } .
              OPTIONAL { ?x sh:description ?descr } .
              OPTIONAL { ?x snum:placeholder ?placeholder } .
              OPTIONAL { ?x snum:inputMask ?mask } .
              OPTIONAL { ?x sh:defaultValue ?default } .
              OPTIONAL { ?x snum:rowSpan ?rowspan } .
              OPTIONAL { ?x sh:minCount ?min } .
              OPTIONAL { ?x sh:maxCount ?max } . }
        ORDER BY ?order
        """,
        initBindings = { 'c' : mTargetClass }
        )
    
    for p in q_tp:
        
        mKind = p['kind'].n3(nsm)
        mNPath = ( mPath + " / " if mPath else '') + p['property'].n3(nsm)
        
        mList.append((
            'shared',
            mNPath,
            str(p['name']) if p['name'] else None,
            str(p['widget']) if p['widget'] else None,
            int(p['rowspan']) if p['rowspan'] else None,
            str(p['descr']) if p['descr'] else None,
            str(p['default']) if p['default'] else None,
            str(p['placeholder']) if p['placeholder'] else None,
            str(p['mask']) if p['mask'] else None,
            int(p['max']) > 1 if p['max'] else True,
            int(p['min']) >= 1 if p['min'] else False,
            int(p['order']) if p['order'] else None
            ))
        
        if mKind in ('sh:BlankNode', 'sh:BlankNodeOrIRI'):
            table_from_shape(mList, mNPath, nsm, p['class'])
            
    return mList ;
    
    
    
