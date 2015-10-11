--Copy (
WITH 
   panel_data_format AS
   (SELECT ROW_NUMBER() OVER (PARTITION BY workerid ORDER BY time ASC) AS time_period, workerid, hitid, assid, time
    FROM 
        (SELECT workerid, hitid, assid, min(time) as time
         FROM actions
         WHERE study = 5 AND workerid IS NOT NULL AND hitid IS NOT NULL AND assid IS NOT NULL AND (action = 'with prisoner' OR action = 'submit')
         GROUP BY workerid, hitid, assid) unique_hits
   ),


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
    FROM conditions_extract),

  -- I feel like I am repeating the same code here, join on the panel data format table twice
  -- I should rewrite this to join on the panel data format table later on after the uNION ALL step
  -- that would adhere more closely to the principle of clean code

  prisoner_submits AS (
    SELECT DISTINCT workerid, hitid, assid, time, condition, 1 AS submit, (other::json->'letter')::text AS letter
    FROM actions
    WHERE 
      study = 5 AND action = 'submit' AND other IS NOT NULL 
  ), -- 4,467 rows, falls to 4,450 if using the DISTINCT keyword

  prisoner_views AS (
    SELECT DISTINCT workerid, hitid, assid, time, condition, 0 as submit, ''::text as letter
    FROM actions
    WHERE study = 5 
      --AND action = 'with prisoner'
      AND workerid IS NOT NULL
      AND hitid IS NOT NULL
      AND assid IS NOT NULL
      AND (
        hitid NOT IN (SELECT hitid FROM prisoner_submits GROUP BY hitid)
        AND assid NOT IN (SELECT assid FROM prisoner_submits GROUP BY assid)
        AND workerid NOT IN (SELECT workerid FROM prisoner_submits GROUP BY workerid))
  ), -- 1,175 rows; falls to 324 if we excluded explicitly hitids from 'prisoner_first_hits' temp table
      -- if we include displays and still exclude first hits and submitted HITs we get to 457 distinct observations
      -- no change in number of records if we include the 'accept' actions


   submits_abandoned_merge AS (
      SELECT workerid, hitid, assid, time, submit, letter, condition 
      FROM prisoner_submits
      UNION ALL
      SELECT workerid, hitid, assid, time, submit, letter, condition
      FROM prisoner_views

   ) -- generates 5642 rows, 601 workers submitted vs 306 did not

-- we need put together the panel data format and the associated ranking of the events in time
-- with condition details with the submit and letter data

  SELECT DISTINCT sam.workerid, pdf.time_period, sam.assid, sam.hitid, sam.submit, LEFT(sam.letter, 15), c.training_dummy, c.work_limit, c.disagreeable_dummy, c.improbability_rate
  FROM submits_abandoned_merge sam
  FULL OUTER JOIN conditions_modified c ON c.id = sam.condition
  FULL OUTER JOIN panel_data_format pdf ON pdf.assid = sam.assid AND pdf.hitid = sam.hitid AND pdf.workerid = sam.workerid
  ORDER BY sam.workerid, pdf.time_period
;
