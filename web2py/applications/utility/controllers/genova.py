def index():
    if request.vars.feedback != None:
      request.workerid = request.vars.workerid 
      request.hitid = request.vars.hitid
      request.testing = False
      request.assid = request.vars.assignmentid 
      logging_response = log_action(request.vars.action_desc, other=request.vars.logs)
      #details = ",".join(request.vars.keys())
      #more_details = ",".join(request.keys())
      import json
      this_response = json.dumps({
	"logging_success": logging_response, 
	#"b": details, 
	"feedback_var_content": request.vars.feedback})
	#"d": request.workerid, 
	#"e": request.feedback, 
	#"f": more_details})
      db.commit()
      return this_response

    import time, random
    num_tags = request.pics_per_task * 5         # 5 tags per pic
    hit_num = hits_done()

    # Load this worker's genova progress.  I store progress in the
    # key-value store, as a triplet of the number of pictures used out
    # of each queue.
    progress_key = 'worker %s genova progress' % request.workerid
    progress = Storage(store_get(progress_key)
                       or dict(control=0, treatment=0, food=0))

    # Load and shuffle the pics
    random.seed(request.workerid + str(progress))
    genova_pics = load_genova_pics()
    random.shuffle(genova_pics.treatment)
    random.shuffle(genova_pics.control)
    #random.shuffle(genova_pics.food)
    
    # Choose 5 images from the 2 queues, depeding on how disagreeable we want it
    pics = []
#from random import shuffle
#x = [[i] for i in range(10)]
#shuffle(x)

# print x  gives  [[9], [2], [7], [0], [4], [5], [3], [1], [8], [6]]
# of course your results will vary
    picture_positions = range(1, request.pics_per_task+1)
    random.shuffle(picture_positions)
    for i in picture_positions:
        def add_pic(type):
            pics.append(genova_pics[type][progress[type]])
            progress[type] += 1

        #r = random.random()
        #if r < request.disagreeable/100.0:
        #    add_pic('treatment')
        #else:
        #    add_pic('control')
	# how about this
	if i <= request.disagreeable/20.0:
		add_pic('treatment')
	else: 
	    	add_pic('control')

	# how about this

    # If this is a hit submission, then let's finish!
    if request.vars.netprog != None:
        store_set(progress_key, progress)

	log('Somebody submitted some tags!')
        if int(request.vars.netprog) != progress.treatment + progress.control + progress.food:
            return 'Error.  You already submitted this hit!'

        othervars = dict()
        othervars['pics'] = pics
	othervars['disturbingness'] = request.vars.disturbingness
	#othervars['complete_training'] = request.vars.complete_training_time
	#othervars['leave_incomplete_training'] = request.vars.leave_training_time
	#othervars['enter_training'] = request.vars.training_start_time_stamp
        othervars['request_vars'] = request.vars
	othervars['activity_log'] = request.vars.activity_log

        # Calculate a random amount to pay them, pretending that they
        # only did so well.
        pay, good_tags = request.price, num_tags
	#randomize_pay(request.price, request.improbability_rate/100.0,num_tags)
        othervars['approved_price'] = pay
        othervars['approved_tags'] = good_tags

        bonus_message = '''
Thank you for working on our HIT today. We approved %d of your 25 tags, which earns you $%.2f of the possible $%.2f for this HIT.

By paying in bonus, we are able to approve every honest HIT you submit, and increase your Approval Rating.

We hope to see more of you in the ClearingHouse.''' % (good_tags, pay, request.price)

        hit_finished(bonus_amount=pay,
                     bonus_message=bonus_message,
                     extra_data=othervars) # Automatically exits this function

    # Now we know that we're displaying the HIT page.

    # If there aren't any photos available, make the worker wait.
    # Every `availability_period' seconds, photos will only be
    # available for the first `availability_rate' percent of them.
    availability_period = 43 * 60 # 43 minutes
    availability_rate = .28
    phase = (time.time() + 13) % availability_period
    #log('AVAIL: %.2f of %.2f: %s' % ((phase / availability_period), availability_rate,
    #                                 (phase / availability_period > availability_rate)))
    if (request.availability == 'low'
        and (phase / availability_period > availability_rate)):
        #log('AVAIL: delaying!!!')

        delay_time = int(availability_period - phase) + 2
        record_action('wait', other={'for':delay_time})
        response.view = 'genova/wait.html'
        return dict(hit_num=hit_num,
                    hits_left= request.work_limit - hit_num,
                    disagreeable=request.disagreeable,
                    training=request.training,
                    improbability_rate=request.improbability_rate,
                    availability=request.availability,
                    work_limit=request.work_limit,
                    until=delay_time)


    # Ok, let's proceed with the regular task!

    def random_offset(max_offset, seed):
        random.seed(seed)
        result = (random.random() - .5) * max_offset * 2
        random.seed()
        return result

    max_offset = 6 if request.improbability_rate < 90 else 2
    displayed_improbability_rate = request.improbability_rate \
        + random_offset(max_offset, now.day) \
        + random_offset(max_offset, now.hour)
    if request.testing:
        displayed_improbability_rate += random_offset(max_offset, now.second)
    displayed_improbability_rate = int(displayed_improbability_rate)
    displayed_improbability_rate = min(displayed_improbability_rate, 99)
    

    # Now we have taken a snippet of pics out of the original shuffled pics.
    # Display the form.
    log_action('with pic', other=pics)
    #log_action('test')
    return dict(hit_num=hit_num,
		study=request.study,
		hitid=request.hitid,
		workerid=request.workerid,
		assid=request.assid,
		phase=request.phase,
                hits_left= request.work_limit - hit_num,
		pics=pics,
		disagreeable=request.disagreeable,
                training=request.training,
                improbability_rate=displayed_improbability_rate,
                availability=request.availability,
                work_limit=request.work_limit,
                net_progress=progress.control + progress.treatment + progress.food)


