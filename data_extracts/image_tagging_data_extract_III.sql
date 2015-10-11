Copy (WITH conditions_extract AS (
   SELECT id, 
      json::json->'availability' AS availability,
      json::json->'disagreeable' AS disagreeable,
      json::json->'improbability_rate' AS improbability_rate,
      json::json->'price' AS wage, 
      json::json->'training'::text AS training,
      json::json->'work_limit' AS work_limit FROM conditions
      WHERE id IN 
      (SELECT condition FROM actions WHERE study = 9)
   ),           -- condition details are in the conditions table, we need to join it on the actions table
   conditions_modified AS 
   (SELECT id, 
      availability::text, 
      disagreeable::text::integer, 
      improbability_rate::text::integer, 
      CASE training::text
         WHEN 'true' THEN 1
         WHEN 'false' THEN 0
      END AS training_dummy, 
      wage::text::float, training, work_limit FROM conditions_extract),  -- this take the previous 
   conditions_nonsubmit AS
   (SELECT a2.workerid, a2.hitid, a2.assid, a2.condition, a2.phase
    FROM actions a1 INNER JOIN actions a2
    ON a1.workerid = a2.workerid AND
       a1.hitid = a2.hitid AND
       a1.assid = a2.assid
    WHERE a1.action = 'js log on user leaving' AND 
          a1.hitid IS NOT NULL AND
          a1.assid IS NOT NULL AND
          a2.action <> 'js log on user leaving' AND
          a2.action <> 'finished'
    GROUP BY a2.workerid, a2.hitid, a2.assid, a2.condition, a2.phase
   ),
   pictures AS
   (SELECT workerid, hitid, assid, 
      (other::json->0)::text AS pic1, 
      (other::json->1)::text AS pic2,
      (other::json->2)::text AS pic3,
      (other::json->3)::text AS pic4,
      (other::json->4)::text AS pic5 FROM actions
    WHERE study = 9 AND hitid IS NOT NULL AND assid IS NOT NULL AND action = 'with pic'),
   waits AS (
      SELECT (other::json->'for')::text::integer AS wait_time, workerid, hitid, assid
      FROM actions WHERE study = 9 AND action = 'wait'),
   -- we do not need survey responses
   -- survey_responses AS (SELECT workerid, age, sex, state, income, educ, employment, location, compensation, why, 1 as submitted FROM survey_results), 
   -- survey_invites AS (
   --		  SELECT workerid, compensation, time_allotted 
	--	  FROM survey_invitations si 
		  WHERE created_at = (SELECT max(created_at) FROM survey_invitations WHERE si.workerid = survey_invitations.workerid)
		  ),
--Select ID,Name, Price,Date
--From  temp t1
--where date = (select max(date) from temp where t1.name =temp.name)
--order by date desc
   -- first_times AS (SELECT time, hitid, assid, workerid FROM actions WHERE study = 9 AND action = 'first time'),
   -- accept_time AS (SELECT time, hitid, assid, workerid FROM actions WHERE study = 9 AND action = 'accept'),
   quota_limits AS (SELECT time, workerid, assid, hitid, 1 as quota_reached FROM actions WHERE study = 9 AND action = 'work quota reached'),
   improbability_rate AS (
   		      	 SELECT (other::json->'improbability_rate')::text AS impro_rate, workerid, hitid, assid FROM actions
			 WHERE action = 'accept' AND study = 9
		      ),
   survey_views AS (SELECT workerid, 1 as survey_viewed FROM actions WHERE study = 9 AND action = 'survey'),
   merge_complete_incomplete AS (
-- select other::json->'activity_log'->0 from actions where study = 9 and action = 'finished'
      SELECT DISTINCT ON(a.workerid, a.assid, a.hitid) a.workerid, a.assid, a.hitid, 1 AS completed, 
      	 a.time, (a.other::json->'activity_log'->0->'action_time')::text AS page_load_time, c.availability AS availability, c.disagreeable AS disagreeable, 
         c.improbability_rate AS improbability_rate, c.training_dummy AS training, c.wage AS wage, a.phase, 
         pics.pic1 AS pic1, pics.pic2 AS pic2, pics.pic3 AS pic3, pics.pic4 AS pic4, pics.pic5 AS pic5,
         sv.survey_viewed, ql.quota_reached, w.wait_time, sr.submitted survey_submitted, sr.age, sr.sex, sr.state, sr.income, sr.educ, sr.employment, 
         sr.location, sr.compensation survey_pay, sr.why, si.compensation survey_offered_pay, si.time_allotted survey_deadline, ir.impro_rate,
	 ip.region_code, ip.country_name
   FROM actions a
   INNER JOIN conditions_modified c ON a.condition = c.id
   INNER JOIN pictures pics ON pics.workerid = a.workerid AND pics.hitid = a.hitid AND pics.assid = a.assid
   LEFT OUTER JOIN survey_views sv ON sv.workerid = a.workerid 
   LEFT OUTER JOIN quota_limits ql ON ql.workerid = a.workerid AND ql.hitid = a.hitid AND ql.assid = a.assid 
   LEFT OUTER JOIN waits w ON w.workerid = a.workerid AND w.hitid = a.hitid AND w.assid = a.assid
   LEFT OUTER JOIN improbability_rate ir ON ir.workerid = a.workerid AND ir.hitid = a.hitid AND ir.assid = a.assid
   LEFT OUTER JOIN survey_responses sr ON sr.workerid = a.workerid
   LEFT OUTER JOIN survey_invites si ON a.workerid = si.workerid
   LEFT OUTER JOIN ip_addresses ip ON a.ip = ip.ip
   WHERE a.action = 'finished' AND a.study = 9 AND a.hitid IS NOT NULL AND a.assid IS NOT NULL
   UNION ALL
   SELECT a.workerid, a.assid, a.hitid, 0 AS completed, a.time, 
      (a.other::json->'activity_log'->0->'action_time')::text AS page_load_time, cm.availability as availability, cm.disagreeable as disagreeable, 
      cm.improbability_rate AS improbability_rate, cm.training_dummy AS training, cm.wage AS wage, cn.phase AS phase,
      pics.pic1 AS pic1, pics.pic2 AS pic2, pics.pic3 AS pic3, pics.pic4 AS pic4, pics.pic5 AS pic5,
      sv.survey_viewed, ql.quota_reached, w.wait_time, sr.submitted AS survey_submitted, sr.age, sr.sex, sr.state, sr.income, sr.educ, sr.employment,
      sr.location, sr.compensation survey_pay, sr.why, si.compensation survey_offered_pay, si.time_allotted survey_deadline, ir.impro_rate,
      ip.region_code, ip.country_name
   FROM actions a
   INNER JOIN conditions_nonsubmit cn
   ON a.workerid = cn.workerid AND
      a.assid = cn.assid AND
      a.hitid = cn.hitid
   INNER JOIN conditions_modified cm ON
      cn.condition = cm.id
   INNER JOIN pictures pics ON 
      pics.workerid = a.workerid AND
      pics.hitid = a.hitid AND
      pics.assid = a.assid
   LEFT OUTER JOIN survey_views sv ON sv.workerid = a.workerid 
   LEFT OUTER JOIN quota_limits ql ON ql.workerid = a.workerid AND ql.hitid = a.hitid AND ql.assid = a.assid
   LEFT OUTER JOIN waits w ON w.workerid = a.workerid AND w.hitid = a.hitid AND w.assid = a.assid
   LEFT OUTER JOIN improbability_rate ir ON ir.workerid = a.workerid AND ir.hitid = a.hitid AND ir.assid = a.assid
   LEFT OUTER JOIN survey_responses sr ON sr.workerid = a.workerid
   LEFT OUTER JOIN survey_invites si ON a.workerid = si.workerid
   LEFT OUTER JOIN ip_addresses ip ON a.ip = ip.ip
   WHERE a.action = 'js log on user leaving' AND a.hitid IS NOT NULL AND a.assid IS NOT NULL) 
      SELECT md.workerid, md.hitid, md.assid, md.age, md.sex, md.state, md.income, md.educ, md.employment, md.location, md.survey_pay, md.why, 
         MAX(md.completed) AS completed,
         (COUNT(md.completed) - SUM(completed)) AS num_reject,
         COUNT(md.completed) AS num_loaded,
         md.time, md.availability, md.disagreeable, md.improbability_rate, md.training, md.wage, md.phase, 
         md.pic1, md.pic2, md.pic3, md.pic4, md.pic5,
         COALESCE(md.survey_viewed, 0) AS survey_seen,
         COALESCE(md.quota_reached, 0) AS hit_quota, 
         COALESCE(md.wait_time, 0) AS waiting_time,
         COALESCE(md.survey_submitted, 0) AS survey_taken,
	 survey_deadline, survey_offered_pay, page_load_time, impro_rate, region_code, country_name

      FROM merge_complete_incomplete md --)
      GROUP BY md.workerid, md.hitid, md.assid, md.age, md.sex, md.state, md.income, md.educ, md.employment, md.location, 
      	       md.survey_pay, md.why, md.time, md.availability, md.disagreeable,
               md.improbability_rate, md.training, md.wage, md.phase, md.pic1, md.pic2, md.pic3, md.pic4, md.pic5, survey_seen, 
	       hit_quota, waiting_time, survey_taken, survey_deadline, survey_offered_pay, page_load_time, impro_rate,
	       region_code, country_name
      LIMIT 1000
) To '/tmp/data_extract13.csv' With CSV HEADER;

