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
 
) as final_data_extract -- WHERE workerid IS NOT NULL
) To '/tmp/extract_2015_02_10.csv' With CSV HEADER;
