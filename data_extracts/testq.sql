   SELECT workerid, assid, hitid  
   FROM actions 
   WHERE study = 9 AND 
      workerid IS NOT NULL AND 
      hitid IS NOT NULL 
      AND assid IS NOT NULL
      AND action = 'finished'
   GROUP BY workerid, hitid, assid
;
