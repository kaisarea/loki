-- the point of this file is to see who was not paid
-- we have a table side_payments but the information in it is very confusing

select count(*) from side_payments group by workerid

;

