WITH debug AS  (select assid, time, action from actions where workerid = 'A100KJ2EG9OH1A' and assid = '39RP059MEHTSSXI3BJCXJTZENOWBMV' and hitid = '3RWB1RTQDJNCPIJFALFDLB8NV508P4'
UNION ALL     
select assid, time, action from actions where workerid = 'A100KJ2EG9OH1A' and hitid = '3AQN9REUTFGIFR77IGMCKUF0A1ZDY8' and assid = '3MHW492WW0D71BG9G03XK5TLQGBVMK')
SELECT assid, time, action from debug order by time asc;                
