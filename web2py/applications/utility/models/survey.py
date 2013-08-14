options.survey = {'price' : [.15, .30],
                  'mystery_task': True,
                  'work_limit' : 20}


db.define_table('survey_results',
                db.Field('workerid', 'text'),
                db.Field('result', 'text'))