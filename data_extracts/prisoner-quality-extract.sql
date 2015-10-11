Copy (

   WITH 

   conditions_extract AS (
   SELECT id, 
      json::json->'disagreeable' AS disagreeable,
      json::json->'improbability_rate' AS improbability_rate,
      json::json->'price' AS wage, 
      json::json->'training'::text AS training,
      json::json->'work_limit' AS work_limit 
   FROM conditions
   WHERE id IN (SELECT condition FROM actions WHERE study = 5)
   ), 


   conditions_modified AS 
   (SELECT id, 
      work_limit::text::integer, 
      CASE disagreeable::text
         WHEN 'true' THEN 1
         WHEN 'false' THEN 0
      END AS disagreeable_dummy,
      improbability_rate::text::integer, 
      CASE training::text
         WHEN 'true' THEN 1
         WHEN 'false' THEN 0
      END AS training_dummy, 
      wage::text::float
    FROM conditions_extract),  -- this take the previous 



   letters AS
   (SELECT workerid, hitid, assid, (other::json->'letter')::text AS letter
    FROM actions
    WHERE study = 5 AND hitid IS NOT NULL AND assid IS NOT NULL AND action = 'submit')


   SELECT DISTINCT ON(a.workerid, a.assid, a.hitid) 
         a.workerid, 
         a.assid, 
         a.hitid,
      	a.time, 
         c.work_limit AS work_limit, 
         c.disagreeable_dummy AS disagreeable, 
         c.improbability_rate AS improbability_rate, 
         c.training_dummy AS training, 
         c.wage AS wage,
         letters.letter
   FROM actions a
   INNER JOIN conditions_modified c ON a.condition = c.id
   INNER JOIN letters ON letters.workerid = a.workerid AND letters.hitid = a.hitid AND letters.assid = a.assid
   WHERE a.action = 'submit' AND a.study = 5 AND a.hitid IS NOT NULL AND a.assid IS NOT NULL

