from datetime import datetime
import sys
import traceback

# ============== Debugging the Scheduler =============
def scheduler_errors(N=10):
    errors = db(db.scheduler_run.status=='FAILED').select(limitby=(0,N),
                                                          orderby=~db.scheduler_run.id)
    for error in errors:
        print error.id, db.scheduler_task[error.scheduler_task].task_name, error.traceback
    print ('When done, you can run clear_scheduler_errors().')
def clear_scheduler_errors():
    db(db.scheduler_run.status=='FAILED').delete()
    db(db.scheduler_task.status=='FAILED').delete()
    db.commit()
def open_scheduler_tasks(task_name=None):
    query = db.scheduler_task.status.belongs(('QUEUED',
                                              'ASSIGNED',
                                              'RUNNING',
                                              'ACTIVE'))
    if task_name:
        query &= db.scheduler_task.task_name == task_name
    return db(query).select()
def log_scheduler_errors(f):
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            debug_t('Error in %s! %s\nRun scheduler_errors() at ./shell for more info' % (f.__name__,e))
            raise
    return wrapper


# ============== Task Definitions =============
@log_scheduler_errors
def send_email(to, subject, message):
    debug_t('Sending email now from within the scheduler!')
    if True:   # Use sendmail
        SENDMAIL = "/usr/sbin/sendmail" # sendmail location
        import os
        p = os.popen("%s -t" % SENDMAIL, "w")
        p.write("To: " + to + "\n")
        p.write("Subject: " + subject + "\n")
        p.write("\n") # blank line separating headers from body
        p.write(message)
        p.write("\n")
        status = p.close()
        if status != 0:
            #print "Sendmail exit status", sts
            pass

    else:   # Use gmail
        from gluon.tools import Mail
        mail = Mail()
        mail.settings.server = 'smtp.gmail.com:587'
        mail.settings.sender = 'mturk@utiliscope.net'
        mail.settings.login = 'mturk@utiliscope.net:byebyesky'
        mail.send(to, subject, message)
    debug_t('Sent!')

@log_scheduler_errors
def message_turk_worker(worker, subject_line, message_body):
    turk.message_worker(worker, subject_line, message_body)


# Initial Setup, Periodic Maintenance
@log_scheduler_errors
def periodic_maintenance():
    setup_db()


@log_scheduler_errors
def refresh_hit_status():
    hits = db(db.hits.status.belongs(('open', 'getting done'))).select()
    db.rollback()
    failed_refreshes = []
    for hit in hits:
        try:
            xml = turk.get_hit(hit.hitid)
        except TurkAPIError as e:
            failed_refreshes.append(hit.hitid)
            continue

        status = turk.is_valid(xml) and turk.get(xml,'HITStatus')
        if not status:
            continue

        # status starts out as 'open' or 'getting done' and we'll record it as:
        #
        #  [mturk status] -> [what we call it]
        #  Assignable     -> open
        #  Unassignable   -> getting done
        #  Reviewable     -> closed
        #  Reviewing      -> closed

        newstatus = hit.status
        #log("refreshing %s %s" % (hitid, status))
        if status == u'Assignable':
            newstatus = 'open'
        if status == u'Unassignable':
            newstatus = 'getting done'
        elif status == u'Reviewable' or status == u'Reviewing':
            # Unassignable happens when someone is doing it now
            # The only other option is Assignable
            newstatus = 'closed'
        record_hit_data(hitid=hit.hitid, status=newstatus, xmlcache=xml.toxml())
    if failed_refreshes:
        debug_t('MTurk API went bogus for refreshing %s/%s hits',
                len(failed_refreshes), len(hits))


