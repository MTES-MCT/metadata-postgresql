-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Utilitaires pour la manipulation des identifiants dans les métadonnées
-- JSON-LD intégrées aux descriptions des objets
-- > recette
--
-- contributeurs : Leslie Lemaire (MTE-MCTRCT-Mer, service du numérique).
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- schéma contenant les objets : z_metadata_recette
--
-- objets créés par le script :
-- - SCHEMA: z_metadata_recette
-- - TABLE: z_metadata_recette.echantillons_jsonb
-- - TABLE: z_metadata_recette.echantillons_description
-- - TABLE: z_metadata_recette.exemple
-- - FUNCTION: z_metadata_recette.test_metadata_valid_uuid()
-- - FUNCTION: z_metadata_recette.test_metadata_is_jsonld()
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Le script crée les objets et échantillons nécessaires
-- à la recette des fonctions de gestion des UUID.
--
-- Pour exécuter la recette de metadata_is_jsonld (inclut
-- plusieurs tests mettant en oeuvre metadata_is_iri) :
-- SELECT z_metadata_recette.test_metadata_is_jsonld() ;
--
-- Pour exécuter la recette de metadata_valid_uuid :
-- SELECT z_metadata_recette.test_metadata_valid_uuid() ;
--
-- Ces fonctions renvoient "True" si tous les tests unitaires
-- ont réussi, une erreur sinon.
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

-- SCHEMA: z_metadata_recette

CREATE SCHEMA IF NOT EXISTS z_metadata_recette ;


-- TABLE: z_metadata_recette.echantillons_jsonb

DROP TABLE IF EXISTS z_metadata_recette.echantillons_jsonb ;
CREATE TABLE z_metadata_recette.echantillons_jsonb (
    id serial PRIMARY KEY,
    fragment jsonb,
    expected_result boolean, -- résultat attendu pour metadata_is_jsonld(fragment)
    expected_error text -- code de l'erreur attendue pour metadata_is_jsonld(fragment, False)
    ) ;
    

-- TABLE: z_metadata_recette.echantillons_description
    
DROP TABLE IF EXISTS z_metadata_recette.echantillons_description ;
CREATE TABLE z_metadata_recette.echantillons_description (
    id serial PRIMARY KEY,
    description text,
    expected_uuid uuid, -- UUID qui devrait être renvoyée par metadata_valid_uuid (ou
                        -- NULL si un nouvel identifiant doit être généré)
    expected_descr text -- nouvelle description après exécution de la fonction
                        -- avec '%s' à la place de l'UUID.
    ) ;
    
    
-- TABLE: z_metadata_recette.exemple

DROP TABLE IF EXISTS z_metadata_recette.exemple ;
CREATE TABLE z_metadata_recette.exemple (id int PRIMARY KEY) ;
-- table proxy pour la recette de metadata_valid_uuid avec les
-- valeurs de descriptions stockées dans echantillons_description


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

-- FUNCTION: z_metadata_recette.test_metadata_valid_uuid()

CREATE OR REPLACE FUNCTION z_metadata_recette.test_metadata_valid_uuid()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Test de la fonction metadata_valid_uuid sur toutes les
           descriptions stockées dans echantillons_description.

SORTIE : True en cas de succès, une erreur sinon.*/

DECLARE
    t record ;
    u uuid ;
    d text ;
    e_mssg text ;
    e_detl text ;

