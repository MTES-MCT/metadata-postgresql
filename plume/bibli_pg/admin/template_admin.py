"""Utilitaires pour la gestion des modèles pré-implémentés de metadata.
"""

from psycopg2 import sql
import re, psycopg2
from json import dump

from plume.bibli_pg.pg_queries import query_get_categories, query_template_tabs
from plume.bibli_pg.template_utils import build_template, build_template_tabs
from plume.bibli_pg import __path__

def export_sample_templates(load=False):
    """Exporte en JSON les modèles pré-implémentés de l'extension PG metadata.

    L'utilisation de cette fonction requiert une connexion PostgreSQL vers une
    base PostgreSQL sur laquelle l'extension metadata est installée (paramètres
    saisis dynamiquement).

    ARGUMENTS
    ---------
    - load (bool) : si True, la commande de chargement des templates
    sera exécutée préalablement à l'export. False par défaut.

    RESULTAT
    --------
    Pas de valeur renvoyée. Les modèles sont sauvegardés dans le sous-dossier
    "export".
    
    Si l'un des modèles recherchés ("Basique", "Classique" et "Données externes")
    n'est pas disponible, un message d'avertissement est imprimé dans la console.
    """
    connection_string = "host={} port={} dbname={} user={} password={}".format(
        input('host (localhost): ') or 'localhost',
        input('port (5432): ') or '5432',
        input('dbname (metadata_dev): ') or 'metadata_dev',
        input('user (postgres): ') or 'postgres',
        input('password : ')
        )
    
    l = {
        "Basique": "basique",
        "Classique": "classique",
        "Donnée externe": "donnee_externe"
        }
    
    conn = psycopg2.connect(connection_string)

    if load:
        with conn:
            with conn.cursor() as cur:            
                cur.execute(
                    "SELECT * FROM z_metadata.meta_import_sample_template()"
                    )
    
    for tpl_label in l.keys():
    
        with conn:
            with conn.cursor() as cur:            
                cur.execute(query_get_categories(), (tpl_label,))
                categories = cur.fetchall()

        template = build_template(categories)
        
        if not template:
            print("Didn't find anything for template '{}'.".format(tpl_label))
            continue
        
        with conn:
            with conn.cursor() as cur:            
                cur.execute(query_template_tabs(), (tpl_label,))
                tabs = cur.fetchall()
                
        templateTabs = build_template_tabs(tabs)
        
        d = { 'template': template, 'templateTabs': templateTabs }
        
        with open(
            r'{}\admin\export\template_{}.json'.format(
                __path__[0], l[tpl_label]
                ),
            'w',
            encoding='utf-8'
            ) as dest:
            dump(d, dest, ensure_ascii=False, indent=4)

    conn.close()
    
