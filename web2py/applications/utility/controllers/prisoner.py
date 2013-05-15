def index():
    min_words = 100

    # Choose a random prisoner ordering for this worker
    import random
    hit_num = hits_done()
    prisoner_num = hit_num % len(prisoners)
    random.seed(request.workerid)
    random.shuffle(prisoners)
    prisoner = Storage(prisoners[prisoner_num])

    # Choose a crime
    random.seed(str(hit_num) + str(request.workerid))
    choose_from = sex_crimes if request.dimension1_treatment else crimes
    prisoner.crime = Storage(random.choice(choose_from))
    random.seed(now)

    othervars = {'hit_num' : hit_num,
                 'prisoner' : prisoner}

    # If this is a hit submission, then let's finish!
    letter = request.vars.letter_to_prisoner
    if letter:
        othervars['letter'] = letter
        log_action('submit', othervars)
        wordcount = (letter.split())
	if wordcount < min_words:
	    send_me_mail('Someone is trying to trick us! %s %s'
			 % (request.workerid, request.assignmentid))
        hit_finished() # Automatically exits this function
  
    # Otherwise, display the form
    log_action('with prisoner', othervars)
    return dict(min_words=100,
                prisoner=prisoner,
                treatment1=request.dimension1_treatment,
                treatment2=request.dimension2_treatment,
                treatment3=request.dimension3_treatment,
                treatment4=request.dimension4_treatment)


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
