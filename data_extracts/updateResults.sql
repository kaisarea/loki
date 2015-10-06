

BEGIN;

DELETE FROM survey_results WHERE task IS NULL AND workerid IN 
(

SELECT workerid
FROM survey_results
GROUP BY workerid
HAVING count(workerid) > 1

)
;

SELECT COUNT(*) FROM survey_results WHERE task IS NULL;
COMMIT;
--ROLLBACK;
