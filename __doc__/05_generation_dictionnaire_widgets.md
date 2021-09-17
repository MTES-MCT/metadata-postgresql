# Génération du dictionnaire des widgets

## Paramètres utilisateur

## Sources de données

### metagraph : le graphe des métadonnées pré-existantes

Les métadonnées pré-existantes sont déduites de la description PostgreSQL de la table ou de la vue, ci-après `old_description`.

Cette information est a priori déjà disponible par l'intermédiaire des classes de QGIS. Néanmoins, si nécessaire, [pg_queries.py](/metadata_postgresql/bibli_pg/pg_queries.py) propose une requête pré-configurée `query_get_table_comment()`, qui peut être utilisée comme suit :

```python

import psycopg2
conn = psycopg2.connect(connection_string)

with conn:
    with conn.cursor() as cur:
    
        query = pg_queries.query_get_table_comment(schema_name, table_name)
        cur.execute(query)
        old_description = cur.fetchone()[0]

conn.close()

```

*NB : `connection_string` la chaîne de connexion à la base de données PostgreSQL.*

### shape : le schéma SHACL des métadonnées communes

### vocabulary : la compilation des thésaurus

### template : le modèle de formulaire
