def index():
    import time
    hit_num = hits_done()

    # Load this worker's genova progress
    key = 'worker %s genova progress' % request.workerid
    progress = db.store(key=key)
    if progress:
        progress = Storage(sj.loads(progress.value))
    else:
        log('There was nothing of key %s' % key)
        progress = Storage(control=0, treatment=0, food=0)

    # Set shuffle seed
    import random
    random.seed(request.workerid)

    # Load and shuffle the pics
    genova_pics = cache.ram('genova_pics', lambda: define_genova_pics(),
                            time_expire=60)
    random.shuffle(genova_pics.treatment)
    random.shuffle(genova_pics.control)
    random.shuffle(genova_pics.food)
    
    # Choose some disagreeable and control images
    pics = []

    def add_pic(type):
        pics.append(genova_pics[type][progress[type]])
        progress[type] += 1

    for i in range(request.pics_per_task):
        r = random.random()
        if r < request.disagreeable/100.0:
            log('r=%s so disagreeable'%r)
            r = random.random();
            if r < .1:
                log('    ...r=%s so food'%r)
                add_pic('food')
            else:
                log('    ...r=%s so not food'%r)
                add_pic('treatment')
        else:
            log('r=%s so control'%r)
            add_pic('control')


    # If this is a hit submission, then let's finish!
    image_tag = request.vars.image_tag
    if image_tag:
        if int(request.vars.netprog) != progress.treatment + progress.control + progress.food:
            return 'Error.  You already submitted this hit!'

        othervars = dict()
        othervars['pics'] = pics
        othervars['tags'] = request.vars.image_tag
	othervars['disturbingness'] = request.vars.disturbingness
        othervars['request_vars'] = request.vars
        log_action('submit', othervars)
        db.store(key=key).update_record(value=sj.dumps(progress))
        hit_finished() # Automatically exits this function

    # Now we know that we're displaying the HIT page.

    # If there aren't any photos available, make the worker wait.
    # Every `availability_period' seconds, photos will only be
    # available for the first `availability_rate' percent of them.
    availability_period = 60 * 1
    availability_rate = .08
    phase = (time.time() + 13) % availability_period
    log('AVAIL: %.2f of %.2f: %s' % ((phase / availability_period), availability_rate,
                                     (phase / availability_period > availability_rate)))
    if (request.availability == 'low'
        and (phase / availability_period > availability_rate)):
        log('AVAIL: delaying!!!')

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
