

-- SELECT a.id, je.value
-- we can use action time to generate ids
-- '{"a":1,"b":2}'::json->'b'
-- now the question
SELECT a.id, 
   a.hitid,
   a.workerid,
   a.assid,
   a.time,
   a.ip,
   a.condition,
   a.phase,
   a.action,
   a.study,
   0 as completed,
   -- json_each_text(je.value::json), 
   je.value::json->'action_time' action_time,
   je.value::json->'action_type' action_type,
   je.value::json->'baseline_time' baseline_time,
   je.value::json->'relative_time' relative_time
--   je.value::json->'text_field_value' text_entered
FROM actions a CROSS JOIN LATERAL 
   (
      SELECT * FROM json_array_elements_text((
         SELECT other::json FROM actions 
         WHERE action = 'js log on user leaving' and id = a.id)) 
      AS json_data
   ) je 
WHERE a.action = 'js log on user leaving'
LIMIT 10; 
--      AND action_type = 'page_loaded';