# ============== Approving Hits and Paying People Bonus =============
@log_scheduler_errors
def process_bonus_queue():
    '''
    HOW THE BONUS QUEUE WORKS:
    For each item in the queue:
      - Approve the assignment (if it has an assid and hitid)
      - Then bonus the worker with the bonus amount
      - It will automatically find an existing assid/hitid to bonus if none is specified
    '''
    try:
        for row in db().select(db.bonus_queue.ALL):
            # Skip workers that we aren't ready for yet
            if row.delay and row.delay > 0:
                action = db.actions(assid=row.assid, action='finished')
                if not action:
                    logger_t.error('No finish action on bonus %s' % row.assid);
                elif (datetime.now() - action.time).total_seconds() < row.delay:
                    continue

            try:
                if row.assid and row.hitid:
                    try_approve_assignment(row.assid, row.hitid)
                
                # This will automatically look up a hitid and assid if
                # none is specified
                pay_worker(row.worker, float(row.amount), row.reason,
                                    row.assid, row.hitid)

                debug_t('Success!  Deleting row.')
                db(db.bonus_queue.assid == row.assid).delete()
                if False:
                    worker = db(db.workers.workerid == row.worker).select()[0]
                    worker.update_record(bonus_paid=worker.bonus_paid + float(row.amount))
                db.commit()
            except TurkAPIError as e:
                logger_t.error(str(e.value))
    except KeyboardInterrupt:
        debug_t('Quitting.')
        db.rollback()
        raise
    except Exception as e:
        logger_t.error('BAD EXCEPTION!!! How did this happen? letz rollback and die... ' + str(e))
        try:
            db.rollback()
        except Exception as e:
            logger_t.error('Got an exception handling even THAT exception: ' + str(e.value))
        raise
    #debug('we are done with bonus queue')

def try_approve_assignment(assid, hitid):
    ass_status = turk.assignment_status(assid, hitid)
    debug_t('Approving ass %s of status %s' %
            (assid, ass_status))

    if len(turk.get_assignments_for_hit(hitid)) == 0:
        raise TurkAPIError("...mturk hasn\'t updated their db yet")

    # Approve the assignment, but only if it's "submitted"
    if ass_status == u'Submitted':
        turk.approve_assignment(assid)

def lookup_recent_assignment(workerid, assid=None, hitid=None):
    if hitid and assid: return (assid, hitid)

    if not (assid and hitid):
        # Default to assid and hitid if specified
        assid_query = ((db.actions.assid == assid)
                       if assid else
                       ((db.actions.assid != 'ASSIGNMENT_ID_NOT_AVAILABLE')
                        & (db.actions.assid != None)))

        hitid_query = ((db.actions.hitid == hitid)
                       if hitid else
                       (db.actions.hitid != None))

        # Look up a new, recent action
        row = db(assid_query & hitid_query & (db.actions.workerid == workerid)
                 & (db.actions.action == 'finished')) \
            .select(db.actions.assid, db.actions.hitid,
                    limitby=(0,1), orderby=~db.actions.time).first()
        if not row:
            raise AssignmentNotFound("Failed to find a hitid/assid for worker %s in our PostgreSQL database." % workerid)

        return row.assid, row.hitid



