def index():
    min_words = 100

    # First -- if this is a hit submission, then let's finish!
    letter = request.vars.letter_to_prisoner
    if letter:
	log_action('submit', {'letter' : letter})
        wordcount = (letter.split())
	if wordcount < min_words:
	    send_me_mail('Someone is trying to trick us! %s %s'
			 % (request.workerid, request.assignmentid))
        hit_finished() # Automatically exits this function
  
    # Choose a random prisoner ordering for this worker
    import random
    hit_num = hits_done()
    prisoner_num = hit_num % len(prisoners)
    random.seed(request.workerid)
    random.shuffle(prisoners)
    prisoner = Storage(prisoners[prisoner_num])

    # Choose a crime
    random.seed(hit_num)
    choose_from = sex_crimes if request.sexy else crimes
    prisoner.crime = Storage(random.choice(choose_from))

    return dict(min_words=100,
                prisoner=prisoner,
                sexy=request.sexy)


def index_old():
    # First -- if this is a hit submission, then let's finish!
    if request.vars.prisoner_name:
        wordcount = len(request.vars.worker_message.split())
        q = ((db.worker_response.worker_id==request.vars.workerid)
             & (db.worker_response.prisoner_name==request.vars.prisoner_name))
        db(q).update(message=request.vars.worker_message,
                     price=request.vars.price,
                     response_length=wordcount)
        #log('when finishing, live is %s %s' % (request.live, request.vars.live))
        hit_finished()
        return # Technically not necessary after hit_finished()

    # Ok, then we are just displaying the HIT
    min_words = 100

    if not db.worker_response(worker_id=request.workerid):
        # If we haven't constructed the responses rows for this worker
        # yet, let's make them
        for row in db().select(db.venice.ALL):
            crime = row.crime if request.experimental_treatment==1 else row.crime_control
            db.worker_response.insert(worker_id=request.workerid,
                                      prisoner_name=row.name,
                                      prisoner_crime=crime,
                                      prisoner_photo=row.photo,
                                      prisoner_message=row.message,
                                      treatment=request.experimental_treatment)
  
    # Choose a random prisoner for this worker to work on
    prisoner = db((db.worker_response.worker_id==request.workerid)
                  & (db.worker_response.message == None)
                  & (db.worker_response.displayed==1)) \
                  .select(db.worker_response.ALL,
                          orderby='<random>',
                          limitby=(0,1)).first()
  
    if prisoner == None:
        prisoner = db((db.worker_response.worker_id==request.workerid)
                      & (db.worker_response.message == None)).select(db.worker_response.ALL,
                                                                     orderby='<random>',
                                                                     limitby=(0,1)).first()
  
    # Abbreviate last name
    prisoner.prisoner_name = prisoner.prisoner_name.split()[0] \
        + ' ' + prisoner.prisoner_name.split()[1][0] + '.'

    prisoner.update_record(displayed=1)
    return dict(min_words=min_words,
                prisoner=prisoner,
                sex=request.experimental_treatment==1)




def tempo():
  return u'<html><body>%s</body></html>' % prisoners[19]