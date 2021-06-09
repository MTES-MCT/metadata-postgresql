-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Utilitaires pour la recherche dans les métadonnées JSON-LD intégrées
-- aux descriptions des objets
--
-- contributeurs : Leslie Lemaire (MTE-MCTRCT-Mer, service du numérique).
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- schéma contenant les objets : z_metadata
--
-- objets créés par le script :
-- - FUNCTION: z_metadata.metadata_description_to_jsonb(text)
-- - VIEW: z_metadata.metadata_catalogue
-- - FUNCTION: z_metadata.metadata_test_unit(jsonb, text[], text, int)
-- - FUNCTION: z_metadata.metadata_search_catalogue_relations(text[])
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- La vue metadata_catalogue répertorie les métadonnées saisies entre deux
-- balises <METADATA> et </METADATA> dans les descriptions/commentaires
-- des relations (tables, vues, etc.) et schémas, selon une structure
-- JSON valide.
--
-- La fonction metadata_description_to_jsonb permet de constituer la
-- vue sans générer d'erreur lorsque des balises <METADATA> contiennent
-- autre chose qu'un JSON valide.
--
-- La fonction metadata_search_catalogue_relations balaie la vue
-- metadata_catalogue, afin de lister les relations (les schémas ne sont
-- pas considérés) dont les métadonnées respectent toutes les conditions
-- listées en argument. Cf. en-tête de la fonction pour plus de détails.
-- Elle ne rendra un résultat que pour des métadonnées structurées selon
-- DCAT au format JSON-LD.
--
-- La fonction metadata_test_unit est une fonction annexe appelée par 
-- metadata_search_catalogue_relations. Elle vérifie si un bloc de
-- métadonnées respecte une condition donnée.
-- 
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-- FUNCTION: z_metadata.metadata_description_to_jsonb(text)

CREATE OR REPLACE FUNCTION z_metadata.metadata_description_to_json(description text)
    RETURNS jsonb
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Cette fonction détermine si le texte considéré contient un jsonb
           valide entre deux balises <METADATA> et </METADATA> et, si oui,
           le renvoie.
           
ARGUMENT : commentaire est le texte à analyser.

SORTIE : jsonb extrait si possible, sinon NULL. */

BEGIN

    RETURN substring(description, '^(?:.*)[<]METADATA[>](.*?)[<][/]METADATA[>]')::jsonb ;

EXCEPTION WHEN OTHERS THEN
    RETURN NULL ;
END
$_$;

COMMENT ON FUNCTION z_metadata.metadata_description_to_json(text) IS 'Cette fonction détermine si le texte considéré contient un jsonb valide entre deux balises <METADATA> et </METADATA> et, si oui, le renvoie.' ;




-- VIEW: z_metadata.metadata_catalogue

CREATE OR REPLACE VIEW z_metadata.metadata_catalogue AS (
    WITH t AS (
        SELECT
            objoid,
            classoid::regclass AS objcatalog,
            z_metadata.metadata_description_to_json(description) AS metadata
            FROM pg_description
            WHERE classoid = ANY(ARRAY['pg_class'::regclass, 'pg_namespace'::regclass])
               AND description IS NOT NULL
        )
    SELECT * FROM t WHERE metadata IS NOT NULL
    ) ;
    
COMMENT ON VIEW z_metadata.metadata_catalogue IS 'Vue des métadonnées contenues dans les descriptions des relations (tables, vues...) et schémas de la base.' ;
COMMENT ON COLUMN z_metadata.metadata_catalogue.objoid IS 'Identifiant de la relation ou du schéma.' ;
COMMENT ON COLUMN z_metadata.metadata_catalogue.objcatalog IS 'Catalogue : ''pg_class'':regclass pour une relation ou ''pg_namespace''::regclass pour un schéma.' ;
COMMENT ON COLUMN z_metadata.metadata_catalogue.metadata IS 'Métadonnées extraites de la description de la relation ou du schéma.' ;


-- FUNCTION: z_metadata.metadata_test_unit(jsonb, text[], text, int)

CREATE OR REPLACE FUNCTION z_metadata.metadata_test_unit(metadata jsonb, chemin text[], noeud text, k int DEFAULT 1)
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Fonction récursive qui, dans les métadonnées considérées, compare
           la valeur associée à une catégorie désignée par un chemin de
           propriétés avec une valeur fournie en argument, pour un opérateur
           donné.
           
