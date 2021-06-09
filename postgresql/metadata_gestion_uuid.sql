-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- Utilitaires pour la manipulation des identifiants dans les métadonnées
-- JSON-LD intégrées aux descriptions des objets
--
-- contributeurs : Leslie Lemaire (MTE-MCTRCT-Mer, service du numérique).
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- schéma contenant les objets : z_metadata
--
-- objets créés par le script :
-- - FUNCTION: z_metadata.metadata_valid_uuid(regclass, int)
-- - FUNCTION: z_metadata.metadata_is_jsonld(jsonb, boolean)
-- - FUNCTION: z_metadata.metadata_is_iri(text)
--
-- dépendances : pgcrypto
--
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--
-- La fonction metadata_valid_uuid vérifie si un UUID valide est
-- présente dans les métadonnées de la relation considérée et,
-- sinon, le crée.
--
-- La fonction metadata_is_jsonld vérifie si le JSON fourni
-- en argument est conforme aux spécifications basiques du JSON-LD et
-- contient bien un objet de type dcat:Dataset.
--
-- La fonction metadata_is_iri détermine si l'argument respecte
-- les contraintes minimales de validité pour un IRI.
-- 
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-- FUNCTION: z_metadata.metadata_valid_uuid(regclass, int)

CREATE OR REPLACE FUNCTION z_metadata.metadata_valid_uuid(relation regclass, k int DEFAULT 0)
    RETURNS uuid
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Cette fonction détermine si la description saisie pour la relation
           considérée contient un UUID valide et, sinon, en implémente un.
           
Lorsque la fonction corrige l'identifiant, elle s'appelle elle-même pour valider
le résultat.
           
ARGUMENT :
- relation est le nom de la relation à analyser, casté en regclass ;
- k est un entier, utilisé pour les appels récursifs de la fonction afin
d'éviter les boucles infinies.

SORTIE : L'UUID de la relation. */

DECLARE
    d text ;
    m jsonb ;
    o jsonb = '[]'::jsonb ;
    b boolean ;
    u uuid ;
    r record ;
    i text ;
    
