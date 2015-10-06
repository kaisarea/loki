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
WITH submissions_data AS (
	SELECT LEFT(RIGHT(si.created_at, 8), 2) hours, count(LEFT(RIGHT(si.created_at, 8), 2)) submissions 
	FROM survey_invitations si join survey_results sr 
	ON sr.workerid = si.workerid 
	GROUP BY hours 
	),
     invitations_data AS (
        SELECT LEFT(RIGHT(si.created_at, 8), 2) hours, count(LEFT(RIGHT(si.created_at, 8), 2)) invitations
        FROM survey_invitations si
        GROUP BY hours
        )
SELECT s.hours, s.submissions, i.invitations, s.submissions/i.invitations::float as ratio
FROM submissions_data s 
JOIN invitations_data i
ON i.hours = s.hours
ORDER BY ratio DESC;
