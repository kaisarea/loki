from __future__ import division
survey_pay = 1.00 

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
    study_number = study
    if not request.vars.testing:
        db.actions.insert(study=study,
                          action='survey',
                          hitid=None,
                          workerid=workerid,
                          assid=None,
                          ip=request.env.remote_addr,
                          condition=1,
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
        	+ 'If you feel you have gotten this message in error please contact us at feedback@crowdclearinghouse.com.'

    # # Make sure they actually completed some of these hits
    if len(db((db.actions.workerid==workerid) & (db.actions.study == study_number) & (db.studies.task == task) & (db.actions.action == 'finished')).select()) == 0:
         return 'You did not complete this hit'

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
#In [25]: a = db((db.actions.study == 11) & (db.actions.workerid == 'APAD02SQH0N57')).select(db.actions.phase, distinct=True)
    phases_of_this_worker = db((db.actions.study == study) & (db.actions.workerid == request.vars.workerid)).select(db.actions.phase, distinct=True)
    if len(phases_of_this_worker) == 1 and phases_of_this_worker[0].phase == None:
      number_of_phases = 0
    else:
      number_of_phases = len(phases_of_this_worker) 
    #list_of_phases = []
    #for particular_phase in phases_of_this_worker:
    #  list_of_phases.append(particular_phase.phase)
    #if len(list_of_phases) == 0:
    #  last_phase = -1
    #else:
    #  last_phase = max(list_of_phases)
    #  if last_phase == None:
    #    last_phase = -1

    return {'hits_completed' : hits_done(workerid=request.vars.workerid, 
                                         study=study, phase=None),
            'survey_pay_string' : '$%.2f' % survey_pay,
            'number_of_phases': number_of_phases,
            'task' : task}


def results():
    proportion = len(db().select(db.survey_results.ALL))/5
    return {'results' : db().select(db.survey_results.ALL),
		'proportion': proportion}
