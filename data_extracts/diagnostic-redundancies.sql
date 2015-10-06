

SELECT workerid, assid, hitid, JSON_AGG(time), JSON_AGG(other) 
FROM actions
WHERE study = 5 AND action = 'submit'
GROUP BY workerid, assid, hitid
HAVING COUNT(time) > 1

;
