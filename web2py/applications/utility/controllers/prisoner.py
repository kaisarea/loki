def index():
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
                & (db.worker_response.displayed==1)).select(db.worker_response.ALL,
                                                            orderby='<random>',
                                                            limitby=(0,1)).first()
  
  #if prisoner == None:
  #  prisoner = db((db.worker_response.worker_id==request.workerid)
  #                &(db.worker_response.response_length < 150)
  #                &(db.worker_response.displayed==1)).select(db.worker_response.ALL,
  #                                                           orderby='<random>',
  #                                                           limitby=(0,1)).first()
  
  if prisoner == None:
    prisoner = db((db.worker_response.worker_id==request.workerid)
                  & (db.worker_response.message == None)).select(db.worker_response.ALL,
                                                                 orderby='<random>',
                                                                 limitby=(0,1)).first()   
  
  # Abbreviate last name
  prisoner.prisoner_name = prisoner.prisoner_name.split()[0] \
      + ' ' + prisoner.prisoner_name.split()[1][0] + '.'

  prisoner.update_record(displayed=1)
  return dict(min_words=min_words, prisoner=prisoner, sex=request.experimental_treatment==1)

def finish():
    mess = request.vars.worker_message
    wrdcount = 0

    #for i in mess.split():
     # eawrdlen = len(i) / len(i)
      #wrdcount = wrdcount + eawrdlen
      
    wrdcount = len(mess.split())
    q = ((db.worker_response.worker_id==request.vars.workerid)
         & (db.worker_response.prisoner_name==request.vars.prisoner_name))
    db(q).update(message=request.vars.worker_message,
                 price=request.vars.price,
                 response_length=wrdcount)
    hit_finished()
