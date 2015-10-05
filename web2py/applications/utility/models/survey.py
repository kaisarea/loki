import random
import xml.etree.ElementTree as ET


survey_pay = 0.75
deadline_days = 5

db.define_table('survey_results'
		, db.Field('workerid', 'text')
		, db.Field('task', 'text')
		, db.Field('result', 'text')
		, db.Field('comment', 'text')
		, db.Field('age', 'text')
		, db.Field('state', 'text')
		, db.Field('sex', 'text')
		, db.Field('location', 'text')
		, db.Field('study', 'text')
		, db.Field('income', 'text')
		, db.Field('educ', 'text')
		, db.Field('employment', 'text')
		, db.Field('why', 'text')
		, db.Field('compensation', 'double')
                , db.Field('created_at', 'text')
		)

db.define_table('survey_invitations'
  , db.Field('workerid', 'text')
  , db.Field('compensation', 'double')
  , db.Field('task', 'text')
  , db.Field('created_at', 'text')
  , db.Field('email_content', 'text')
  , db.Field('time_allotted', 'integer'))


def pay_unpaid_survey():
    unpaid_surveyers = db((db.side_payments.status=="OUTSTANDING")).select()
    for payment_case in unpaid_surveyers:
        print(payment_case.workerid)
        print(payment_case.payment_amount)
        payment_success_state = pay_worker_direct(payment_case.workerid, payment_case.payment_amount, 'Thank you for completing our survey!')
        #payment_success_state = "SUCCESS"
        if payment_success_state == "SUCCESS":
            payment_case.update_record(status='SUCCESS', purpose='survey payment')
            db.commit()
            print("Worker %s bonused successfully" % payment_case.workerid)
        else:
            print("Payment for worker %s failed" % payment_case.workerid)

def workers_not_paid_api():
    survey_submitters = db((db.survey_results.workerid != None)).select(db.survey_results.workerid, db.survey_results.created_at, db.survey_results.compensation)
    assignments_disappeared = 0
    initializer = 0
    workers_to_be_paid = []
    payments_to_be_made = []
    for worker in survey_submitters:
        #print(worker)
        initializer += 1
        if initializer > 10000:
            break
        all_assignments = db((db.actions.workerid==worker.workerid)).select(db.actions.assid, distinct=True)
        #ass = db(
        #    (db.actions.workerid==worker.workerid) & 
        #    ((db.actions.action=='accept') | (db.actions.action=='finished'))).select(orderby=~db.actions.time, limitby=(0,1)).first()
        #print()
        #try:
        #    (assid, hitid) = lookup_recent_assignment(worker.workerid, None, None)
        #except:
        #    print("lookup failed")
        #    assid = None
        #    hitid = None
        #print(ass.assid)
        #print(assid)
        #if not ass:
        #    assignments = [assid, None]
        #else:
        #    assignments = [assid, ass.assid]
        if not all_assignments:
            print("no asses found")
            continue
        else:
            assignments = [i.assid for i in all_assignments]
        survey_payments_for_this_worker = 0
        print(assignments)
        for AssId in assignments:
            if survey_payments_for_this_worker > 0:
                break
            if not AssId:
                print(AssId)
                print(assignments)
                print("Not able to find assid for this worker in our database, skipping..")
                continue

            params = {'AssignmentId' : AssId, 'PageSize' : 100}
            bonus_payments = turk.ask_turk_raw('GetBonusPayments', params)
            print(bonus_payments)
            root = ET.fromstring(bonus_payments)
            if not root.find('GetBonusPaymentsResult').find('Request').find('Errors'): #.find('Error'):
                numResults = int(root.find('GetBonusPaymentsResult').find('TotalNumResults').text)
                print("Number of results in the XML: %s" % str(numResults))
                if numResults == 0:
                    print("no results here")
                    #survey_payments_for_this_worker = None
                    continue
                for payment_instance in root.iter('BonusPayment'):
                    if "survey" in str(payment_instance.find('Reason').text):
                        print("This guy received a bonus!")
                        survey_payments_for_this_worker += 1
            else:
                print("Assignment ID was lost in the Mech Turk API")
                assignments_disappeared += 1
                continue
        
        print(survey_payments_for_this_worker)
        if survey_payments_for_this_worker == 0:
            database_record = db((db.survey_invitations.workerid==worker.workerid)).select(orderby=~db.survey_invitations.compensation).first()
            workers_to_be_paid.append(worker.workerid)
            if not database_record or not database_record.compensation:
                print("information about the size of payments due not found")
            else:
                print(database_record.compensation)
                payments_to_be_made.append(float(database_record.compensation))
                db.side_payments.insert(payment_amount=database_record.compensation, 
                                        status = 'OUTSTANDING', 
                                        workerid = worker.workerid, 
                                        associated_assid = AssId)
                db.commit()
                #payment_outcome = pay_worker_direct(worker.workerid, database_record.compensation, 'Thank you for completing our survey!')
                #print(payment_outcome)
        print("So far %s workers to be paid" % str(len(workers_to_be_paid)))
        print("So far %s dollars to be paid" % str(sum(payments_to_be_made)))
        print("%s workers screened so far" % str(initializer))
        #db.side_payments.insert(payment_amount=
    print(workers_to_be_paid)
    print(len(workers_to_be_paid))
    print(sum(payments_to_be_made))

