options.genova = {'price' : [.01, .02, .03]}
db.define_table('pprofiles', db.Field('name'), 
			     db.Field('photo', 'upload'), 
			     db.Field('treatment'), 
			     db.Field('message'), 
			     db.Field('crime'))