BEGIN

    FOR t IN (SELECT * FROM z_metadata_recette.echantillons_description)
    LOOP
    
        BEGIN
    
        EXECUTE format('COMMENT ON TABLE z_metadata_recette.exemple IS %L', t.description) ;
        
        SELECT z_metadata.metadata_valid_uuid('z_metadata_recette.exemple'::regclass) INTO u ;
        
        IF NOT FOUND
        THEN
            RAISE EXCEPTION 'Echec du test pour l''échantillon n°%.', t.id::text
                USING DETAIL = 'La fonction n''a renvoyé aucun UUID.' ;        
        END IF ;
        
        IF t.expected_uuid IS NOT NULL AND NOT u = t.expected_uuid
        THEN
            RAISE EXCEPTION 'Echec du test pour l''échantillon n°%.', t.id::text
                USING DETAIL = format('UUID attendu : "%s". UUID obtenu : "%s".', t.expected_uuid, u) ;
        END IF ;
        
        SELECT obj_description('z_metadata_recette.exemple'::regclass, 'pg_class') INTO d ;
        
        IF NOT coalesce(format(t.expected_descr, u), '') =  coalesce(d, '')
        THEN
            RAISE EXCEPTION 'Echec du test pour l''échantillon n°%.', t.id::text
                USING DETAIL = format('Description attendue :
"%s".

Description obtenue :
"%s"', coalesce(format(t.expected_descr, u), 'NULL'), coalesce(d, 'NULL')) ;

        END IF ;
        
        EXCEPTION WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                                    e_detl = PG_EXCEPTION_DETAIL ;
            RAISE EXCEPTION 'Erreur inattendue lors du test sur l''échantillon n°%.', t.id::text
                USING DETAIL = '> ' || e_mssg || coalesce(chr(10) || nullif(e_detl, ''), '') ;   
        END ;
    
    END LOOP ;
    
    RETURN True ;

END
$_$;


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-- FUNCTION: z_metadata_recette.test_metadata_is_jsonld()

CREATE OR REPLACE FUNCTION z_metadata_recette.test_metadata_is_jsonld()
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Test de la fonction metadata_is_jsonld sur toutes les
           descriptions stockées dans echantillons_jsonb.

SORTIE : True en cas de succès, une erreur sinon. */

DECLARE
    j record ;
    e text ;
    b boolean ;
    e_mssg text ;
    e_detl text ;

BEGIN

    FOR j IN (SELECT * FROM z_metadata_recette.echantillons_jsonb)
    LOOP
    
        b = NULL ;
        
        BEGIN   
            
            BEGIN
            
                PERFORM z_metadata.metadata_is_jsonld(j.fragment, False) ;
                
                IF j.expected_error IS NOT NULL
                THEN
                    b = False ;
                END IF ;
                
            EXCEPTION WHEN OTHERS THEN
                GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                                        e_detl = PG_EXCEPTION_DETAIL ;
                
                IF j.expected_error IS NULL
                THEN            
                    RAISE EXCEPTION 'Echec du test pour l''échantillon n°%. Erreur non planifiée.', j.id::text
                        USING DETAIL = '> ' || e_mssg || coalesce(chr(10) || nullif(e_detl, ''), '') ;               
                END IF ;
                
                IF NOT e_mssg ~  ('#' || j.expected_error)
                THEN
                    RAISE EXCEPTION 'Echec du test pour l''échantillon n°%.', j.id::text
                        USING DETAIL = format('Erreur attendue : "%s". Erreur obtenue : "%s".',
                                            j.expected_error::text,
                                            e_mssg::text) || coalesce(chr(10) || nullif(e_detl, ''), '') ; 
                END IF ;
                
            END ;
        
            IF NOT b
            THEN
                RAISE EXCEPTION 'Echec du test pour l''échantillon n°%. Une erreur était attendue, mais aucune n''a été générée.', j.id::text
                        USING DETAIL = format('Erreur attendue : "%s".', j.expected_error::text) ;
            END IF ;
        
        SELECT z_metadata.metadata_is_jsonld(j.fragment) INTO b ;
        
        IF NOT FOUND
        THEN
            RAISE EXCEPTION 'Echec du test pour l''échantillon n°%.', j.id::text
                USING DETAIL = 'La fonction n''a renvoyé aucun résultat.' ;        
        END IF ;
        
        
        IF NOT j.expected_result = b
        THEN
            RAISE EXCEPTION 'Echec du test pour l''échantillon n°%.', j.id::text
                USING DETAIL = format('Résultat attendu : "%s". Résultat obtenu : "%s".', j.expected_result::text, b::text) ;     
        END IF ;

        EXCEPTION WHEN OTHERS THEN
            GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                                    e_detl = PG_EXCEPTION_DETAIL ;
            RAISE EXCEPTION 'Erreur inattendue lors du test sur l''échantillon n°%.', j.id::text
                USING DETAIL = '> ' || e_mssg || coalesce(chr(10) || nullif(e_detl, ''), '') ;   
        END ;
        
    END LOOP ;
    
    RETURN True ;
    
END
$_$;


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-- Echantillons pour la recette de la fonction metadata_valid_uuid :

INSERT INTO z_metadata_recette.echantillons_description (description, expected_uuid, expected_descr) VALUES

    -- 1
    -- pas de commentaire
    ('', NULL, '

<METADATA>
[
    {
        "@id": "urn:uuid:%s",
        "@type": [
            "http://www.w3.org/ns/dcat#Dataset"
        ]
    }
]
</METADATA>
'),

    -- 2
    -- commentaire sans métadonnées
    ('Chose', NULL, 'Chose

<METADATA>
[
    {
        "@id": "urn:uuid:%s",
        "@type": [
            "http://www.w3.org/ns/dcat#Dataset"
        ]
    }
]
</METADATA>
'),

    -- 3
    -- JSON-LD valide basique + UUID valide
    ('<METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]</METADATA>',
        '7279c6ec-b133-44f1-a400-0df441f7bd6c'::uuid,
        '<METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]</METADATA>'
        ),
        
    -- 4
    -- JSON-LD valide basique + UUID invalide
    ('<METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]</METADATA>',
        NULL,
        '<METADATA>
[
    {
        "@id": "urn:uuid:%s",
        "@type": [
            "http://www.w3.org/ns/dcat#Dataset"
        ]
    }
]
</METADATA>'),

    -- 6
    -- JSON-LD invalide
    ('<METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c" } ]</METADATA>',
        NULL,
        '<METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c" } ]</METADATA>

<METADATA>
[
    {
        "@id": "urn:uuid:%s",
        "@type": [
            "http://www.w3.org/ns/dcat#Dataset"
        ]
    }
]
</METADATA>
'),

    -- 7
    -- JSON invalide
    ('<METADATA>[ "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c" } ]</METADATA>',
        NULL,
        '<METADATA>[ "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c" } ]</METADATA>

<METADATA>
[
    {
        "@id": "urn:uuid:%s",
        "@type": [
            "http://www.w3.org/ns/dcat#Dataset"
        ]
    }
]
</METADATA>
'),

    -- 8
    -- JSON-LD valide basique + UUID valide + sac de noeuds avec
    -- les balises <METADATA>
    ('<METADATA></METADATA><METADATA><METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]</METADATA>',
        '7279c6ec-b133-44f1-a400-0df441f7bd6c'::uuid,
        '<METADATA></METADATA><METADATA><METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]</METADATA>'
        ),

    -- 9
    -- JSON-LD valide basique + UUID valide + sac de noeuds avec
    -- les balises <METADATA>
    ('<METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]</METADATA><METADATA></METADATA>',
        NULL,
        '<METADATA>[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]</METADATA><METADATA></METADATA>

<METADATA>
[
    {
        "@id": "urn:uuid:%s",
        "@type": [
            "http://www.w3.org/ns/dcat#Dataset"
        ]
    }
]
</METADATA>
'),

    -- 10
    -- JSON-LD valide complexe + UUID valide
    ('Commentaire saisi par le service.

<METADATA>
[
  {
    "@id": "urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/accessRights": [
      {
        "@id": "_:Nd35a480c3efb4f7d8bc14a8938b18261"
      }
    ],
    "http://purl.org/dc/terms/description": [
      {
        "@language": "fr",
        "@value": "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l''INSEE au 1er janvier de l''année de référence."
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2021-02-04"
      }
    ]
  },
  {
    "@id": "_:Nd35a480c3efb4f7d8bc14a8938b18261",
    "@type": [
      "http://purl.org/dc/terms/RightsStatement"
    ],
    "http://www.w3.org/2000/01/rdf-schema#label": [
      {
        "@language": "fr",
        "@value": "Aucune restriction d''accès ou d''usage."
      }
    ]
  }
]
</METADATA>
',
    '479fd670-32c5-4ade-a26d-0268b0ce5046'::uuid,
    'Commentaire saisi par le service.

<METADATA>
[
  {
    "@id": "urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/accessRights": [
      {
        "@id": "_:Nd35a480c3efb4f7d8bc14a8938b18261"
      }
    ],
    "http://purl.org/dc/terms/description": [
      {
        "@language": "fr",
        "@value": "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l''INSEE au 1er janvier de l''année de référence."
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2021-02-04"
      }
    ]
  },
  {
    "@id": "_:Nd35a480c3efb4f7d8bc14a8938b18261",
    "@type": [
      "http://purl.org/dc/terms/RightsStatement"
    ],
    "http://www.w3.org/2000/01/rdf-schema#label": [
      {
        "@language": "fr",
        "@value": "Aucune restriction d''accès ou d''usage."
      }
    ]
  }
]
</METADATA>
') ;



-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-- Echantillons pour la recette de la fonction metadata_is_jsonld :

INSERT INTO z_metadata_recette.echantillons_jsonb (fragment, expected_result, expected_error) VALUES

    -- 1
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', True, NULL),
    
    -- 2
    ('{ "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c" }', False, '01'),
    
    -- 3
    ('[]', False, '02'),
    
    -- 4
    ('[ "chose" ]', False, '03'),
    
    -- 5
    ('[ { "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', False, '04'),
    
    -- 6
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] }, {} ]', False, '04'),
    
    -- 7
    ('[ { "@id": [ "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c" ], "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', False, '05'),
    
    -- 8
    ('[ { "@id": 1, "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', False, '05'),
    
    -- 9
    ('[ { "@id": "\\chose", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', False, '06'),
    
    -- 10
    ('[ { "@id": "chose et chose", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', False, '06'),
    
    -- 11
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "chose": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', False, '07'),
    
    -- 12
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": "http://www.w3.org/ns/dcat#Dataset" } ]', False, '08'),
    
    -- 13
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset", "Chose" ] } ]', False, '09'),
    
    -- 14
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ { "chose" : "n''est pas un type" } ] } ]', False, '10'),
    
    -- 15
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "<chose>" ] } ]', False, '11'),
    
    -- 16
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] },
        { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', False, '12'),
        
    -- 17
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose\\chose" : "chose" } ]', False, '13'),
    
    -- 18
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : "chose" } ]', False, '14'),
    
    -- 19
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [] } ]', False, '15'),
    
    -- 20
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ "chose" ] } ]', False, '29'),
    
    -- 21
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@id" : 1 } ] } ]', False, '16'),
    
    -- 22
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@id" : "chose{chose" } ] } ]', False, '17'),
    
    -- 23
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"],
          "chose" : [ { "@id" : "chose", "chose" : "chose" } ] } ]', False, '18'),
          
    -- 24
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"],
          "chose" : [ { "@id" : "_:chose" } ], "chose2" : [ { "@id" : "_:chose" } ] } ]', False, '19'),
          
    -- 25
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@id" : "_:chose" } ] },
        { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6d", "@type": [ "chose"], "chose" : [ { "@id" : "_:chose" } ] } ]', False, '19'),
        
    -- 26
    ('[ { "@id": "_:chose", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@id" : "_:chose" } ] } ]', False, '20'),
    
    -- 27
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "chose" : "chose" } ] } ]', False, '21'),
    
    -- 28
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@value" : 1 } ] } ]', False, '22'),
    
    -- 29
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@value" : "valeur", "chose" : "chose" } ] } ]', False, '23'),
    
    -- 30
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@value" : "valeur", "@type" : "type", "@language" : "langue" } ] } ]', False, '24'),
    
    -- 31
    ('[ { "@id": "_:chose", "@type": [ "http://www.w3.org/ns/dcat#Dataset"] } ]', False, '25'),
    
    -- 32
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"], "chose" : [ { "@id" : "_:chose"} ] } ]', False, '26'),
    
    -- 33
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "chose"] } ]', False, '27'),
    
    -- 34
    ('[ { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6c", "@type": [ "http://www.w3.org/ns/dcat#Dataset"] },
        { "@id": "urn:uuid:7279c6ec-b133-44f1-a400-0df441f7bd6d", "@type": [ "http://www.w3.org/ns/dcat#Dataset"] } ]', False, '28'),
    
    -- 35
    ('[
  {
    "@id": "urn:uuid:479fd670-32c5-4ade-a26d-0268b0ce5046",
    "@type": [
      "http://www.w3.org/ns/dcat#Dataset"
    ],
    "http://purl.org/dc/terms/accessRights": [
      {
        "@id": "_:Nd35a480c3efb4f7d8bc14a8938b18261"
      }
    ],
    "http://purl.org/dc/terms/description": [
      {
        "@language": "fr",
        "@value": "Délimitation simplifiée des départements de France métropolitaine pour représentation à petite échelle, conforme au code officiel géographique (COG) de l''INSEE au 1er janvier de l''année de référence."
      }
    ],
    "http://purl.org/dc/terms/modified": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
        "@value": "2021-02-04"
      }
    ],
    "http://purl.org/dc/terms/provenance": [
      {
        "@id": "_:Nca4314839d3b4a9bba6cbc67aa607994"
      }
    ],
    "http://purl.org/dc/terms/publisher": [
      {
        "@id": "_:N5f0a1b687d2b4e0eb425412ce86f8f9b"
      }
    ],
    "http://purl.org/dc/terms/temporal": [
      {
        "@id": "_:N678a2e51c6864720ab1343279e74e1db"
      }
    ],
    "http://purl.org/dc/terms/title": [
      {
        "@language": "fr",
        "@value": "ADMIN EXPRESS - Départements de métropole"
      }
    ],
    "http://www.w3.org/ns/dcat#contactPoint": [
      {
        "@id": "_:Neae3737569764e39a497eb7691ff84d8"
      }
    ],
    "http://www.w3.org/ns/dcat#distribution": [
      {
        "@id": "_:N6160bfa39b134e369ceafd9e105c3c6c"
      }
    ],
    "http://www.w3.org/ns/dcat#keyword": [
      {
        "@language": "fr",
        "@value": "ign"
      },
      {
        "@language": "fr",
        "@value": "donnée externe"
      },
      {
        "@language": "fr",
        "@value": "admin express"
      }
    ],
    "http://www.w3.org/ns/dcat#landingPage": [
      {
        "@id": "https://geoservices.ign.fr/ressources_documentaires/Espace_documentaire/BASES_VECTORIELLES/ADMIN_EXPRESS/IGNF_ADMIN_EXPRESS_2-4.html"
      }
    ],
    "http://www.w3.org/ns/dcat#theme": [
      {
        "@id": "http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO"
      },
      {
        "@id": "http://publications.europa.eu/resource/authority/data-theme/REGI"
      }
    ],
    "urn:uuid:218c1245-6ba7-4163-841e-476e0d5582af": [
      {
        "@language": "fr",
        "@value": "À mettre à jour !"
      }
    ]
  },
  {
    "@id": "_:Nca4314839d3b4a9bba6cbc67aa607994",
    "@type": [
      "http://purl.org/dc/terms/ProvenanceStatement"
    ],
    "http://www.w3.org/2000/01/rdf-schema#label": [
      {
        "@language": "fr",
        "@value": "Donnée référentielle produite par l''IGN."
      }
    ]
  },
  {
    "@id": "_:Neae3737569764e39a497eb7691ff84d8",
    "@type": [
      "http://www.w3.org/2006/vcard/ns#Organization"
    ],
    "http://www.w3.org/2006/vcard/ns#fn": [
      {
        "@language": "fr",
        "@value": "Pôle IG"
      }
    ],
    "http://www.w3.org/2006/vcard/ns#hasEmail": [
      {
        "@id": "mailto:pig.servicex@developpement-durable.gouv.fr"
      }
    ]
  },
  {
    "@id": "_:Nd35a480c3efb4f7d8bc14a8938b18261",
    "@type": [
      "http://purl.org/dc/terms/RightsStatement"
    ],
    "http://www.w3.org/2000/01/rdf-schema#label": [
      {
        "@language": "fr",
        "@value": "Aucune restriction d''accès ou d''usage."
      }
    ]
  },
  {
    "@id": "_:N5f0a1b687d2b4e0eb425412ce86f8f9b",
    "@type": [
      "http://xmlns.com/foaf/0.1/Organization"
    ],
    "http://xmlns.com/foaf/0.1/name": [
      {
        "@language": "fr",
        "@value": "Institut national de l''information géographique et forestière (IGN-F)"
      }
    ]
  },
  {
    "@id": "_:N6160bfa39b134e369ceafd9e105c3c6c",
    "@type": [
      "http://www.w3.org/ns/dcat#Distribution"
    ],
    "http://purl.org/dc/terms/accessURL": [
      {
        "@id": "https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#admin-express"
      }
    ],
    "http://purl.org/dc/terms/issued": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2021-01-19"
      }
    ],
    "http://purl.org/dc/terms/licence": [
      {
        "@id": "_:N2c42eee2f6dd4651861a20feecdcf02d"
      }
    ]
  },
  {
    "@id": "_:N2c42eee2f6dd4651861a20feecdcf02d",
    "@type": [
      "http://purl.org/dc/terms/LicenseDocument"
    ],
    "http://www.w3.org/2000/01/rdf-schema#label": [
      {
        "@language": "fr",
        "@value": "Base de données soumise aux conditions de la licence ouverte Etalab."
      }
    ]
  },
  {
    "@id": "_:N678a2e51c6864720ab1343279e74e1db",
    "@type": [
      "http://purl.org/dc/terms/PeriodOfTime"
    ],
    "http://www.w3.org/ns/dcat#endDate": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2021-01-15"
      }
    ],
    "http://www.w3.org/ns/dcat#startDate": [
      {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2021-01-15"
      }
    ]
  }
]', True, NULL) ;

