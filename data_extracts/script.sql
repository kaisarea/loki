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
(SELECT 
	a1.workerid
	, a1.hitid
	, a1.other as js_info
  	, a2.other as pic_info
	, a1.phase
	, a1.time as time_finished
	, a2.time as time_displayed
	, a1.ip as ip_finished
	, a2.ip as ip_viewed
	, a1.condition 
	, survey.result
FROM 
	actions a1
	, actions a2
	, survey_results survey
WHERE 
	a1.workerid = a2.workerid 
	AND a1.hitid = a2.hitid 
	AND a1.assid = a2.assid 
	AND a1.phase = a2.phase 
	AND a1.action = 'finished' 
	AND a2.action = 'with pic' 
	AND a1.study = 9 
	AND a2.study = 9
	AND survey.workerid = a1.workerid) To '/tmp/extract.csv' With CSV;  
