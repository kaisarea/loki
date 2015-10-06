Copy (
   SELECT action, hitid, workerid, assid, time, condition, other, phase 
   FROM actions WHERE study = 9 AND workerid IS NOT NULL and hitid IS NOT NULL AND assid IS NOT NULL AND action <> 'survey' 
) To '/tmp/actions_study_9.csv' With CSV HEADER;

