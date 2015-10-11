--Copy (
WITH 

   uniquehits AS
   (SELECT * 
   FROM ( SELECT ROW_NUMBER() OVER (ORDER BY workerid, time) AS hit_id, workerid, hitid, assid, time FROM (
      SELECT workerid, hitid, assid, min(time) as time 
      FROM actions 
      WHERE study = 5 AND workerid IS NOT NULL AND hitid IS NOT NULL AND assid IS NOT NULL 
      GROUP BY workerid, hitid, assid) unique_hits) hitids
   ),

   panel_data_format AS
   (SELECT ROW_NUMBER() OVER (PARTITION BY workerid ORDER BY time ASC) AS time_period, workerid, hitid, assid, time
    FROM uniquehits),


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

   prisoner_first_hits AS (
      SELECT DISTINCT hitid 
      FROM actions
      WHERE study = 5 AND hitid IS NOT NULL AND workerid IS NOT NULL AND assid IS NOT NULL AND action LIKE 'display' AND other LIKE '%utiliscope/submit_first_hit%'

   ), -- 2,112 first HITs, 2,086 unique first hits (I guess there are a couple of reloads)



   prisoner_finish_actions AS (
      SELECT DISTINCT hitid
      FROM actions
      WHERE study = 5 AND hitid IS NOT NULL AND workerid IS NOT NULL AND assid IS NOT NULL AND action LIKE 'finished'
      AND hitid NOT IN (SELECT hitid FROM prisoner_first_hits)
   ), -- 6,397 distinct finished hitids, if we exclude the first HITs as defined in the table 'prisoner_first_hits' here it goes down to 4,311
      -- based on this methodology we have 4,311 finished HITs excluding the first HIT
      -- based on submits we have 4,467, where is the discrepancy coming from? Maybe people submitted a short letter or otherwise failed to pass through our filters

   prisoner_submits AS (
      SELECT DISTINCT workerid, hitid, assid, time, condition, 1 AS submit,
         (other::json->'letter')::text AS letter
      FROM actions
      WHERE 
         study = 5 
         AND action = 'submit' 
         AND workerid IS NOT NULL 
         AND hitid IS NOT NULL 
         AND assid IS NOT NULL
         AND hitid NOT IN (SELECT hitid FROM prisoner_first_hits)
   ), -- 4,467 rows, falls to 4,450 if using the DISTINCT keyword

   prisoner_views AS (
      SELECT DISTINCT workerid, hitid, assid, time, condition, 0 as submit, ''::text as letter
      FROM actions
      WHERE study = 5 
         AND ((action LIKE '%with prisoner%') OR (action LIKE 'display') OR (action LIKE 'accept'))
         AND workerid IS NOT NULL
         AND hitid IS NOT NULL
         AND assid IS NOT NULL
         AND hitid NOT IN (SELECT hitid FROM prisoner_submits GROUP BY hitid)
         AND hitid NOT IN (SELECT hitid FROM prisoner_first_hits)
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
/*
    SELECT sam.workerid, sam.hitid, sam.assid, pdf.time_period, c.work_limit, c.disagreeable_dummy,
	c.improbability_rate, c.training_dummy, c.wage, sam.submit --, LEFT(sam.letter, 10)
    FROM submits_abandoned_merge AS sam
    INNER JOIN conditions_modified c ON sam.condition = c.id
    FULL OUTER JOIN panel_data_format pdf ON sam.workerid = pdf.workerid AND sam.assid = pdf.assid AND sam.hitid = pdf.hitid
    ORDER BY sam.workerid, pdf.time_period
*/
/*
	SELECT a.action, a.hitid, a.workerid, a.assid, a.time, a.study, pdf.time_period FROM panel_data_format pdf
	INNER JOIN actions a ON a.hitid = pdf.hitid AND a.assid = pdf.assid AND a.workerid = pdf.workerid
	WHERE pdf.hitid NOT IN (SELECT hitid FROM submits_abandoned_merge)
		AND pdf.hitid NOT IN (SELECT hitid FROM prisoner_views)
		AND pdf.hitid NOT IN (SELECT hitid FROM prisoner_first_hits)
		AND pdf.time_period <> 1
*/
/*
	SELECT pdf.time_period, pfh.hitid, a.assid, a.workerid, a.action, LEFT(a.other, 40), a.time
	FROM panel_data_format pdf
	INNER JOIN prisoner_first_hits pfh ON pfh.hitid = pdf.hitid
	INNER JOIN actions a ON a.hitid = pdf.hitid
	WHERE pdf.time_period <> 1
	ORDER BY a.workerid, a.time
*/
SELECT * from uniquehits ORDER BY workerid, time
--) To '/home/econ/data/panel_data_prisoner_quality_II.csv' With CSV HEADER;
--*/
;
