def index():
    min_words = 100
    if request.disagreeable:
        pics = pics_treatment
    else:
        pics = pics_control
    # Choose a random prisoner ordering for this worker
    import random
    hit_num = hits_done()
    pics_num = hit_num % len(pics)
    random.seed(request.workerid)
    random.shuffle(pics)
    pic = Storage(pics[pics_num])

    othervars = {'hit_num' : hit_num,
                 'pic' : pic}

    # If this is a hit submission, then let's finish!
    review = request.vars.review
    if review:
        othervars['review'] = review
        log_action('submit', othervars)
        wordcount = (review.split())
	if wordcount < min_words:
	    send_me_mail('Someone is trying to trick us! %s %s'
			 % (request.workerid, request.assignmentid))
        hit_finished() # Automatically exits this function
  
    # Otherwise, display the form
    log_action('with pic', othervars)
    return dict(min_words=100,
                pic=pic,
		disagreeable=request.disagreeable,
                training=request.training,
                improbability=request.improbability,
                improbability_rate=request.improbability_rate,
                inconstancy=request.inconstancy,
                limit=request.limit,
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
