def index():
    if "age" in request.vars:
        db.survey_results.insert(workerid=request.workerid,
                                 result=request.vars)
        request.errors=""
        validates=True
        for var in ["sex","age","state","educ","employment","where","duration","income"]:
            if not(var in request.vars and request.vars[var] != ""):
                validates = False
                request.errors+= "You did not answer the " + var + " question. <br>" 
        if validates:
            return """
            <h3>Thank you</h3>

            <p>We very much appreciate your time.
            You will receive $XXX once the survey has been processed.
            You will be paid via bonus and should receive an email from Amazon confirming this.</p>
            """                
    return {}


def results():
    return {'results' : db().select(db.survey_results.ALL)}
