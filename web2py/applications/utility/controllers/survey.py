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
    if not request.vars.workerid or len(request.vars.workerid) < 1:
        return 'missing workerid'

    if request.vars.task != 'genova' and request.vars.task != 'prisoner':
        return 'Hey Claus, this is Mike.  I just added a check to' \
            + 'force specifying genova or prisoner in the URL.' \
            + 'This is what you see if you don\'t do it.'

    if db.survey_results(task=request.vars.task,
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
                                 task=request.vars.task,
                                 result=sj.dumps(request.vars))
        enqueue_bonus(request.workerid, survey_pay,
                      reason='Thank you for completing our survey!')
        return """
            <h3>Thank you</h3>

            <p>We very much appreciate your time.
            You will receive $%.2f once the survey has been processed.
            You will be paid via bonus and should receive an email from Amazon confirming this.</p>
            """ % survey_pay
    return {}


def results():
    return {'results' : db().select(db.survey_results.ALL)}