Que l'opérateur de comparaison soit positif (ex : "est égal") ou négatif (ex : "ne
contient pas"), la condition n'est jamais considérée comme respectée quand la propriété
cible n'existe pas dans les métadonnées.

Pour un opérateur positif, une condition est considérée comme respectée si la propriété
visée existe dans le graphe et qu'au moins une des ses valeurs respecte la condition.

Pour un opérateur négatif, une condition est considérée comme respectée si la propriété
visée existe dans le graphe et que toutes ses valeurs respectent la condition.
           
ARGUMENTS :
- metadata est un JSON-LD (format PostgreSQL jsonb) contenant les métadonnées ;

- chemin est une liste d'identifiants de propriétés (text[]) définissant une catégorie
de métadonnées. 

L'avant dernier élément du chemin est un opérateur :
"=" (égalité), "!=" (n'est pas égal), ">=" (contient), "!>=" (ne contient pas),
"~" (respecte l'expression rationnelle), '!~' (ne respecte pas l'expression
rationnelle). Tous les opérateurs ont une variante insensible à la casse :
"=*", ">=*", etc.

le dernier élément du chemin est une chaîne de caractères correspondant à la valeur à
tester pour la catégorie et l'opérateur en question.

- noeud est l'identifiant du noeud à utiliser comme sujet lors de la prochaine
itération. Doit être initialisé avec l'identifiant du dcat:Dataset ;

- k est un entier incrémenté au fil des itérations de la fonction, correspondant
à l'indice de la composante de chemin à utiliser comme prédicat lors de la
prochaine itération. Initialisé à 1 (valeur par défaut).

SORTIE : True si la condition est vérifiée, False si la propriété existe
et ne vérifie pas la condition, NULL si elle n'existe pas.*/

DECLARE
    b boolean ;
    f boolean ;
    s jsonb ;
    n record ;
    m int ;
    
BEGIN

    m = array_length(chemin, 1) ;
        
    -- à la dernière itération, on vérifie la
    -- valeur
    IF k = m - 2
    THEN 
    
        IF chemin[k + 1] = '~'
        THEN
        
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )            
            SELECT bool_or(valeur ~ chemin[k + 2])
                INTO f
                FROM a2 ;
        
        ELSIF chemin[k + 1] = '~*'
        THEN
        
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_or(valeur ~* chemin[k + 2])
                INTO f
                FROM a2 ;
        
        ELSIF chemin[k + 1] = '!~'
        THEN
        
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_and(valeur !~ chemin[k + 2])
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '!~*'
        THEN
        
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_and(valeur !~* chemin[k + 2])
                INTO f
                FROM a2 ;
                  
        ELSIF chemin[k + 1] = '='
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_or(valeur = chemin[k + 2])
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '=*'
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_or(lower(valeur) = lower(chemin[k + 2]))
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '!='
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_and(valeur != chemin[k + 2])
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '!=*'
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_and(lower(valeur) != lower(chemin[k + 2]))
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '>='
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_or(strpos(valeur, chemin[k + 2]) > 0)
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '>=*'
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_or(strpos(lower(valeur), lower(chemin[k + 2])) > 0)
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '!>='
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_and(strpos(valeur, chemin[k + 2]) = 0)
                INTO f
                FROM a2 ;
                
        ELSIF chemin[k + 1] = '!>=*'
        THEN              
   
            WITH a1 AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            ),
            a2 AS (
                SELECT jsonb_array_elements(noeuds) ->> '@value' AS valeur
                    FROM a1
            )
            SELECT bool_and(strpos(lower(valeur), lower(chemin[k + 2])) = 0)
                INTO f
                FROM a2 ;
            
        END IF ;
    
        RETURN f ;
        -- sera NULL si la propriété n'existe pas dans le graphe

    -- si la dernière itération n'est pas encore atteinte,
    -- on boucle sur les identifiants des noeuds objets de la propriété
    ELSE
    
        FOR n IN (
            WITH a AS (
                SELECT
                    item -> chemin[k] AS noeuds
                    FROM jsonb_array_elements(metadata) AS t (item)
                    WHERE item @> format('{ "@id": %s }', to_jsonb(noeud))::jsonb
                        AND item ? chemin[k]
            )
            SELECT jsonb_array_elements(noeuds) ->> '@id' AS fils FROM a
            )
        LOOP
        
            SELECT z_metadata.metadata_test_unit(metadata, chemin, n.fils, k + 1) INTO b ;
            
            IF strpos(chemin[m - 1], '!') = 0
            THEN
                -- pour un opérateur positif,
                -- dès lors qu'une des branches respecte la condition,
                -- on ne perd pas de temps à examiner les autres
                EXIT WHEN b ;
            ELSE
                -- avec un opérateur négatif, le
                -- test s'achève (sur un échec) dès que l'une
                -- des branches ne respecte pas la condition
                EXIT WHEN NOT b ;
            END IF ;
                        
        END LOOP ;
    
    END IF ;
    
    RETURN b ;