BEGIN

    -- lorsque la fonction n'a pas réussi à produire un UUID valide
    -- après deux essais, on renvoie une erreur
    IF k >= 2
    THEN
        RAISE EXCEPTION 'L''implémentation d''un UUID dans la description de la relation % a échoué.', relation::text ;
    END IF ;

    -- récupération de la description de la relation
    d = coalesce(obj_description(relation, 'pg_class'), '') ;
    
    -- extraction du texte contenu entre les balises <METADATA>,
    -- si elles existent et tentative de conversion en JSON
    BEGIN   
        m = substring(d, '^(?:.*)[<]METADATA[>](.*?)[<][/]METADATA[>]')::jsonb ;    
    EXCEPTION WHEN OTHERS THEN
    END ;
    
    IF m IS NOT NULL
    -- m n'est pas vide : on dispose d'un JSON valide
    THEN
    
        IF z_metadata.metadata_is_jsonld(m)
        -- cas d'un JSON-LD valide
        THEN
    
            -- récupération de l'identifiant du jeu de données (qui doit
            -- exister, sinon le JSON-LD n'aurait pas pu être valide)
            SELECT
                item ->> '@id'
                INTO STRICT i
                FROM jsonb_array_elements(m) AS t (item)
                WHERE item @> '{ "@type" : ["http://www.w3.org/ns/dcat#Dataset"] }' ;
             
            BEGIN
            
                u = replace(i, 'urn:uuid:', '')::uuid ;
                -- si cette commande ne génère pas d'erreur, on considère l'UUID comme
                -- valide et on le renvoie. C'est le seul cas de succès de toute
                -- cette fonction.
                RETURN u ;
            
            EXCEPTION WHEN OTHERS THEN
            
                ------ SIMPLE REMPLACEMENT DE L'UUID ------
            
                -- génération d'un UUID
                u = gen_random_uuid() ;
                
                -- boucle sur les composants de premier niveau du JSON-LD
                FOR r IN (
                    SELECT 
                        item
                        FROM jsonb_array_elements(m) AS t (item)
                    )
                LOOP
                    
                    IF (r.item -> '@type') = '[ "http://www.w3.org/ns/dcat#Dataset" ]'::jsonb
                    THEN
                        -- pour le fragment de JSON-LD correspondant au dcat:Dataset,
                        -- on reconstruit le JSON-LD en corrigeant l'identifiant
                        o = o || jsonb_build_array(
                            jsonb_set(r.item, '{@id}', to_jsonb('urn:uuid:' || u::text))
                            ) ;                            
                    ELSE
                        -- les autres fragments sont réintégrés tels quels
                        o = o || jsonb_build_array(r.item) ;
                    END IF ;
                                      
                END LOOP ;
                
                -- mise à jour de la description de la relation avec le JSON-LD
                -- contenant le nouvel identifiant
                EXECUTE format(
                    'COMMENT ON TABLE %s IS %L',
                    relation::text,
                    regexp_replace(
                        d,
                        '^(.*)[<]METADATA[>](.*?)[<][/]METADATA[>]',
                        '\1<METADATA>' || chr(10) || jsonb_pretty(o) || chr(10) || '</METADATA>'
                        )
                    ) ;
                
                -- on relance la fonction pour valider le fait que tout est
                -- maintenant en ordre
                RETURN z_metadata.metadata_valid_uuid(relation, k + 1) ;
            
            END ;                
        
        ELSE        
        -- cas où le JSON n'est pas un JSON-LD valide
            
            BEGIN      
                -- on tente quand même de récupérer l'identifiant du jeu de données
                -- dans le JSON
                SELECT
                    item ->> '@id'
                    INTO i
                    FROM jsonb_array_elements(m) AS t (item)
                    WHERE item @> '{ "@type" : ["http://www.w3.org/ns/dcat#Dataset"] }' ;
            
                -- ... et de le caster en uuid
                u = replace(i, 'urn:uuid:', '')::uuid ;  
                
            EXCEPTION WHEN OTHERS THEN
            END ;
            
        END IF ;    
    END IF ;
            
    
    ------ CREATION D'UN NOUVEAU JSON-LD ------
    
    -- dans tous les cas où on ne disposait pas d'un JSON-LD valide
    IF u IS NULL
    THEN            
        -- si on n'a pas pu récuper d'UUID, on en génère un nouveau
        u = gen_random_uuid() ;           
    END IF ;
    
    -- création d'un JSON-LD sommaire ne contenant que l'identifiant
    o = format('[ { "@id": "urn:uuid:%s", "@type": [ "http://www.w3.org/ns/dcat#Dataset" ] } ]', u::text)::jsonb ;
    
    -- on ajoute le JSON-LD à la fin de la
    -- description, et ce même si les balises <METADATA>
    -- étaient présentes, afin de préserver leur contenu.
    EXECUTE format(
        'COMMENT ON TABLE %s IS %L',
        relation::text,
        d || chr(10) || chr(10) || '<METADATA>' || chr(10) || jsonb_pretty(o)
            || chr(10) || '</METADATA>' || chr(10)
        ) ;
    
    -- on relance la fonction pour valider
    -- le fait que tout est maintenant en ordre
    RETURN z_metadata.metadata_valid_uuid(relation, k + 1) ;
           
END
$_$;

COMMENT ON FUNCTION z_metadata.metadata_valid_uuid(regclass, int) IS 'Cette fonction détermine si la description saisie pour la relation considérée contient un UUID valide et, sinon, en implémente un.' ;


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-- FUNCTION: z_metadata.metadata_is_jsonld(jsonb, boolean)

CREATE OR REPLACE FUNCTION z_metadata.metadata_is_jsonld(fragment jsonb, sans_echec boolean DEFAULT True)
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Cette fonction vérifie si le JSON fourni en argument est conforme
           aux spécifications basiques du JSON-LD et contient bien un objet de
           type dcat:Dataset.
           
Elle pourrait produire de faux négatifs sur des JSON-LD à la structure plus
complexe que ceux qui sont produits par le système de gestion des métadonnées.
                     
