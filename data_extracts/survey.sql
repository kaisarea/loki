WITH surveyInvites AS (
   SELECT workerid, compensation, created_at 
   FROM survey_invitations 
   WHERE created_at::date > '2015-03-01'
), surveyResults AS (
   SELECT workerid, compensation, created_at
   FROM survey_results
   WHERE created_at::date > '2015-03-01'
), survey_payments AS (
   SELECT payment_amount, associated_hitid, created_at, workerid, purpose
   FROM side_payments
   WHERE created_at::date > '2015-03-01' and created_at IS NOT NULL
)
SELECT si.workerid, si.compensation invite_pay, sr.compensation result_pay, sp.payment_amount actual_pay, sp.created_at, sr.created_at FROM surveyInvites si
INNER JOIN surveyResults sr ON sr.workerid = si.workerid
INNER JOIN survey_payments sp ON si.workerid = sp.workerid
ORDER BY sp.payment_amount DESC



;

-- you will reeive $2.00 and our gratitude
