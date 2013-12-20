options.survey = {'price' : [.15, .30],
                  'mystery_task': True,
                  'work_limit' : 20}


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
    for worker in workers:
        message_body = '''blah blah title.

Link to survey: http://yuno.us:8003/survey?workerid=%s&task=%s
''' % (workerid, study.task)

        turk.message_worker(worker,
                            '[put subject here]',
                            message_body)
