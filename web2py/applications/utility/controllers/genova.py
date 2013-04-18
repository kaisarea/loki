def index():
	return {'current_workerid' : request.workerid}

def finish(): 
	db.venice.insert(id=request.vars.id, crime=request.vars.crime, photo=request.vars.photo, 
			 name=request.vars.name, treatment=request.vars.treatment, message=request.vars.message)
	hit_finished()
