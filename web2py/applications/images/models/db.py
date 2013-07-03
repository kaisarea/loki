db = DAL('postgres://nail:serbial7@localhost/nail_utility')

db.define_table('venice', Field('name'), Field('photo', 'upload'),
    Field('treatment'), Field('message'), Field('crime'), format= '%(title)s')