def pay_worker(workerid, bonusamt, reason, assid=None, hitid=None):
    """ Finds a recent completed assignment and hit (if not specified), and
        pays the worker with it.
    """
    try:
        (assid, hitid) = lookup_recent_assignment(workerid, assid, hitid)
    except:
        except_type, except_class, tb = sys.exc_info()
        exc_info = (except_type, except_class, traceback.extract_tb(tb))
        #human_time_snapshot = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        error_type = str(exc_info[0])
        error_message = exc_info[1].message
        error_file = exc_info[2][0][0]
        error_line_number = exc_info[2][0][1]
        error_function = exc_info[2][0][2]
        error_command = exc_info[2][0][3]
        db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', error_message=error_type+error_command)
        db.commit()
        print("Assignment ID not found in the utiliscope database, this is a FAILED payment")
        return
    time_stamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    try:
        current_assignment_status = turk.assignment_status(assid, hitid)
        # we are getting the assignment status, could be None, Approved, Submitted or Rejected
        # in theory what could happen is that it's None or it could even happen that Turk does not recognized the HIT ID
        # that is used to query the API, if we fail here I don't quite see why would we not be able to pay
        # unless it's the case that we can bonus only Approved assignment
    except:
        except_type, except_class, tb = sys.exc_info()
        exc_info = (except_type, except_class, traceback.extract_tb(tb))
        #human_time_snapshot = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        error_type = str(exc_info[0])
        error_message = exc_info[1].message
        error_file = exc_info[2][0][0]
        error_line_number = exc_info[2][0][1]
        error_function = exc_info[2][0][2]
        error_command = exc_info[2][0][3]
        db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', error_message=error_type+error_message)
        db.commit()
        print("We were not able to ascertain the status of the latest available assignment, this thwarts our efforts to bonus it")
        print((error_command, error_function, error_line_number, error_file, error_message, error_type))
        return

    if current_assignment_status != u'Approved':
        print("This assignment is not approved so I guess we're not able to bonus it?")
        db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', error_message='Trying to bonus a hit that isn\'t ready!  it is %s'
                           % turk.assignment_status(assid, hitid))
        db.commit()
        raise TurkAPIError('Trying to bonus a hit that isn\'t ready!  it is %s'
                           % turk.assignment_status(assid, hitid))

    # Now let's give it a bonus
    if float(bonusamt) > 0.0:
        try:
            payment_respose = turk.give_bonus(assid, workerid, float(bonusamt), reason)
            print(payment_response)
            # Now how can we tell that this failed and how exactly did it fail?
            # payment_response should some XML where there is either True when success and False when fail, so we need to extract that
            # currently this is not being check at all but rather assignment is being updated and then total bonus of the worker
            # are looked at but those could fail for different reasons and this would provide a false positive in terms 
            # of looking for failed payments
        except:
            except_type, except_class, tb = sys.exc_info()
            exc_info = (except_type, except_class, traceback.extract_tb(tb))
            #human_time_snapshot = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            error_type = str(exc_info[0])
            error_message = exc_info[1].message
            error_file = exc_info[2][0][0]
            error_line_number = exc_info[2][0][1]
            error_function = exc_info[2][0][2]
            error_command = exc_info[2][0][3]
            db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', error_message=error_type+error_message)
            db.commit()
            return

    # Update the assignment log and verify everything worked
    try:
        update_ass_from_mturk(hitid)
    except:
        except_type, except_class, tb = sys.exc_info()
        exc_info = (except_type, except_class, traceback.extract_tb(tb))
            #human_time_snapshot = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        error_type = str(exc_info[0])
        error_message = exc_info[1].message
        error_file = exc_info[2][0][0]
        error_line_number = exc_info[2][0][1]
        error_function = exc_info[2][0][2]
        error_command = exc_info[2][0][3]
        db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', error_message=error_type+error_message)
        db.commit()
        return

    try:
        total_bonus_given_to_worker = turk.bonus_total(assid)
    except:
        except_type, except_class, tb = sys.exc_info()
        exc_info = (except_type, except_class, traceback.extract_tb(tb))
            #human_time_snapshot = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        error_type = str(exc_info[0])
        error_message = exc_info[1].message
        error_file = exc_info[2][0][0]
        error_line_number = exc_info[2][0][1]
        error_function = exc_info[2][0][2]
        error_command = exc_info[2][0][3]
        db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', error_message=error_type+error_message)
        db.commit()
        print("There was an error during attempted payment, check the database for more info")
        return

    try:
        this_assignment_status = turk.assignment_status(assid, hitid)
    except:
        except_type, except_class, tb = sys.exc_info()
        exc_info = (except_type, except_class, traceback.extract_tb(tb))
            #human_time_snapshot = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        error_type = str(exc_info[0])
        error_message = exc_info[1].message
        error_file = exc_info[2][0][0]
        error_line_number = exc_info[2][0][1]
        error_function = exc_info[2][0][2]
        error_command = exc_info[2][0][3]
        db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', error_message=error_type+error_message)
        db.commit()
        print("There was an error during attempted payment, check the database for more info")
        return

    if this_assignment_status != u'Approved' or total_bonus_given_to_worker < float(bonusamt) - .001:
        db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, 
                                workerid=workerid, status='FAILED', 
                                error_message='Bonus did\'t work! We have %s and %s<%s' % (turk.assignment_status(assid, hitid), turk.bonus_total(assid), float(bonusamt)))
        print('Bonus did\'t work! We have %s and %s<%s' % (turk.assignment_status(assid, hitid), turk.bonus_total(assid), float(bonusamt)))
        return
    db.side_payments.insert(payment_amount=bonusamt, purpose=reason, associated_assid=assid, associated_hitid=hitid, created_at=time_stamp, workerid=workerid, status='SUCCESS')
    db.commit()

