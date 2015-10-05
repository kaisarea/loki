from __future__ import division
import time
import datetime
from bokeh.plotting import figure, output_file, show, HBox, VBox
import numpy as np
#from bokeh.plotting import figure, HBox, output_file, show, VBox
from bokeh.models import Range1d
#from bokeh.plotting import figure, output_file, show

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
    if len(db((db.actions.workerid==workerid) & (db.actions.study == study_number) & (db.actions.action == 'accept')).select()) == 0:
         return 'We need people who have actually seen our HIT to take this survey'

    # If this was a POST with the survey data, let's collect the
    # survey results and pay them
    # at this point we should recover the promised pay from the survey_invitations table
    invitations_received_by_worker = db(db.survey_invitations.workerid==request.vars.workerid).select(db.survey_invitations.compensation)
    compensation_promised_to_the_worker = max([i.compensation for i in invitations_received_by_worker])
    #compensation_promised_to_the_worker = db.survey_invitations(workerid=request.vars.workerid).compensation	
    survey_submit_time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    if 'age' in request.vars:
        db.survey_results.insert(workerid=request.vars.workerid, 
          task=task,
          result = sj.dumps(request.vars),
          comment = request.vars.comment,
          age = request.vars.age,
          state = request.vars.state,
          sex = request.vars.sex,
          location = request.vars.where,
          study = study.id,
          income = request.vars.income,
          educ = request.vars.educ,
          employment = request.vars.employment,
          why = request.vars.why,
          compensation = compensation_promised_to_the_worker,
          created_at = survey_submit_time_stamp)

	# but we will have to include the legacy case where people from the
	# old system try to log in
	if not (db.survey_invitations(workerid=request.vars.workerid) is None):
		enqueue_bonus(workerid, compensation_promised_to_the_worker, reason='Thank you for completing our survey!')
	else:
		enqueue_bonus(workerid, 1.0, reason='Thank you for completing our survey!')

        return """
            <h3>Thank you</h3>

            <p>We very much appreciate your time.
            You will receive $%.2f once the survey has been processed.
            You will be paid via bonus and should receive an email from Amazon confirming this.</p>
            """ % compensation_promised_to_the_worker
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
            'survey_pay_string' : '$%.2f' % compensation_promised_to_the_worker,
            'number_of_phases': number_of_phases,
            'task' : task}


def results():
  proportion = len(db().select(db.survey_results.ALL))*100/(len(db().select(db.survey_invitations.ALL))+499)

  # income
  income_data = []
  income_index = []
  gender_data = []
  age_data = []
  state_data = []
  location_data = []
  education_data = []
  employment_data = []
  reason_for_leaving_data = []

  income_brackets = np.array(['less than $20,000', '$20,000 - $39,999', '$40,000 - $59,999', 
				'$60,000 - $79,999', '$80,000 - $99,999', '$100,000 - $119,999',
    				'$120,000 - $139,999', '$140,000 - $159,999', 'More than $160,000',
 				'Prefer not to answer'])

  meta_compensation_data = {
    '11': 'Prefer not to answer', 
    '2': 'less than $20,000',
    '3': '$20,000 - $39,999',
    '4': '$40,000 - $59,999',
    '5': '$60,000 - $79,999',
    '6': '$80,000 - $99,999',
    '7': '$100,000 - $119,999',
    '8': '$120,000 - $139,999',
    '9': '$140,000 - $159,999',
    '10': 'More than $160,000'}
  for survey_row in db().select(db.survey_results.ALL):
    if (survey_row.income is not None and survey_row.income != ""):
#d = dict()

#for i in xrange(100):
#    key = i % 10
#    if key in d:
#        d[key] += 1
#    else:
#        d[key] = 1
      
      income_index.append(meta_compensation_data[survey_row.income])
      income_data.append(int(survey_row.income))
      gender_data.append(survey_row.sex)
      age_data.append(int(survey_row.age))
      state_data.append(survey_row.state)
      location_data.append(int(survey_row.location))
      education_data.append(int(survey_row.educ))
      employment_data.append(int(survey_row.employment))
      reason_for_leaving_data.append(int(survey_row.why))
    elif survey_row.income is None:
      json_data_survey = sj.loads(survey_row.result)
      income_data.append(int(json_data_survey["income"]))
    else: 
      income_data.append(-1)

  regularized_income_data = [ (x - 2) for x in income_data ]
   

  output_file("/home/econ/utility/static/survey/lines.html", title="line plot example")
  hist, edges = np.histogram(income_data, density=False, bins=12)

  p = figure(title="Histogram of income", background_fill="#E8DDCB")
  p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
     fill_color="#036564", line_color="#033649")

  # customize axes
  xa, ya = p.axis
  xa.axis_label = 'Income of the survey participant'
  ya.axis_label = 'Number of responses'

  show(p)
  x1 = [0, 1, 2, 3, 4, 5,  6,  7, 8,   9, 10]
  y1 = [0, 8, 2, 4, 6, 9, 15, 18, 19, 25, 28]

  # EXERCISE: create two more data sets, x2, y2 and x3, y3, however
  # you want. Make sure the corresponding x and y data are the same length

  # specify and output static HTML file
  #output_file("/home/econ/utility/static/survey/scatter.html")

  # EXERCISE: Plot all the sets of points on different plots p1, p2, p3.
  # Try setting `color` (or `line_color`) and `alpha` (or `line_alpha`).
  # You can also set `line_dash` and `line_width`. One example is given.
  #p1 = figure(plot_width=300, plot_height=300)
  #p1.line(x1, y1, size=12, color="red", alpha=0.5)

  # create a figure
  #p4 = figure()

  # EXERCISE: add all the same renderers above, on this one plot

  return {'results' : db().select(db.survey_results.ALL), 'proportion': proportion}
