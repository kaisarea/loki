survey_pay = 1.00

db.define_table('survey_results'
		, db.Field('workerid', 'text')
		, db.Field('task', 'text')
		, db.Field('result', 'text')
		#, db.Field('comment', 'text')
		#, db.Field('age', 'text')
		#, db.Field('state', 'text')
		#, db.Field('sex', 'text')
		#, db.Field('where', 'text')
		#, db.Field('study', 'text')
		#, db.Field('income', 'text')
		#, db.Field('educ', 'text')
		#, db.Field('employment', 'text')
		#, db.Field('why', 'text')
#		, migrate = True, fake_migrate = True
		)


def announce_survey(study):
    #print("Olleeee")
    workers = db((db.actions.study == study)
                 & (db.actions.workerid != None)
                 & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE')) \
                 .select(db.actions.workerid, distinct=True)
#### nail: the actions table contains the field phase so we can use
### that to flag users who only have taken part in those and flag them
### in a variable and the pass that variable to view and there condition
### a question based on this variable


    workers = [w.workerid for w in workers]
    shadow_workers = workers[0:500]
    workers = shadow_workers
    #print(shadow_workers)
    #workers = ['APAD02SQH0N57', 'A1RI556NVWJKR6']
	# first one is Nail's, second one is Claus'
# this is the list of worker IDs
# this is Nail's workerid: APAD02SQH0N57

#     for worker in workers:
#         message_body = '''Dear Mechanical Turk worker,
#         
#         We are working to improve our HITs and make them more attractive to
#         workers like you.
#         
#         If you fill out the survey using the link below you will receive $%.2f and 
#         our undying gratitude...
#         
#         The survey should take no more than 2 minutes to complete.
# 
# Link to survey: https://yuno.us/survey?workerid=%s&task=%s
# ''' % (survey_pay, workerid, study.task)
# 
#         subject = ('Help us improve our HITs on Mechanical Turk and receive $%.2f'
#                    % (survey_pay))
# 
#         turk.message_worker(worker,
#                             subject,
#                             message_body)

    for worker in workers:
        message_body =  '''Dear Mechanical Turk worker,

Thank you for looking at one of our HITs. We are a new outfit and
have a slightly different way of running our HITs than the other
guys. It is very important for us to improve our HITs and make them 
more attractive to workers like you.

If you fill out the brief survey using the link below you will 
receive $%.2f and our undying gratitude...

The survey should take no more than 2 minutes to complete.
The link will expire in five days, so make sure you fill 
it out soon to receive your compensation.

Link to survey: https://yuno.us/survey?workerid=%s&s=%s \
		''' % (survey_pay, worker, study.id)

        #The CrowdClearingHouse crew
        #print(message_body)
        subject_line =  '''\
		Help us improve our HITs on Mechanical Turk and receive $%.2f \
		''' % (survey_pay)
        task = study.task
	proceed_with_email = True
        #print(request.vars.workerid)
        #print(db.survey_results(task=task, workerid=worker))
        if db.survey_results(task=task, workerid=worker):
          # this worker has already done the survey
          print("This worker has already submitted the survey")
          #continue
          proceed_with_email = False
	# another check -- checking whether the worker was sent an invitation to survey email already
	all_scheduled_emails_to_workers = db(db.scheduler_task.function_name=='message_turk_worker').select(distinct=db.scheduler_task.vars)
	for record_about_email in all_scheduled_emails_to_workers:
		if sj.loads(record_about_email.vars)['worker'] == worker:
			print("This worker was already sent an email from us!")
			proceed_with_email = False
		#elif record_about_email.status == "FAILED":
		#	print("The previous emailed failed to send, resending..")
		#	proceed_with_email = True

	if not proceed_with_email:
		continue

        db.scheduler_task.insert(function_name='message_turk_worker',
                                 application_name='utility/utiliscope',
                                 vars=sj.dumps({'worker' : worker,
                                                'subject_line' : subject_line,
                                                'message_body' : message_body
        						}))
        #db.actions.insert(study=9, action = 'survey email scheduled', workerid = worker, 
	db.commit()
	print("New email sent to a new worker")

        # turk.message_worker(worker,
        #                     subject_line,
        #                     message_body)
