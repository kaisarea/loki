def index():
	hits_open = db(db.hits.status=='closed').select()
	hits_closed_count = len(hits_open)
	return "There are %s closed HITs" % hits_closed_count    
	# ok, so our first dashboard app is gonna tell us how many HITs are close and how many are open
	# hello hello
