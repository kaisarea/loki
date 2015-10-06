
Copy 
(SELECT
	a1.workerid,
	a1.phase,
	a1.hitid,
	a1.assid
FROM
	actions a1, 
	actions a2
WHERE 
	a1.workerid = a2.workerid 	AND
	a1.hitid = a2.hitid		AND
	a1.assid = a2.assid		AND
	a1.phase = a2.phase		AND
	a1.action = 'with pic' 		AND
	a2.action = 'finished' 		AND
	a1.study = 9 			AND
	a2.study = 9) To '/tmp/test-extract.csv' With CSV;
