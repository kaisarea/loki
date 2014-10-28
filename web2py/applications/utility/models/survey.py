survey_pay = 0.20

db.define_table('survey_results',
                db.Field('workerid', 'text'),
                db.Field('task', 'text'),
                db.Field('result', 'text'))


def announce_survey(study):
    workers = db((db.actions.study == study)
                 & (db.actions.workerid != None)
                 & (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE')) \
                 .select(db.actions.workerid, distinct=True)

    workers = [w.workerid for w in workers]
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

Link to survey: https://yuno.us/survey?workerid=%s&s=%s \
		''' % (survey_pay, workerid, study.id)

        #The CrowdClearingHouse crew

        subject_line =  '''\
		Help us improve our HITs on Mechanical Turk and receive $%.2f \
		''' % (survey_pay)

        db.scheduler_task.insert(function_name='message_turk_worker',
                                 application_name='utility/utiliscope',
                                 vars=sj.dumps({'worker' : worker,
                                                'subject_line' : subject_line,
                                                'message_body' : message_body}))
        db.commit()

        # turk.message_worker(worker,
        #                     subject_line,
        #                     message_body)
