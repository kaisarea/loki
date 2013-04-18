options.prisoner = {'price' : [.01, .02, .03],
                    'experimental_treatment' : [1, 0],
                    'mystery_task': True,
                    'work_limit' : 20}


db.define_table('worker_response',
                Field('message', 'text'),
                Field('worker_id'),
                Field('prisoner_name', 'text'),
		Field('prisoner_crime', 'text'),
		Field('prisoner_photo', 'text'),
		Field('prisoner_message', 'text'),
		Field('price', 'text'),
                Field('treatment'),
		Field('response_length'),
        Field('displayed'))


db.define_table('venice', Field('name'), Field('photo'),
    Field('message', 'text'), Field('crime', 'text'), Field('crime_control', 'text'))
    
#db.define_table('prisoners', Field('name'), Field('photo'),
#    Field('message', 'text'), Field('crime', 'text'), Field('crime_control', 'text'))

#db.prisoners.truncate()

#for row in db().select(db.venice.ALL):
#    db.prisoners.insert(name=row.name, photo=row.photo, message=row.message, crime=row.crime, crime_control=row.crime_control)


#for i in xrange(1,20):
#    random_row_1 = db().select(db.prisoners.ALL,orderby='<random>',limitby=(0,1))[0]
#    random_row_2 = db().select(db.prisoners.ALL, orderby='<random>',limitby=(0,1))[0]
#    tit = random_row_1.name
#    tat = random_row_2.name
#    random_row_1.update_record(name=tat)
#    random_row_2.update_record(name=tit)