def wait():
    hit_num = hits_done()
    delay_time = 3 * 60
    response.view = 'genova/wait.html'
    return dict(hit_num=hit_num,
                hits_left= request.work_limit - hit_num,
                disagreeable=request.disagreeable,
                training=request.training,
                improbability_rate=request.improbability_rate,
                availability=request.availability,
                work_limit=request.work_limit,
                until=delay_time)


def results():
    if len(request.args) > 0:
        studies = (db.studies(request.args[0]),)
    else:
        studies = db(db.studies.task=='pic').select()

    workers = db(db.actions.action=='submit', db.actions.study.belongs(studies)) \
        .select(db.actions.workerid, distinct=True)
    workers = [w.workerid for w in workers]

    def worker_results(workerid):
        rows = db((db.actions.action=='submit')
                  &(db.actions.workerid==workerid)) \
            .select(db.actions.other, db.actions.time, db.actions.condition,
                    orderby=~db.actions.time)
        return Storage(worker=workerid,
                       latest=rows[0].time,               
                       condition=db.conditions(rows[0].condition).json)

    # Copied this code from djangosnippets
    import re
    import cgi
    re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S|re.M|re.I)
    def plaintext2html(text, tabstop=4):
        def do_sub(m):
            c = m.groupdict()
            if c['htmlchars']:
                return cgi.escape(c['htmlchars'])
            if c['lineend']:
                return '<br>'
            elif c['space']:
                t = m.group().replace('\t', '&nbsp;'*tabstop)
                t = t.replace(' ', '&nbsp;')
                return t
            elif c['space'] == '\t':
                return ' '*tabstop;
            else:
                url = m.group('protocal')
                if url.startswith(' '):
                    prefix = ' '
                    url = url[1:]
                else:
                    prefix = ''
                last = m.groups()[-1]
                if last in ['\n', '\r', '\r\n']:
                    last = '<br>'
                return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
        return re.sub(re_string, do_sub, text)

    return dict(studies=studies,
                results=sorted([worker_results(w) for w in workers],
                               key=lambda w: now-w.latest),
                format=plaintext2html)


def preview(): return {}
def first_time():
    response.view = 'first_time.html'
    return {}

def echo():
#    return request.vars.value
  return "HELOOOOOOOOOO"
