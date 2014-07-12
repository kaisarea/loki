# ============== Setting up a Fresh DB =============
def setup_db(study=None, force=False):
    log('Creating postgres indices')
    create_indices_on_postgres()
    load_ip_data(force)
    update_worker_info(force)
    if study:
        log('Populating runs for study %d' % study)
        populate_runs(study)

def create_indices_on_postgres():
    '''Creates a set of indices if they do not exist'''
    ## Edit this list of table columns to index
    ## The format is [('table', 'column')...]
    indices = [('actions', 'study'),
               ('actions', 'assid'),
               ('actions', 'hitid'),
               ('actions', 'time'),
               ('actions', 'workerid'),
               ('countries', 'code'),
               ('continents', 'code'),
               ('hits', 'study'),
               ('ips', 'from_ip'),
               ('ips', 'to_ip'),
               ('workers', 'workerid'),
               ('store', 'key'),
               ('condition_choices', 'workerid'),
               ('condition_choices', 'study'),
               ('condition_choices', 'phase')]
    for table, column in indices:
        index_exists = db.executesql("select count(*) from pg_class where relname='%s_%s_idx';"
                                     % (table, column))[0][0] == 1
        if not index_exists:
            db.executesql('create index %s_%s_idx on %s (%s);'
                          % (table, column, table, column))
        db.commit()

# ============== Migration Help =============
#import hashlib
#log('Using db %s %s' % (database, hashlib.md5(database).hexdigest()))
def db_hash(): 
    import cPickle, hashlib
    return hashlib.md5(database).hexdigest()

def get_migrate_status(table_name):
    import cPickle, hashlib
    f = open('applications/utility/databases/%s_%s.table'
             % (hashlib.md5(database).hexdigest(),
                table_name),
             'r')
    result = cPickle.load(f)
    f.close()
    return result

def save_migrate_status(table_name, status):
    import cPickle, hashlib
    f = open('applications/utility/databases/%s_%s.table'
             % (hashlib.md5(database).hexdigest(),
                table_name),
             'w')
    cPickle.dump(status, f)
    f.close()
    print 'saved'

def del_migrate_column(table_name, column_name):
    a = get_migrate_status(table_name)
    del a[column_name]
    save_migrate_status(table_name, a)


def reload_model(name):
    '''THIS DOES NOT WORK'''
    execfile(request.folder + '/models/' + name + '.py')
    return 'THIS DOES NOT WORK'


# ============== Database Maintenance Helpers =============
def clean_bonus_queue(sloppy=False):
    for b in db(db.bonus_queue.id > 0).select():
        turks_ass = turk.get_assignments_for_hit(b.hitid)
        if len(turks_ass) != 1: continue
        turks_ass = turks_ass[0]
        turks_assid = turk.get(turks_ass, 'AssignmentId')
        turks_ass_status = turk.get(turks_ass, 'AssignmentStatus')
        bonus_ass_status = turk.assignment_status(b.assid, b.hitid)
        turk_ass_ok = (turks_ass_status == u'Approved')
        if sloppy:
            turk_ass_ok = turk_ass_ok or (turks_ass_status == u'Submitted')
        if turk_ass_ok \
                and turks_assid != b.assid \
                and not bonus_ass_status:
            # Then the item we have in the bonus queue is no good.
            log('BAD ASS:  %s' % b.assid)
            log('GOOD ASS: %s, %s' % (turks_assid, turks_ass_status))
            del db.bonus_queue[b.id]
        else:
            if turks_assid == b.assid:
                reason = 'the two assids (bonus v. turk) are a MATCH'
            elif bonus_ass_status:
                reason = 'bonus_ass exists with a status of %s' % bonus_ass_status
            elif not (turks_ass_status == u'Approved'
                      or turks_ass_status == u'Submitted'):
                reason = 'turks_ass_status is %s' % turks_ass_status
            else:
                reason = '... er actually we got a bigger problem than that'
            log("..ok cuz " + reason)
    log('#### Run db.commit() now!!!!!!! ####')

def populate_ass_bonuses():
    query = (db.assignments.paid == -1) & (db.assignments.assid != 'None')
    last_ass = db(query).select(db.assignments.ALL,
                                limitby=(0,1),
                                orderby=~db.assignments.id)[0].id

    for ass in db(query).select(orderby=db.assignments.id):
        bonus = turk.bonus_total(ass.assid)
        print ('%s/%s Bonus for %s is %s'
               % (ass.id, last_ass, ass.assid, bonus))
        ass.update_record(paid = bonus)
        db.commit()

def update_ass_conditions():
    for i,ass in enumerate(db().select(db.assignments.ALL)):
        if ass.assid:
            actions = db(db.actions.assid == ass.assid) \
                .select(db.actions.condition, distinct=True)
            if len(actions) == 1 and actions[0].condition:
                print 'Updating', ass.assid, actions[0].condition
                ass.update_record(condition=actions[0].condition)
            else:
                print 'foo', len(actions), actions[0].condition if len(actions) == 1 else ''


