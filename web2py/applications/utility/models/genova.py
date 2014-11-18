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
