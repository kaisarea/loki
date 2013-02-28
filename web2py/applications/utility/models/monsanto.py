options.myhit = {'price' : [.01, .02, .03]}
db.define_table('myhit',                   # Make a database table for this hit
                db.Field('response', 'text'))  # it will store worker' response
