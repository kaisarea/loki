def index():
    import time, random
    hit_num = hits_done()

    # Kludgey redirect for the first_time hit that pays $.50
    if not request.testing and db((db.actions.workerid == request.workerid)
                                  & (db.actions.action == 'finished')).count() < 1:
        response.view = 'first_time.html'
        return {}

    # Load this worker's genova progress.  I store progress in the
    # key-value store, as a triplet of the number of pictures used out
    # of each queue.
    progress_key = 'worker %s genova progress' % request.workerid
    progress = db.store(key=progress_key)
    if progress:                
        # If we've already got it in the DB
        progress = Storage(sj.loads(progress.value))
    else:
        # Else, initialize from zero
        progress = Storage(control=0, treatment=0, food=0)


    # Load and shuffle the pics
    random.seed(request.workerid + str(progress))
    genova_pics = define_genova_pics()
    random.shuffle(genova_pics.treatment)
    random.shuffle(genova_pics.control)
    #random.shuffle(genova_pics.food)
    
    # Choose 5 images from the 3 queues, depeding on how disagreeable we want it
    pics = []
    for i in range(request.pics_per_task):
        def add_pic(type):
            pics.append(genova_pics[type][progress[type]])
            progress[type] += 1

        r = random.random()
        if r < request.disagreeable/100.0:
            #r = random.random();
            #if r < .1:  add_pic('food')
            #else:       add_pic('treatment')
            add_pic('treatment')
        else:
            add_pic('control')


    # If this is a hit submission, then let's finish!
    if 'keyword_1' in request.vars:
        if int(request.vars.netprog) != progress.treatment + progress.control + progress.food:
            return 'Error.  You already submitted this hit!'

        othervars = dict()
        othervars['pics'] = pics
	othervars['disturbingness'] = request.vars.disturbingness
        othervars['request_vars'] = request.vars
        log_action('submit', othervars)
        db.store(key=progress_key).update_record(value=sj.dumps(progress))
        hit_finished() # Automatically exits this function

    # Now we know that we're displaying the HIT page.

    # If there aren't any photos available, make the worker wait.
    # Every `availability_period' seconds, photos will only be
    # available for the first `availability_rate' percent of them.
    availability_period = 60 * 1
    availability_rate = .08
    phase = (time.time() + 13) % availability_period
    #log('AVAIL: %.2f of %.2f: %s' % ((phase / availability_period), availability_rate,
    #                                 (phase / availability_period > availability_rate)))
    if (request.availability == 'low'
        and (phase / availability_period > availability_rate)):
        #log('AVAIL: delaying!!!')

        delay_time = int(availability_period - phase) + 2
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

    # Now we have taken a snippet of pics out of the original shuffled pics.
    # Display the form.
    log_action('with pic', other=pics)
    return dict(hit_num=hit_num,
                hits_left= request.work_limit - hit_num,
		pics=pics,
		disagreeable=request.disagreeable,
                training=request.training,
                improbability_rate=request.improbability_rate,
                availability=request.availability,
                work_limit=request.work_limit,
                net_progress=progress.control + progress.treatment + progress.food)


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

def track_error_submit():
    log_action('error submit', other=request.vars)
    log('Tracking Error submit! vars are %s' % sj.dumps(request.vars))
    return 'Good thanks for that'

def preview(): return {}
def first_time():
    response.view = 'first_time.html'
    return {}

def echo():
#    return request.vars.value
  return "HELOOOOOOOOOO"