END
$_$;

COMMENT ON FUNCTION z_metadata.metadata_test_unit(jsonb, text[], text, int) IS 'Fonction récursive qui teste si, dans les métadonnées considérées, la catégorie définie par le chemin chemin prend la valeur valeur.' ;


-- FUNCTION: z_metadata.metadata_search_catalogue_relations(text[])

CREATE OR REPLACE FUNCTION z_metadata.metadata_search_catalogue_relations(chemins text[])
    RETURNS regclass[]
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Cette fonction renvoie les identifiants des relations dont les métadonnées
           satisfont tous les critères de recherche donnés en argument.
           
Un critère est considéré comme non satisfait lorsque la propriété visée n'existe pas
dans les métadonnées.
           
ARGUMENT : chemins est une liste de chemins, où chaque chemin est lui-même
une liste d'identifiants de propriétés définissant une catégorie de métadonnées, présentée
sous la forme d'un tableau litéral.

L'avant dernier élément du chemin est un opérateur :
"=" (égalité), "!=" (n'est pas égal), ">=" (contient), "!>=" (ne contient pas),
"~" (respecte l'expression rationnelle), '!~' (ne respecte pas l'expression
rationnelle). Tous les opérateurs ont une variante insensible à la casse :
"=*", ">=*", etc. Cf. en-tête de la fonction metadata_test_unit pour plus de
détails.

le dernier élément du chemin est une chaîne de caractères correspondant à la valeur à
tester pour la catégorie et l'opérateur en question.

Par exemple, pour chercher les relations telles que le nom du
point de contact contient "pôle IG" et dont l'un des mots-clés est exactement
"données externes" :

SELECT z_metadata.metadata_search_catalogue_relations(
    ARRAY[
      '{ "http://www.w3.org/ns/dcat#contactPoint", "http://www.w3.org/2006/vcard/ns#fn", ">=*", "pôle IG" }',
      '{ "http://www.w3.org/ns/dcat#keyword", "=", "donnée externe" }'
    ]
) ;

SORTIE : liste des identifiants des relations (regclass). */

DECLARE
    r record ;
    l regclass[] = '{}'::regclass[] ;
    c text ;
    i text ;
    b boolean = FALSE ;
    
BEGIN

    <<boucle_relations>>
    FOR r IN (SELECT * FROM z_metadata.metadata_catalogue
                WHERE objcatalog = 'pg_class'::regclass)
    LOOP       
    
        -- récupération de l'identifiant du jeu de données
        SELECT
            item ->> '@id'
            INTO i
            FROM jsonb_array_elements(r.metadata) AS t (item)
            WHERE item @> '{ "@type" : ["http://www.w3.org/ns/dcat#Dataset"] }' ;
            
    
        -- boucle sur les conditions à vérifier
        FOREACH c IN ARRAY chemins
        LOOP
            
            SELECT z_metadata.metadata_test_unit(r.metadata, c::text[], i) INTO b ;
            
            CONTINUE boucle_relations WHEN NOT coalesce(b, False) ;
            -- dès qu'une condition n'est pas satisfaite, on passe
            -- au jeu suivant.
        
        END LOOP ;
        
        l = l || ARRAY[r.objoid::regclass] ;
        
    END LOOP ;

    RETURN l ;

END
$_$;

COMMENT ON FUNCTION z_metadata.metadata_search_catalogue_relations(text[]) IS 'Cette fonction renvoie les identifiants des relations dont les métadonnées répondent aux critères de recherche donnés en argument.' ;

