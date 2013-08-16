survey_pay = .20

def index():
    '''
    In here, check:
     - Have they done the task?

    Then when they do it for the first time, pay them and insert into
    database.
    '''

    if not request.vars.workerid or len(request.vars.workerid) < 1:
        return 'missing workerid'

    if request.vars.task != 'genova' and request.vars.task != 'prisoner':
        return 'Hey Claus, this is Mike.  I just added a check to' \
            + 'force specifying genova or prisoner in the URL.' \
            + 'This is what you see if you don\'t do it.'

    if db.survey_results(task=request.vars.task,
                         workerid=request.vars.workerid):
        return 'You already completed this survey'

    tmp = db((db.actions.workerid==request.vars.workerid)
             & (db.actions.study == db.studies.id)
             & (db.studies.task == request.vars.task)
             & (db.actions.action == 'finished')).select()

    if len(tmp) == 0:
        pass
        #return 'You did not complete this hit'

    if "age" in request.vars:
        #db.bonus_queue.insert
        db.survey_results.insert(workerid=request.vars.workerid,
                                 task=request.vars.task,
                                 result=request.vars)
        return """
            <h3>Thank you</h3>

            <p>We very much appreciate your time.
            You will receive $%.2f once the survey has been processed.
            You will be paid via bonus and should receive an email from Amazon confirming this.</p>
            """ % survey_pay
    return {}


def results():
    return {'results' : db().select(db.survey_results.ALL)}