def reinvite_email():
  compensation = 2.00
  # we want workers who 
  # 1) accessed the survey
  # 2) finished a HIT in study 9
  # ---> take a difference between the two sets
  # add condition to select only workers who have accepted the preview HIT

  workers_accessing_the_survey = db((db.actions.study == 9) & (db.actions.workerid != None) & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE') & (db.actions.action == 'survey')).select(db.actions.workerid, distinct=True)
  workers_who_finished_hit = db((db.actions.study == 9) & (db.actions.workerid != None) & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE') & (db.actions.action == 'finished')).select(db.actions.workerid, distinct=True)
  workers_accept = db((db.actions.study == 9) & (db.actions.workerid != None) & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE') & (db.actions.action == 'accept')).select(db.actions.workerid, distinct=True)
  submitted_the_survey = db((db.survey_results.workerid != None)).select(db.survey_results.workerid, distinct=True)
  workers_who_accepted = [single.workerid for single in workers_accept]
  workers_accessing_the_survey = [entry.workerid for entry in workers_accessing_the_survey]
  workers_who_finished_hit = [item.workerid for item in workers_who_finished_hit]
  workers_who_submitted = [this_worker.workerid for this_worker in submitted_the_survey]
  workers_did_not_accept = set(workers_accessing_the_survey) - set(workers_who_accepted)
  #print(workers_test) 
  access_survey_but_not_finish_hit = set(workers_accessing_the_survey) - set(workers_who_finished_hit)
  print(len(access_survey_but_not_finish_hit))
  access_survey_but_not_finish_hit = access_survey_but_not_finish_hit - set(workers_who_submitted)
  print(len(access_survey_but_not_finish_hit))
  access_survey_but_not_finish_hit = access_survey_but_not_finish_hit - workers_did_not_accept
  access_survey_but_not_finish_hit = list(access_survey_but_not_finish_hit)
  print(len(access_survey_but_not_finish_hit))
  access_survey_but_not_finish_hit = access_survey_but_not_finish_hit[1:]

  for workerid in access_survey_but_not_finish_hit:
    #message = '''Dear Mechanical Turk worker,
    #  Thank you for accessing a survey we designed for you. Our records indicate that our system contained a faulty code that prevented you from actually seeing the survey, not to mention submitting it. We apologize to you for this mistake. We would like to invite you to participate in this survye again, this time for $%.2f. The link is as before https://yuno.us/survey?workerid=%s&s=9 ''' % (compensation, workerid) 
    message = '''Dear Mechanical Turk worker,
    	Thank you for accessing our survey. Unfortunately, the survey webpage contained faulty code that prevented you from seeing the survey. We are very sorry for this and would like to invite you to complete the survey, this time for $%.2f. The link is as before https://yuno.us/survey?workerid=%s&s=9 ''' % (compensation, workerid)
    subject = '''Sorry you were not able to see our survey, try again for $%.2f''' % compensation
    #subject = '''Sorry you were not able to see the survey, try again for $%.2f''' % compensation
    db.scheduler_task.insert(function_name='message_turk_worker', application_name='utility/utiliscope', vars=sj.dumps({'worker' : workerid, 'subject_line' : subject, 'message_body' : message}))
    survey_scheduled_time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    db.survey_invitations.insert(workerid=workerid, compensation=compensation, task=9, created_at=survey_scheduled_time_stamp, email_content=message)
    db.commit()
    print(message)
    print(subject)
    print("Apology sent to a worker %s" % workerid)

	
def announce_survey(study):
  workers = db((db.actions.study == study) & (db.actions.workerid != None) & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE') & (db.actions.action == 'accept')).select(db.actions.workerid, distinct=True)

  workers = [w.workerid for w in workers]
  print(len(workers))
  shadow_workers = workers[4000:len(workers)]
  workers = shadow_workers
  #workers = ['APAD02SQH0N57', 'A1RI556NVWJKR6']
	# first one is Nail's, second one is Claus'

  for worker in workers:
    message_body =  '''Dear Mechanical Turk worker,

Thank you for looking at one of our HITs. We are a new outfit and have a slightly different way of running our HITs than the other guys. It is very important for us to improve our HITs and make them more attractive to workers like you.

If you fill out the brief survey using the link below you will receive $%.2f and our undying gratitude...

The survey should take no more than 2 minutes to complete. The link will expire in %s days, so make sure you fill it out soon to receive your compensation.

Link to survey: https://yuno.us/survey?workerid=%s&s=%s ''' % (survey_pay, deadline_days, worker, study.id)

    subject_line =  '''Help us improve our HITs on Mechanical Turk and receive $%.2f ''' % (survey_pay)
    task = study.task
    proceed_with_email = True
    if db.survey_results(task=task, workerid=worker):
      # this worker has already done the survey
      #print("This worker has already submitted the survey")
      #continue
      proceed_with_email = False
	  # another check -- checking whether the worker was sent an invitation to survey email already
    # here it would be a good idea to implemented checking the newly created survey_invitations table
    all_scheduled_emails_to_workers = db(db.scheduler_task.function_name=='message_turk_worker').select(distinct=db.scheduler_task.vars)
    for record_about_email in all_scheduled_emails_to_workers:
      if sj.loads(record_about_email.vars)['worker'] == worker:
        print("This worker was already sent an email from us!")
        proceed_with_email = False
		    #elif record_about_email.status == "FAILED":
		    #	print("The previous emailed failed to send, resending..")
		    #	proceed_with_email = True

    # alternative check of whether a worker has received an email
    if db.survey_invitations(task=task, workerid=worker):
      # this worker has received an email from us!
      proceed_with_email = False

    if not proceed_with_email:
      continue

    db.scheduler_task.insert(function_name='message_turk_worker', application_name='utility/utiliscope',
                                 vars=sj.dumps({'worker' : worker,
                                                'subject_line' : subject_line,
                                                'message_body' : message_body}))
    #db.actions.insert(study=9, action = 'survey email scheduled', workerid = worker, 
    survey_scheduled_time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')    
    db.survey_invitations.insert(workerid=worker, compensation=survey_pay, task=task, created_at=survey_scheduled_time_stamp, email_content=message_body, time_allotted=deadline_days)
    db.commit()
    print("New email sent to a new worker")


def second_wave_email(study):
   random.seed(123456)
   compensation = 2.00
   workers_accept = db((db.actions.study == 9) & (db.actions.workerid != None) & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE') & (db.actions.action == 'accept')).select(db.actions.workerid, distinct=True)
   workers_accessed_survey = db((db.actions.study == 9) & (db.actions.workerid != None) & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE') & (db.actions.action == 'survey')).select(db.actions.workerid, distinct = True)
   submitted_the_survey = db((db.survey_results.workerid != None)).select(db.survey_results.workerid, distinct=True)
   survey_submits_list = [one.workerid for one in submitted_the_survey]
   list_workers_accept = [one.workerid for one in workers_accept]
   list_workers_accessed_survey = [one.workerid for one in workers_accessed_survey]
   workers_not_seen_survey = list( set(list_workers_accept) - set(survey_submits_list) )
   #workers_not_seen_survey = ['A1RI556NVWJKR6']
   print(len(workers_not_seen_survey))
   workers_not_seen_survey = workers_not_seen_survey[2010:len(workers_not_seen_survey)]
   for workerid in workers_not_seen_survey:
      deadline_days = int(round(random.uniform(0.5, 10.49)))
      if workerid == 'A1VI3SOIHT6Y0D':
         proceed_with_email = False
         print("Run for your livees!!!")
         continue
      message = '''Dear Mechanical Turk worker,\n\nThank you for looking at one of our HITs. We are a new outfit and it is very important for us to improve our HITs and make them more attractive to workers like you.\n\nWe are sending a second invitation to our survey in case the first one did not find you at a convenient time or landed in your spam folder. If you fill out the brief survey using the link below you will receive $%.2f and our gratitude. The survey should take no more than 2 minutes to complete.\n\nThe link will expire in %s days, so make sure you fill it out soon to receive your compensation.\n\nLink to the survey: https://yuno.us/survey?workerid=%s&s=9 ''' % (compensation, deadline_days, workerid)
      """   message = '''Dear Mechanical Turk worker, 
         Thank you for looking at one of our HITs. We are a new outfit and it is very important for us to improve our HITs and make them more attractive to workers like you. We are sending a second invitation to our survey to you in case the first one did not find you at a convenient time or landed in your spam folder by accident. If you fill out the brief survey using the  link below you will receive $%.2f and our gratitude. The survey should take no more than 2 minutes to complete. The link will expire in %s days, so make sure you fill it out soon to receive your compensation.

         Link to the survey: https://yuno.us/survey?workerid=%s&s=9 ''' % (compensation, deadline_days, workerid)                 """
      subject_line = '''Feedback to our HITs on Mechanical Turk -- reward $%.2f ''' % (compensation)
      task = study.task
      proceed_with_email = True
      if db.survey_results(task=task, workerid=workerid):
         proceed_with_email = False
      all_scheduled_emails_to_workers = db(db.scheduler_task.function_name=='message_turk_worker').select(distinct=db.scheduler_task.vars)
      email_count = 0
      for record_about_email in all_scheduled_emails_to_workers:
         if sj.loads(record_about_email.vars)['worker'] == workerid:
            email_count+=1
      if email_count > 1:
         proceed_with_email = False
      else:
         proceed_with_email = True

            #if workerid == 'A1RI556NVWJKR6':
               #proceed_with_email = True
               #print("Claus is getting an email")
            #else:
               #print("This worker was already sent an email from us!")
               #proceed_with_email = False

    # alternative check of whether a worker has received an email
      #if db.survey_invitations(task=task, workerid=workerid):
      # this worker has received an email from us!
      #   if workerid == "A1RI556NVWJKR6":
       #     proceed_with_email = True
       #     print("Claus is getting an email")
       #  else:
       #     print("This worker has received an email already")
       #     proceed_with_email = False

      if not proceed_with_email:
         continue

      db.scheduler_task.insert(function_name='message_turk_worker', application_name='utility/utiliscope',
                                 vars=sj.dumps({'worker' : workerid,
                                                'subject_line' : subject_line,
                                                'message_body' : message}))
      survey_scheduled_time_stamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')    
      db.survey_invitations.insert(workerid=workerid, compensation=compensation, task=task, created_at=survey_scheduled_time_stamp, email_content=message, time_allotted=deadline_days)
      db.commit()
      print("New email sent to a new worker")


def pay_all_survey_takers():
   submitted_the_survey = db((db.survey_results.workerid != None) & (db.survey_results.created_at != None) & (db.survey_results.created_at > '2015-03-01') & (db.survey_results.compensation == 2)).select(db.survey_results.workerid, distinct=True)
   got_paid = db((db.side_payments.purpose == 'Thank you for completing our survey!') & (db.side_payments.payment_amount == 2)).select(db.side_payments.workerid, distinct=True)
   submitted_the_survey = [one.workerid for one in submitted_the_survey]
   got_paid = [one.workerid for one in got_paid]
   diff = list( set(submitted_the_survey) - set(got_paid) )
   #diff = diff[0:175]
   print(diff)
   print(len(diff))
   for worker in diff:
      try:
        pay_worker(worker, 2.0, 'Thank you for completing our survey!')
      except TurkAPIError:
         print("assid expired")
         continue

