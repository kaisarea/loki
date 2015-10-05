options.genova = {'price' : [.05, .10, .15, .20, .25, .30, .35, .40, .45, .50],
		  'disagreeable' : [0, 20, 40, 60, 80, 100],
                  'training' : [False, True],
                  'improbability_rate' : [93, 56],
                  'availability' : ['high'],

                  'special_conditions' : [(
                       .07, {'price' : .25,
                             'disagreeable' : 0,
                             'training' : True,
                             'improbability_rate' : 93,
                             'availability' : 'low'}
                      )],

		  'pics_per_task': 5,
                  'mystery_task': True,
                  'work_limit' : 50,
                  'pay_delay' : 90 * 60,
                  'first_time_bonus' : 0.25,
                  'phase_change_time' : 24 * 60 * 60,

                  'hit_params' : {'title' : 'Clearing House - Different Task Each Day! (Pays Bonus)',
                                  'description' : 'We aggregate tasks from many clients.  Tasks and task details change each day.  View today\'s HIT to see it and decide if you like it.',
                                  'keywords' : 'CrowdClearinghouse, Clearing House, Clearinghouse, random, bonus',
                                  'block_india' : True}
}


# This is how we load pictures
def load_genova_pics():
    """
    For treatment we will later do analogous code as for the control
    where directory will be crawled and all the content read
    in. Disturbing images come from disturbingpictures.tumblr.com.  I
    got as far as http://disturbingpictures.tumblr.com/page/22. Next
    time continue with page 23.
    """
    global genova_pics

    def load_pics(subdir):
        #filenames = os.listdir("applications/utility/static/genova/%s" % subdir)
        #f = open('/home/econ/loki/static/genova/file_list_%s' % subdir, 'r')
        filenames = [line.strip() for line in open('/home/econ/loki/static/genova/file_list_%s' % subdir)]
        #test = f.readline()
        #test.strip()
        return ['/static/genova/%s/%s' % (subdir, f) for f in filenames]


    genova_pics = Storage()
    genova_pics.control   = list(cache.ram('control pics', lambda: load_pics('control'), time_expire=60))
    genova_pics.treatment = list(cache.ram('treatment pics', lambda: load_pics('treatment'), time_expire=60))
    #genova_pics.food      = load_pics('food')
    return genova_pics


def updateImprobability():
    # This function will attempt to replicate code from the controller so we may obtain veritable
    # improbability data
    import random, time, json
    def random_offset(max_offset, seed):
        random.seed(seed)
        result = (random.random() - .5) * max_offset * 2
        random.seed()
        return result
    # we need workerid ID and progress
    # What is progress?
    # we need to loop through all the assignments
    condition1 = (db.actions.study == 9)
    condition2 = (db.actions.action == 'with pic')
    condition3 = (db.actions.workerid != None)
    condition4 = (db.actions.workerid != 'WORKER_ID_NOT_AVAILABLE')
    allConditions = condition1 & condition2  & condition3 & condition4
    allWorkers = db(allConditions).select(db.actions.workerid, distinct=True, orderby=db.actions.workerid)
    counter = 0
    for worker in allWorkers:
        condition5 = (db.actions.workerid == worker.workerid)
        allAssConditions = allConditions & condition5
        allAssignments = db(allAssConditions).select(orderby=db.actions.time)
        for assignment in allAssignments:
            assExpConditions = db((db.conditions.id==assignment.condition)).select().first()
            try:
                improbabilityRate = json.loads(assExpConditions.json)['improbability_rate']
            except AttributeError:
                print("Could not locate condition of this assignment")
                print(assignment.assid)
                continue
            
            max_offset = 6 if improbabilityRate < 90 else 2
            displayed_improbability_rate = improbabilityRate + random_offset(max_offset, assignment.time.day) + random_offset(max_offset/2, assignment.time.hour)
            displayed_improbability_rate = int(displayed_improbability_rate)
            displayed_improbability_rate = min(displayed_improbability_rate, 99)
            
            cond6 = (db.actions.action == 'accept')
            cond7 = (db.actions.assid == assignment.assid)
            cond8 = (db.actions.time == assignment.time)
            cond9 = (db.actions.other == None)
            conditionsForUpdate = condition1 & condition5 & cond6 & cond7 & cond8 & cond9
            disImproRateDict = dict(improbability_rate=displayed_improbability_rate)
            dbOutput = json.dumps(disImproRateDict)
            testExistence = db(conditionsForUpdate).count()
            print(testExistence)
            if testExistence == 0:
                continue
            elif testExistence > 1:
                print("weird stuff, more than one record")
            #if testExistence is None:
            #    print("Did not find an empty record")
            #else:
            #    for record in testExistence:
            #        print("record")
            updateRes = db(conditionsForUpdate).update(other = dbOutput)
            print(updateRes)
            db.commit()
            counter+=1
            shellOutput = [counter, worker.workerid, assignment.time, assignment.assid, improbabilityRate, displayed_improbability_rate]
            #print(counter)
            #print(worker.workerid)
            #print(assignment.time)
            #print(assignment.assid)
            #print(improbabilityRate)
            #print(displayed_improbability_rate)
            print(shellOutput)
            #if counter > 5:
            #    return