def update_ass_from_mturk(hitid):
    # Get the assignments for this from mturk
    asses = turk.get_assignments_for_hit(hitid)

    # Go through each assignment
    for ass in asses:
        assid = turk.get(ass, 'AssignmentId')
        bonus_amount = turk.bonus_total(assid)

        update_ass(assid,
                   hitid=turk.get(ass, 'HITId'),
                   workerid=turk.get(ass, 'WorkerId'),
                   status=turk.get(ass, 'AssignmentStatus'),
                   paid = bonus_amount,
                   xmlcache=ass.toxml())
    
def give_bonus_up_to(assid, workerid, bonusamt, reason):
    delta = turk.give_bonus_up_to(assid, workerid, float(bonusamt), reason)
    ass = db.assignments(assid=assid)
    soft_assert(ass, 'WTF no ass???')
    ass.update_record(paid = float(ass.paid) + float(delta))
    db.commit()



# ============== Launch a Whole Study =============
def schedule_hit(launch_date, study, task, othervars):
    def varnum(array, index): return array[index] if len(array) > index else None
    db.hits.insert(status = 'unlaunched',
                   launch_date = launch_date,
                   study = study,
                   task = task,
                   othervars = sj.dumps(othervars))
    db.commit()


def launch_test_study(task, num_hits=1, nonce=None):
    study_name = 'teststudy %s' % task
    if nonce: study_name += ' %s' % nonce
    launch_study(num_hits, task, study_name, " ... test ...")


def launch_pinger(num_hits, seconds_until_complete, study_id):
    time = datetime.now()
    delay = timedelta(seconds = float(seconds_until_complete) / num_hits)
    log('Launching %s hits, with %s in between, for a total of %.2f hours'
        % (num_hits, delay, seconds_until_complete / 60.0 / 60.0))
    for i in range(num_hits):
        time = time + delay
        #log('Scheduling at %s' % time)
        schedule_hit(time, study_id, db.studies(study_id).task, {})
    db.commit()

def launch_study(num_hits, task, name, description, hit_params=None):
    # Hit params default to what's in options, but can be overridden here
    params = task in options and 'hit_params' in options[task] and options[task]['hit_params'] or {}
    params.update(hit_params or {})

    conditions = options[task]
    study = get_or_make_one(db.studies.name == name,
                            db.studies,
                            {'name' : name,
                             'launch_date' : datetime.now(),
                             'task' : task})
    study.update_record(description = description,
                        conditions = sj.dumps(conditions, sort_keys=True),
                        hit_params = sj.dumps(params, sort_keys=True))

    for i in range(num_hits):
        schedule_hit(datetime.now(), study.id, task, {})
    db.commit()


# ============== Launch a Eenie-Weenie Single Hit =============
@log_scheduler_errors
def process_launch_queue():
    for hit in db((db.hits.status == 'unlaunched')
                  & (db.hits.launch_date < datetime.now())).select():
        launch_hit(hit)
def launch_hit(hit):
    try:
        # Check db.hits for the hit
        # if it doesn't exist or is launched, throw an error.
        # otherwise, create it and update hits and hits_log

        # Make sure it's fresh (dunno if this actually helps)
        hit = db.hits[hit.id]
        assert hit.status == 'unlaunched', 'Hit is already launched!'

        # Get the hit parameters, which default to Mystery Task
        params = Storage(mystery_task_params)
        assert hit.study.hit_params, 'No parameters for this hit!'
        params.update(sj.loads(hit.study.hit_params))

        # Give it a url
        params['question'] = turk.external_question(
            hit_serve_url(hit.task), iframe_height)
        
        # Launch the hit
        result = turk.create_hit(params.question,
                                 params.title,
                                 params.description,
                                 params.keywords,
                                 params.ass_duration,
                                 params.lifetime,
                                 params.assignments,
                                 params.reward,
                                 params.tag,
                                 params.block_india)

        hitid = turk.get(result, 'HITId')
        if not hitid: raise TurkAPIError('LOST A HIT! This shouldn\'t happen! check this out.')

        debug_t('Launched hit %s' % hitid)

        # Get this into the hits database quick, in case future calls fail
        hit.update_record(hitid=hitid, xmlcache='fail! not inserted yet', status='open')
        db.commit()

        # Now let's get the xml result, and put the rest of this into the log
        xml = turk.get_hit(hitid)
        record_hit_data(hitid=hitid,
                        #creation_time=turk.hit_creation(xml),
                        xmlcache=xml.toxml())

    except TurkAPIError as e:
        debug_t('Pooh! Launching hit id %s failed with:\n\t%s' \
                    % (hit.id, e.value))

