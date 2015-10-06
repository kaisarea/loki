WITH survey_views AS (
  SELECT workerid, time, ip
  FROM actions
  WHERE study = 9 AND action = 'survey'),

     unfinished_hits AS (
  SELECT workerid, hitid, assid, time, ip, condition, other, phase
  FROM actions
  WHERE action = 'js log on user leaving'),

 ;