ARGUMENT :
- fragment est un JSON casté en jsonb.
- sans_echec est un booléen. Si sans_echec vaut True (valeur par défaut),
la fonction renvoie False lorsque le fragment n'est pas un JSON-LD conforme.
Sinon, elle renvoie une erreur en cas de non conformité.

SORTIE : Booléen. True si le fragment est conforme, False sinon. */

DECLARE
    d int = 0 ;
    n int ;
    l text[] = ARRAY[]::text[] ;
    l1 text[] = ARRAY[]::text[] ;
    l2 text[] = ARRAY[]::text[] ;
    b text ;
    s record ;
    p record ;
    o record ;
    e_mssg text ;
    e_detl text ;
    e_hint text ;
    
BEGIN

    -- test : le fragment est-il un tableau json ?
    IF NOT coalesce(jsonb_typeof(fragment) = 'array', False)
    THEN
        RAISE EXCEPTION '[Non conformité #01] Le fragment n''est pas de type JSON array.' ;
    END IF ;
    
    -- test : le tableau contient-il au moins un objet ?
    IF NOT coalesce(jsonb_array_length(fragment) >= 1, False)
    THEN
        RAISE EXCEPTION '[Non conformité #02] Le fragment ne contient aucun objet.' ;
    END IF ;


    ------ BOUCLE SUR OBJETS CONTENUS DANS LE FRAGMENT ------
    -- soit sur les sujets des triples
    
    FOR s IN ( SELECT item FROM jsonb_array_elements(fragment) AS t (item) )
    LOOP
    
        -- test : l'objet est-il de type objet json ?
        IF NOT coalesce(jsonb_typeof(s.item) = 'object', False)
        THEN
            RAISE EXCEPTION '[Non conformité #03] L''objet n''est pas de type JSON object.'
                USING DETAIL = jsonb_pretty(s.item) ;
        END IF ;
                
        -- test : le sujet a-t-il un identifiant ?
        IF NOT s.item ? '@id'
        THEN
            RAISE EXCEPTION '[Non conformité #04] L''objet n''a pas de clé "@id".'
                USING DETAIL = jsonb_pretty(s.item) ;
        END IF ;
        
        -- test : l'identifiant est-il un string json ?
        IF NOT coalesce(jsonb_typeof(s.item -> '@id') = 'string', False)
        THEN
            RAISE EXCEPTION '[Non conformité #05] La valeur de la clé "@id" n''est pas de type JSON string.'
                USING DETAIL = jsonb_pretty(s.item) ;
        END IF ;
        
        -- test : l'identifiant est-il un IRI valide ?
        IF NOT z_metadata.metadata_is_iri(s.item ->> '@id')
        THEN
            RAISE EXCEPTION '[Non conformité #06] La valeur de la clé "@id" n''est pas un IRI valide.'
                USING DETAIL = jsonb_pretty(s.item),
                    HINT = 'Caractères interdits : ''<'', ''>'', '' '', ''"'', ''{'', ''}'', ''|'', ''\'', ''^'', ''`''.' ;
        END IF ;
        
        -- test : le sujet a-t-il un type ?
        IF NOT s.item ? '@type'
        THEN
            RAISE EXCEPTION '[Non conformité #07] L''objet n''a pas de clé "@type".'
                USING DETAIL = jsonb_pretty(s.item) ;
        END IF ;
        
        -- test : le type est-il un tableau json ?
        IF NOT coalesce(jsonb_typeof(s.item -> '@type') = 'array', False)
        THEN
            RAISE EXCEPTION '[Non conformité #08] La valeur de la clé "@type" n''est pas de type JSON array.'
                USING DETAIL = jsonb_pretty(s.item) ;
        END IF ;
        
        -- test : le type est-il un tableau json de longueur 1 ?
        IF NOT coalesce(jsonb_array_length(s.item -> '@type') = 1, False)
        THEN
            RAISE EXCEPTION '[Non conformité #09] La valeur de la clé "@type" n''est pas un JSON array de longueur 1.'
                USING DETAIL = jsonb_pretty(s.item) ;
        END IF ;
        
        -- test : la valeur du type est-elle un string json ?
        IF NOT coalesce(jsonb_typeof(s.item -> '@type' -> 0) = 'string', False)
        THEN
            RAISE EXCEPTION '[Non conformité #10] La valeur de la clé "@type" n''est pas un JSON array contenant un JSON string.'
                USING DETAIL = jsonb_pretty(s.item) ;
        END IF ;
        
        -- test : la valeur du type est-il un IRI valide ?
        IF NOT z_metadata.metadata_is_iri(s.item -> '@type' ->> 0)
        THEN
            RAISE EXCEPTION '[Non conformité #11] La valeur de la clé "@type" n''est pas un JSON array contenant un IRI valide.'
                USING DETAIL = jsonb_pretty(s.item),
                    HINT = 'Caractères interdits : ''<'', ''>'', '' '', ''"'', ''{'', ''}'', ''|'', ''\'', ''^'', ''`''.' ;
        END IF ;
        
        -- test : l'identifiant est-il utilisé plusieurs fois ?
        IF (s.item ->> '@id') = ANY(l)
        THEN
            RAISE EXCEPTION '[Non conformité #12] L''identifiant @id : "%" est utilisé par plusieurs objets.', (s.item ->> '@id') ;
        ELSE
            -- liste des identifiants d'objets
            l = array_append(l, s.item ->> '@id') ;        
        END IF ;
        
        -- liste des identifiants des noeuds vides (définitions)
        IF (s.item ->> '@id')  ~ '^_[:].'
        THEN        
            l1 = array_append(l1, s.item ->> '@id') ;
        END IF ;              
        
        -- présence, parmi l'ensemble, d'un objet de type dcat:Dataset et un seul ?
        d = d + coalesce(((s.item -> '@type') = '[ "http://www.w3.org/ns/dcat#Dataset" ]'::jsonb)::int, 0) ;
        
        
        ------ BOUCLE SUR LES CLES ------
        -- (hors @id et @type)
        -- soit sur les prédicats des triples
        
        FOR p IN ( WITH a AS ( SELECT key, value FROM jsonb_each(s.item) )
                SELECT * FROM a WHERE NOT key = ANY(ARRAY['@id', '@type']) )
        LOOP
   
            -- test : le prédicat est-il un IRI valide ?
            IF NOT z_metadata.metadata_is_iri(p.key)
            THEN
                RAISE EXCEPTION '[Non conformité #13] La clé "%" n''est pas un IRI valide.', p.key
                    USING HINT = 'Caractères interdits : ''<'', ''>'', '' '', ''"'', ''{'', ''}'', ''|'', ''\'', ''^'', ''`''.' ;
            END IF ;
            
            -- test : la valeur est-elle un tableau json ?
            IF NOT coalesce(jsonb_typeof(p.value) = 'array', False)
            THEN
                RAISE EXCEPTION '[Non conformité #14] La valeur de la clé "%" n''est pas de type JSON array.', p.key
                    USING DETAIL = jsonb_pretty(s.item) ;
            END IF ;
            
            -- test : le tableau contient-il au moins un objet ?
            IF NOT coalesce(jsonb_array_length(p.value) >= 1, False)
            THEN
                RAISE EXCEPTION '[Non conformité #15] La valeur de la clé "%" est un JSON array vide.', p.key
                    USING DETAIL = jsonb_pretty(s.item) ;
            END IF ;
            
            
            ------ BOUCLE SUR LES VALEURS ------
            -- soit sur les objets des triples
            
            FOR o IN ( SELECT item FROM jsonb_array_elements(p.value) AS t (item) )
            LOOP
            
                -- test : l'objet est-il un objet JSON ?
                IF NOT coalesce(jsonb_typeof(o.item) = 'object', False)
                THEN
                    RAISE EXCEPTION '[Non conformité #29] Une valeur de la clé "%" n''est pas de type JSON object.', p.key
                        USING DETAIL = jsonb_pretty(s.item) ;
                END IF ;
                
                -- cas d'un IRI
                IF o.item ? '@id'
                THEN
                    
                    -- test : l'identifiant est-il un string json ?
                    IF NOT coalesce(jsonb_typeof(o.item -> '@id') = 'string', False)
                    THEN
                        RAISE EXCEPTION '[Non conformité #16] Une valeur de la clé "%" est un IRI dont la clé "@id" prend une valeur qui n''est pas de type JSON string.', p.key
                            USING DETAIL = jsonb_pretty(s.item) ;
                    END IF ;
                    
                    -- test : l'identifiant est-il un IRI valide ?
                    IF NOT z_metadata.metadata_is_iri(o.item ->> '@id')
                    THEN
                        RAISE EXCEPTION '[Non conformité #17] Une valeur de la clé "%" est un IRI dont la clé "@id" prend une valeur invalide.', p.key
                            USING DETAIL = jsonb_pretty(s.item),
                                HINT = 'Caractères interdits : ''<'', ''>'', '' '', ''"'', ''{'', ''}'', ''|'', ''\'', ''^'', ''`''.' ;
                    END IF ;
                    
                    -- test : l'objet a-t-il d'autres propriétés que @id ?
                    WITH a AS ( SELECT key, value FROM jsonb_each(o.item) )
                    SELECT count(*) INTO n FROM a WHERE NOT key = '@id' ;
                        
                    IF n > 0
                    THEN
                        RAISE EXCEPTION '[Non conformité #18] Une valeur de la clé "%" est un IRI avec d''autres clés associées que "@id".', p.key
                            USING DETAIL = jsonb_pretty(s.item) ;
                    END IF ;
                    
                    -- cas particulier d'un noeud vide
                    IF (o.item ->> '@id')  ~ '^_[:].'
                    THEN
                    
                        -- test : le noeud vide a-t-il déjà été référencé ?
                        IF (o.item ->> '@id') = ANY(l2)
                        THEN
                            RAISE EXCEPTION '[Non conformité #19] Le noeud vide "%" est référencé plusieurs fois.', (s.item ->> '@id') ;
                        END IF ;

                        -- test : le noeud vide est-il auto-référencé ?
                        IF (o.item ->> '@id') = (s.item ->> '@id')
                        THEN
                            RAISE EXCEPTION '[Non conformité #20] Le noeud vide "%" est auto-référencé.', (o.item ->> '@id') ;
                        END IF ;
                        
                        -- liste des identifiants des noeuds vides (références)
                        l2 = array_append(l2, o.item ->> '@id') ;
                        
                    END IF ;     
                
                -- cas d'une valeur littérale
                ELSE
                
                    -- test : la valeur est-elle identifiée comme valeur ?
                    IF NOT o.item ? '@value'
                    THEN
                        RAISE EXCEPTION '[Non conformité #21] Une valeur littérale de la clé "%" n''a pas de clé "@value".', p.key
                            USING DETAIL = jsonb_pretty(s.item) ;
                    END IF ;
                    
                    -- test : la valeur est-elle un string json ?
                    IF NOT coalesce(jsonb_typeof(o.item -> '@value') = 'string', False)
                    THEN
                        RAISE EXCEPTION '[Non conformité #22] Une valeur littérale de la clé "%" a une "@value" qui n''est pas de type JSON string.', p.key
                            USING DETAIL = jsonb_pretty(s.item) ;
                    END IF ;
                
                    -- test : la valeur a-t-elle d'autres propriétés que @value,
                    -- @language et @type ?
                    WITH a AS ( SELECT key, value FROM jsonb_each(o.item) )
                    SELECT count(*) INTO n FROM a WHERE NOT key = ANY(ARRAY[ '@value', '@language', '@type']) ;
                        
                    IF n > 0
                    THEN
                        RAISE EXCEPTION '[Non conformité #23] Une valeur littérale de la clé "%" a d''autres clés associées que "@value", "@language" et "@type".', p.key
                            USING DETAIL = jsonb_pretty(s.item) ;
                    END IF ;
                    
                    -- test : la valeur a-t-elle à la fois une langue et un type ?                        
                    IF o.item ?& ARRAY['@type', '@language']
                    THEN
                        RAISE EXCEPTION '[Non conformité #24] Une valeur littérale de la clé "%" a à la fois une clé "@language" et une clé "@type".', p.key
                            USING DETAIL = jsonb_pretty(s.item) ;
                    END IF ;

                END IF ;
                
            END LOOP ;
           
        END LOOP ;
           
    END LOOP ;
    
    -- on vérifie que les noeuds vides définis correspondent
    -- exactement aux noeuds vides référencés
    IF NOT (l1 @> l2 AND l2 @> l1)
    THEN
    
        FOREACH b IN ARRAY l1
        LOOP
            -- test : le noeud vide défini (c'est l'un des objets du fragment) est-il
            -- référencé (utilisé comme valeur d'une clé) ?
            IF NOT b = ANY(l2)
            THEN
                RAISE EXCEPTION '[Non conformité #25] Le noeud vide "%" est défini mais non référencé.', b ;
            END IF ;
        END LOOP ;
        
        FOREACH b IN ARRAY l2
        LOOP
            IF NOT b = ANY(l1)
            THEN
                -- test : le noeud vide référencé (c'est la valeur d'une clé) est-il
                -- défini ?
                RAISE EXCEPTION '[Non conformité #26] Le noeud vide "%" est référencé mais non défini.', b ;
            END IF ;
        END LOOP ;
        
    END IF ;
    
    -- test : l'un des objets du fragment est-il un dcat:Dataset ?
    IF d = 0
    THEN
        RAISE EXCEPTION '[Non conformité #27] Le fragment ne contient aucun objet de type dcat:Dataset.' ;
    END IF ;
    
    -- test : le fragment contient-il plus d'un objet de type dcat:Dataset ?
    IF d > 1
    THEN
        RAISE EXCEPTION '[Non conformité #28] Le fragment contient plus d''un objet de type dcat:Dataset.' ;
    END IF ;

    RETURN True ;
    
EXCEPTION WHEN OTHERS THEN
    IF sans_echec
    THEN
        RETURN False ;
    ELSE
        GET STACKED DIAGNOSTICS e_mssg = MESSAGE_TEXT,
                                e_detl = PG_EXCEPTION_DETAIL,
                                e_hint = PG_EXCEPTION_HINT ;
        RAISE EXCEPTION '%', e_mssg
            USING DETAIL = e_detl,
                HINT = e_hint ;
    END IF ;
END
$_$;

COMMENT ON FUNCTION z_metadata.metadata_is_jsonld(jsonb, boolean) IS 'Cette fonction vérifie si le JSON fourni en argument est conforme aux spécifications basiques du JSON-LD et contient bien un objet de type dcat:Dataset.' ;

/* NB : pour l'heure, metadata_is_jsonld ne vérifie pas l'absence de boucle,
si ce n'est pour le cas d'un triple dont le sujet et l'objet seraient
le même identifiant de noeud vide. */


-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


-- FUNCTION: z_metadata.metadata_is_iri(text)

CREATE OR REPLACE FUNCTION z_metadata.metadata_is_iri(valeur text)
    RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
/* OBJET : Cette fonction détermine si l'argument respecte les contraintes
           minimales de validité pour un IRI.
                     
ARGUMENT : une chaîne de caractères.

SORTIE : Booléen. True si l'argument est conforme, False sinon. */

DECLARE
    -- liste des caractères interdits
    l text[] = ARRAY['<', '>', ' ', '"', '{', '}', '|', '\', '^', '`'] ;
    c text ;
    
BEGIN

    IF valeur = ''
    THEN    
        RETURN False ;
    END IF ;

    FOREACH c IN ARRAY(l)
    LOOP
    
        IF strpos(valeur, c) > 0
        THEN
            RETURN False ; 
        END IF ;
    
    END LOOP ;
    
    RETURN True ;

END
$_$;

COMMENT ON FUNCTION z_metadata.metadata_is_iri(text) IS 'Cette fonction détermine si l''argument respecte les contraintes minimales de validité pour un IRI.' ;


