-- take the first HIT for every user and look at the action associated with it
-- 1. take the first HIT for every user


WITH first_time_hit AS (
   SELECT workerid, hitid, min(time) AS first_time
   FROM actions
   WHERE study = 5 AND workerid IS NOT NULL AND hitid IS NOT NULL AND assid IS NOT NULL
   GROUP BY workerid, hitid
)

SELECT a.action, fth.hitid, fth.workerid, a.time
FROM actions a
INNER JOIN first_time_hit fth ON fth.workerid = a.workerid AND fth.hitid = a.hitid
WHERE a.study = 5 AND a.workerid IS NOT NULL AND a.hitid IS NOT NULL
ORDER BY a.workerid, a.time ASC
;