mystery_task_params = Storage(
        {'title' : 'Mystery Task (BONUS)',
         'description' : 'Preview to see the task and how much it pays.  We continually change the payments and tasks for these hits, so check back often.  All payments are in bonus.  You will be paid within minutes of finishing the HIT.',
         'keywords' : 'mystery task, bonus, toomim',
         'ass_duration' : ass_duration,
         'lifetime' : hit_lifetime,
         'assignments' : 1,
         'reward' : 0.0,
         'tag' : None,
         'block_india' : True})


# ============== Junk Code (will delete soon) =============
def process_tickets():
    return "NO! Don't use this."

    def get_table_row(table, row_header):
        # Look for the row with `header' in the first string of
        # the first TD of the row
        for row in table.components:
            #print row.components[0].components[0]
            if row.components[0].components[0] == row_header:
                return row #.components[2].components[0].components[0]
        return None

    def get_beautify_key_value(beautify, key):
        r = get_table_row(beautify.components[0], key)
        if r:
            return r.components[2].components[0]
        return None

    def has_live_get_var(error):
        get_vars = get_beautify_key_value(e.snapshot['request'], 'get_vars')
        if not get_vars: return False
        return get_beautify_key_value(get_vars, 'live')
        
    def find_hitid(error):
        get_vars = get_beautify_key_value(error.snapshot['request'], 'get_vars')
        if not get_vars:
            send_me_mail('Crap, no get_vars in this guy!\n\n %s error')
        hitid = get_beautify_key_value(get_vars, 'hitId')
        if not (hitid and len(hitid.components) == 1):
            send_me_mail('Crap, no hitid in this guy!\n\n %s error')
        return hitid.components[0]
    def is_sandbox(error):
        sandboxp = get_beautify_key_value(e.snapshot['request'], 'sandboxp')
        if not sandboxp or 'components' not in sandboxp or len(components) < 1:
            debug_t('This shouldn\'t happen! in process_tickets()')
            return False
        s = sandboxp.components[0]
        if not (s == 'False' or s == 'True'):
            debug_t('This shouldn\'t happen either! in process_tickets()')
            return false
        return s == 'True'

    if True:
        import os, stat, time
        from gluon.restricted import RestrictedError
        path='applications/utility/errors/'

        last_run = store_get('last_process_tickets_time') or 0.3
        this_run = time.time()

        recent_files = [x for x in os.listdir(path)
                        if os.path.getmtime(path + x) > last_run]

        for file in recent_files:
            debug_t('Trying error file %s' % file)
            e=RestrictedError()
            e.load(request, 'utility', file)

            # Ok, let's see if this was a live one
            if has_live_get_var(e) and not is_sandbox(e):
                debug_t('This error has a live!  Dealing with it now.')
                hitid = find_hitid(e)
                url = ('http://%s:%s/admin/default/ticket/utility/%s'
                       % (server_url, server_port, file))
                send_me_mail("There was an error in your mturk study!!!\nGo check it out at %s"
                             % url)
                try:
                    debug_t('Expiring hit %s' % hitid)
                    result = turk.expire_hit(hitid)
                    # result.toprettyxml().replace('\t', '   ')
                    debug_t('Expired this hit.')
                except TurkAPIError as e:
                    debug_t("Couldn't expire it. Maybe it was already done.  Error was: %s"
                            % e)
        store_set('last_process_tickets_time', this_run)
        db.commit()
#     except Exception as e:
#         debug_t('Got error when processing tickets! %s' % e)

# def beautify_table_to_dict(b):
#     from gluon.html import BEAUTIFY
#     for row in b.components[0].components:
#         key = row.components[0].components[0]
#         value = row.components[2].components[0]
#         if isinstance(value, BEAUTIFY):

