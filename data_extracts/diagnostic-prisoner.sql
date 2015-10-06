--select action, count(DISTINCT ON (hitid, workerid)) as count 
--from actions where study = 5 and action <> 'survey' and action <> 'work quota reached' 
--group by action 
--order by count desc;

SELECT action, COUNT(*) AS frequency FROM 
(
   SELECT action, hitid, workerid, assid 
   FROM actions
   WHERE study = 5 AND action <> 'survey' AND action <> 'work quota reached' AND workerid IS NOT NULL AND hitid IS NOT NULL AND assid IS NOT NULL
   AND (other IS NOT NULL OR action <> 'submit')
   GROUP BY action, workerid, hitid, assid
) AS unique_actions
GROUP BY action
ORDER BY frequency DESC;
