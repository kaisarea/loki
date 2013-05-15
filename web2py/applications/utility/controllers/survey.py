def index():
    if request.vars.q1:
        db.survey_results.insert(assid=request.assid,
                                 result=request.vars)
        return {}#..
    return {}


def results():
    return {'results' : db.survey_results.all()}
