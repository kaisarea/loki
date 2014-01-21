def index():
    if request.disagreeable:
        pics = pics_treatment
    else:
        pics = pics_control
    pics = [Storage(p) for p in pics]

    # Choose a random picture ordering for this worker
    import random
    random.seed(request.workerid)
    random.shuffle(pics)        # Shuffles all the pics in a set way

    # Now the pictures are shuffled.  Let's give the worker a set of
    # pictures.
    hit_num = hits_done()
    first_pic = hit_num * request.pics_per_task # The first of n pics
    pics = pics[first_pic : first_pic + request.pics_per_task]
    othervars = dict()
    
    # Now we have taken a snippet of pics out of the original shuffled pics
    # If this is a hit submission, then let's finish!
    image_tag = request.vars.image_tag
    if image_tag:
        #othervars['review'] = review
        othervars['tags'] = request.vars.image_tag
        log_action('submit', othervars)
        hit_finished() # Automatically exits this function
  
    # Otherwise, display the form
    log_action('with pic')
    return dict(hit_count = hit_num,
		pics=pics,
		disagreeable=request.disagreeable,
                training=request.training,
                improbability_rate=request.improbability_rate,
                work_limit=request.work_limit)


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

def preview(): return {}
def first_time():
    response.view = 'first_time.html'
    return {}

def echo():
#    return request.vars.value
  return "HELOOOOOOOOOO"
