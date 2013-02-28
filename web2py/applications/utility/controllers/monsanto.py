def index():
    return {'current_workerid' : request.workerid}

def finish():
    db.myhit.insert(response=request.vars.worker_name)
    hit_finished()