#db(db.person.name == 'Massimo').update(
#        visits = db.person.visits + 1)
            # we can save it under accept/display/with pic, they should even have the same time
            #imageNamesList = json.loads(assignment.other)
            #print(type(imageNamesList))
            #print(imageNamesList)
            #for image in imageNamesList:
            #    if "control" in image:
            #        print("control")
            #        #controlPics += 1
            #    elif "food" in image:
            #        print("food")
            #        #foodPics += 1
            #    elif "treatment" in image:
            #        print("treatment")
            #        #treatmentPics += 1
            #    else:
            #        print("image type not recognized")

def randomize_pay(pay, expected_rate_of_success, num_tags):
    import math
    rate_of_failure = 1.0 - expected_rate_of_success
    rate_of_failure /= 6.0  # Let's diminish it, be nicer
    rate_of_success = 1 - random.random() * rate_of_failure
    good_tags = round(num_tags * rate_of_success)
    pay = pay * (good_tags/float(num_tags))
    log('With noise, we want to pay %.4f' % pay)
    pay = math.ceil(pay * 100.0)/100.0
    log('When rounded, are actually paying %.3f' % pay)
    return (pay, int(good_tags))

#(rate_of_success / 100.0)  float(request.price)

def updateGeoFromIP():
    import requests
    print("getting geo info")
    ip_addresses = db(
        (db.actions.workerid != None) & 
        (db.actions.ip != None)
        ).select(db.actions.ip, distinct=True)
    counter = 0
    for ip_address in ip_addresses:
        counter = counter + 1
        """if counter > 3:
            break"""
        page_to_be_requested = 'http://freegeoip.net/json/' + ip_address.ip
        r = requests.get(page_to_be_requested)
        response_dict = r.json()
        try:
            country_name = response_dict['country_name']
        except AttributeError:
            country_name = "NA"
        try:
            region_code = response_dict['region_code']
        except AttributeError:
            region_code = "NA"
        try:
            region_name = response_dict['region_name']
        except AttributeError:
            region_name = "NA"
        try:
            city = response_dict['city']
        except AttributeError:
            city = "NA"
        try:
            time_zone = response_dict['time_zone']
        except AttributeError:
            time_zone = "NA"
        try:
            #print(response_dict.zip_code)
            zip_code = response_dict['zip_code']
        except AttributeError:
            zip_code = "NA"
        try:
            country_code = response_dict['country_code']
        except AttributeError:
            #print(type(r))
            #print(r['country_code'])
            #print(response_dict.country_code)
            country_code = "NA"
        try:
            latitude = response_dict['latitude']
        except AttributeError:
            latitude = 0.00
        try:
            longitude = response_dict['longitude']
        except AttributeError:
            longitude = 0.00
        try:
            metro_code = response_dict['metro_code']
        except AttributeError:
            metro_code = 0
#        print([city, region_name, region_code, time_zone, zip_code, latitude, longitude, country_name])
        db.ip_addresses.insert(
            ip = ip_address.ip, country_code = country_code, country_name = country_name,
            region_code = region_code, region_name = region_name, 
            city = city, zip_code = zip_code, time_zone = time_zone,
            latitude = latitude, longitude = longitude, metro_code = metro_code)
        db.commit()
        print(counter)






















