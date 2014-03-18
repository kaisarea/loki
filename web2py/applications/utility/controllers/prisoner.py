def index():
    min_words = 100

    # Kludgey redirect for the first_time hit that pays $.50
    if not request.testing and db((db.actions.workerid == request.workerid)
                                  & (db.actions.action == 'finished')).count() < 1:
        response.view = 'first_time.html'
        return {}

    ###########################################################
    ##### Step 1: Set up all the experimental conditions  #####

    # # Each condition's values listed as: [Control, Experimental]
    # conditions = {'disagreeable'       : [False,    True],
    #               'training'           : [False,    True],
    #               'improbability_rate' : [94,      51],
    #               'work_limit'         : [90,       5]}

    # # Now let's set all these guys
    # for k,v in conditions.items():
    #     request[k] = v[1] if request.experimental_dimension == k else v[0]


    #############################################################
    ##### Ok... now let's get on with setting up this task  #####

    # Choose a random prisoner ordering for this worker
    import random
    hit_num = hits_done() - 1        # Subtract 1 for the first_time bonus
    if request.testing: hit_num = 0  # Cause otherwise it'll be -1
    random.seed(request.workerid)
    #prisoners = michelle_prisoners + meg_profiles + profiles + second_batch_of_profiles
    random.shuffle(prisoners)
    prisoner = Storage(prisoners[hit_num])   
    # This way with fixed random seed the worker will get the following
    # prisoner in a fixed randomized group of prisoners.
    # Will achieve both randomization and predictability.

    # Choose a crime
    random.seed(str(hit_num) + str(request.workerid))
    choose_from = sex_crimes if request.disagreeable else crimes
    prisoner.crime = Storage(random.choice(choose_from))
    random.seed(now) # Now reset the randomizer in case anything in
                     # the future needs actual random numbers

    othervars = {'prisoner' : prisoner}

    # If this is a hit submission, then let's finish!
    letter = request.vars.letter_to_prisoner
    if letter:
        othervars['letter'] = letter
#### This log_action function is storing the worker response to a database table
#### othervars is a way how to store additional information
        log_action('submit', othervars)
        wordcount = (letter.split())
	if wordcount < min_words:
	    send_me_mail('Someone is trying to trick us! %s %s'
			 % (request.workerid, request.assignmentid))
        hit_finished() # Automatically exits this function
  
    # Otherwise, display the form
    log_action('with prisoner', othervars)
    return dict(min_words=min_words,
                prisoner=prisoner,
                disagreeable=request.disagreeable,
                training=request.training,
                needs_to_train=hit_num == 0 or request.testing,
                hit_num = hit_num,
                hits_left = request.work_limit - hit_num - 1,
                #improbability=request.improbability,
                improbability_rate=request.improbability_rate,
                #inconstancy=request.inconstancy,
                #limit=request.limit,
                bonus_time='%d' % (request.pay_delay/60),
                work_limit=request.work_limit - 1)


def results():
    if len(request.args) > 0:
        studies = (db.studies(request.args[0]),)
    else:
        studies = db(db.studies.task=='prisoner').select()

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
                       condition=db.conditions(rows[0].condition).json,
                       letters=[sj.loads(row.other)['letter'] for row in rows])

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
