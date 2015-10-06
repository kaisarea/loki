/*
	We are trying to match information from the with picture actions
	with the information from the finished action. This is actually a very interesting
	SQL problem. 

First we need to collect all the finished actions:

SELECT * FROM actions WHERE action = 'finished';

Then we need to create another subquery to look at with pic actions

SELECT * FROM actions WHERE action = 'with pic';

Now we need to join these two on workerid, hitid, possibly even assignment id.


	SELECT * FROM actions LIMIT 10;
*/
Copy 
(
SELECT workerid2 as workerid,
	details,
	ip_finished,
	time_finished,
	hitid2 as hitid,
	assid2 as assignment_id,
	images,
	phase2 as phase,
	time_loaded,
	ip_worked,
	condition2 as condition,
	result as survey_response,
	js_info,
	time_abandoned,
	ip_left
FROM (
	SELECT * FROM
	(
		SELECT * FROM 
		(
			SELECT * FROM 
			(
				SELECT workerid as workerid1, 
					hitid as hitid1, 
					assid as assid1, 
					other as details, 
					phase as phase1, 
					time as time_finished, 
					ip as ip_finished, 
					condition as condition1 
				FROM actions 
				WHERE action = 'finished' AND study = 9
			) AS a1

			FULL OUTER JOIN
	
			(
				SELECT  workerid as workerid2, 
					hitid as hitid2, 
					assid as assid2, 
					other as images, 
					phase as phase2, 
					time as time_loaded, 
					ip as ip_worked, 
					condition as condition2
				FROM actions 
				WHERE action = 'with pic' AND study = 9
			) AS a2
		
			ON
				workerid1 = workerid2 AND
				hitid1 = hitid2 AND
				assid1 = assid2 AND
				phase1 = phase2
		) AS actions_select

		FULL OUTER JOIN

		survey_results
		ON actions_select.workerid1 = survey_results.workerid
	) AS finished_with_pic_survey

	FULL OUTER JOIN
	
	(
		SELECT workerid as workerid3,
			hitid as hitid3,
			assid as assid3,
			other as js_info,
			phase as phase3,
			time as time_abandoned,
			ip as ip_left,
			condition as condition3
		FROM actions
		WHERE action = 'js log on user leaving' AND study = 9
	) AS java_script_logs
	ON workerid2 = workerid3 AND
		hitid2 = hitid3 AND
		assid2 = assid3 AND
		phase2 = phase3
) as final_data_extract -- WHERE workerid IS NOT NULL
) To '/tmp/extract.csv' With CSV HEADER;
