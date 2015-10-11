WITH 
availability AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, phase,
      other::json->'for'
   FROM actions WHERE study = 9 AND action = 'wait'),
-- first times
first_time_action AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, phase, other
   FROM actions WHERE study = 9 AND action = 'first time'
),
-- nothing useful in the accept other column
accept_actions AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, phase, other
   FROM actions WHERE study = 9 AND action = 'accept'
),
quota_actions AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, other, phase
   FROM actions WHERE study = 9 AND action = 'work quota reached'
),
-- survey information from the actions table
survey_views AS (
   SELECT workerid, time, ip
   FROM actions WHERE study = 9 AND action = 'survey'),

display_actions AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, phase, other AS page
   FROM actions WHERE study = 9 AND action = 'display'
),
incomplete AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, phase, other, 0 AS completed
   FROM actions 
   WHERE action = 'js log on user leaving'),
-- finished actions
-- finished action will contain rich other data
completed_hits AS(
   SELECT study, action, hitid, workerid, assid, time, ip, condition, phase, 
      other, 1 AS completed
   FROM actions WHERE action = 'finished' AND study = 9
),
-- the following contains some information from the preview page
-- we do not have any workerids here.. because this is before
-- workers accept the first hit
preview AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, other, phase
   FROM actions
   WHERE study = 9 AND action = 'preview'
),

-- the following contains the images shown to the user
with_pic AS (
   SELECT study, action, hitid, workerid, assid, time, ip, condition, 
      other::json->>1 pic1, 
      other::json->>2 pic2,
      other::json->>3 pic3,
      other::json->>4 pic4,
      other::json->>5 pic5,
      phase 
   FROM actions
   WHERE study = 9 AND action = 'with pic')


SELECT DISTINCT ON (i.hitid, i.workerid, i.assid) i.hitid, i.workerid, i.assid, i.completed FROM incomplete i
UNION ALL
SELECT DISTINCT ON(c.hitid, c.workerid, c.assid) c.hitid, c.workerid, c.assid, c.completed FROM completed_hits c;
   
