survey_pay = .20

# Things to do:
# - Improve the HTML
#   DONE - Fix the images for prisoner/genova in prisoner html
#   DONE - Make the submit button not orange
#   - ??? anything else ???
# - Do we want a server-side validation function?  Probably not necessary.
# - When ready, prolly re-enable the check that they've completed this hit
# - Test it (multiple browsers, etc.)
#
# - Craft a good outgoing survey email message in models/survey.py
#   in the announce_survey() function I just made there
# - Test it

def index():
    study = request.vars.s
    workerid = request.vars.workerid

    if not request.vars.testing:
        db.actions.insert(study=study,
                          action='survey',
                          hitid=None,
                          workerid=workerid,
                          assid=None,
                          ip=request.env.remote_addr,
                          condition=None,
                          other=None)

    # Check workerid
    if not workerid or len(workerid) < 1:
        return 'missing workerid'

    # Check study
    study = db.studies(study)
    if not study: return 'Missing s parameter.  (ask mike)'

    # Check task
    task = study.task
    if not task or (task != 'genova' and task != 'prisoner'):
        return 'No task on this s'

    if db.survey_results(task=task,
                         workerid=request.vars.workerid):
        return 'You already completed this survey.' \
        	+ 'If you feel you have gottent this message in error please contact us at XXXX@XXXX.'

    # # Make sure they actually completed some of these hits
    # if len(db((db.actions.workerid==request.vars.workerid)
    #           & (db.actions.study == db.studies.id)
    #           & (db.studies.task == request.vars.task)
    #           & (db.actions.action == 'finished')).select()) == 0:
    #     return 'You did not complete this hit'

    # If this was a POST with the survey data, let's collect the
    # survey results and pay them
    if 'age' in request.vars:
        db.survey_results.insert(workerid=request.vars.workerid,
                                 task=task,
                                 result=sj.dumps(request.vars))
        enqueue_bonus(request.workerid, survey_pay,
                      reason='Thank you for completing our survey!')
        return """
            <h3>Thank you</h3>

            <p>We very much appreciate your time.
            You will receive $%.2f once the survey has been processed.
            You will be paid via bonus and should receive an email from Amazon confirming this.</p>
            """ % survey_pay
    return {'hits_completed' : hits_done(workerid=request.vars.workerid,
                                         study=study),
            'survey_pay_string' : '$%.2f' % survey_pay,
            'task' : task}


def results():
    return {'results' : db().select(db.survey_results.ALL)}