# ============== Database Consistency Checks =============
def hits_with_multiple_finishes(study=''):
    study_clause = ('and actions.study=%d' % study.id) if study else ''
    query = """select actions.study, actions.hitid, count(actions.hitid)
               from actions where actions.action = 'finished' %s
               group by actions.study, actions.hitid
               having count(*) > 1
            """ % study_clause
    return db.executesql(query)

def hits_with_multiple_finishes2(study=None):
    study = (db.actions.study == study) if study else (db.actions.study > 0)
    return db((db.actions.action == 'finished') & study).select(
        db.actions.study, db.actions.hitid, db.actions.hitid.count(),
        groupby=(db.actions.study, db.actions.hitid),
        having=(db.actions.hitid.count() > 1)
        )

def hits_with_multiple_asses(study=None):
    study_clause = ('and actions.study=%d' % study.id) if study else ''

    query = """select actions.study, actions.hitid, count(distinct(actions.assid))
               from actions where assid != 'ASSIGNMENT_ID_NOT_AVAILABLE' %s
               group by actions.study, actions.hitid
               having count(distinct(actions.assid)) > 1
            """ % study_clause
    return db.executesql(query)

def asses_with_multiple_finishes(study=None):
    study_clause = ('and actions.study=%d' % study.id) if study else ''
    query = """select actions.study, actions.assid, count(*)
               from actions where actions.action = 'finished' %s
               group by actions.study, actions.assid
               having count(*) > 1
            """ % study_clause
    return db.executesql(query)

def asses_with_multiple_workers(study=None):
    study_clause = ('and actions.study=%d' % study.id) if study else ''

    query = """select actions.study, actions.assid, count(distinct(actions.workerid))
               from actions where assid != 'ASSIGNMENT_ID_NOT_AVAILABLE' %s
               group by actions.study, actions.assid
               having count(distinct(actions.workerid)) > 1
            """ % study_clause
    return db.executesql(query)

def asses_with_multiple_hits(study=None):
    study_clause = ('and actions.study=%d' % study.id) if study else ''

    query = """select actions.study, actions.assid, count(distinct(actions.hitid))
               from actions where assid != 'ASSIGNMENT_ID_NOT_AVAILABLE' %s
               group by actions.study, actions.assid
               having count(distinct(actions.hitid)) > 1
            """ % study_clause
    return db.executesql(query)

def thingthings_with_multiple_things(thing1, thing2, thing3, study):
    study_clause = ('and actions.study=%d' % study.id) if study else ''

    query = """select actions.study, actions.%(thing1)sid, actions.%(thing2)sid, count(distinct(actions.%(thing3)sid))
               from actions where workerid != 'WORKER_ID_NOT_AVAILABLE' and assid != 'ASSIGNMENT_ID_NOT_AVAILABLE' %(study)s
               group by actions.study, actions.%(thing1)sid, actions.%(thing2)sid
               having count(distinct(actions.%(thing3)sid)) > 1
            """ % {'study': study_clause,
                   'thing1': thing1,
                   'thing2': thing2,
                   'thing3': thing3}
    return db.executesql(query)

def workerhits_with_multiple_asses(study=None):
    return thingthings_with_multiple_things('worker', 'hit', 'ass', study)
def asshits_with_multiple_workers(study=None):
    return thingthings_with_multiple_things('ass', 'hit', 'worker', study)
def workerasses_with_multiple_hits(study=None):
    return thingthings_with_multiple_things('worker', 'ass', 'hit', study)

all_consistency_funcs = '''hits_with_multiple_finishes
    hits_with_multiple_asses
    asses_with_multiple_finishes
    asses_with_multiple_workers
    asses_with_multiple_hits
    workerhits_with_multiple_asses
    asshits_with_multiple_workers
    workerasses_with_multiple_hits'''.split()

def check_database_constraints(study=None):
    for func in all_consistency_funcs:
        exec('tmp = %s(study)' % func)
        print ('Found %s %s' % (len(tmp), func.replace('_', ' ')))

# ============== From When Shit Hit Fans =============
def pay_worker_extra(workerid, amount, reason):
    '''	Finds a recent assignment that the worker completed and pays                         
    him with it'''
    ass = db((db.actions.workerid==workerid)
             &(db.actions.action=='finished')).select(orderby=~db.actions.time,
                                                      limitby=(0,1)).first()
    if not ass or not ass.assid:
        log('No assignment for worker %s' % workerid)
        return

    return turk.give_bonus(ass.assid, workerid, amount, reason)

def add_hits_log_creation_dates():
#     for hit in db().select(db.hits_log.ALL):
#         hit.update_record(xmlbody = hit.xmlbody.replace('\n','')
#                           .replace('\t',''),
#                           creation_time)
    pass
