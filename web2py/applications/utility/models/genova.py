options.genova = {'price' : [.05, .10, .15, .20, .25, .30, .35, .40, .45, .50, .55, .60],
		  'disagreeable' : [0, 12.5, 25, 50, 75, 100],
                  'training' : [False, True],
                  'improbability_rate' : [93, 56],
                  'availability' : ['high', 'low'],

		  'pics_per_task': 5,
                  'mystery_task': True,
                  'work_limit' : 50,
                  'pay_delay' : 13 * 60,
                  'first_time_bonus' : 0.50,

                  'special_conditions' : [(
                       .07, {'price' : .25,
                             'disagreeable' : False,
                             'training' : True,
                             'improbability_rate' : 56,
                             'availability' : 'low'}
                      )]
}


# This is how we load pictures
def define_genova_pics():
    """
    For treatment we will later do analogous code as for the control
    where directory will be crawled and all the content read
    in. Disturbing images come from disturbingpictures.tumblr.com.  I
    got as far as http://disturbingpictures.tumblr.com/page/22. Next
    time continue with page 23.
    """
    global genova_pics

    def load_pics(subdir):
        filenames = os.listdir("applications/utility/static/genova/%s" % subdir)
        return ['/static/genova/%s/%s' % (subdir, f) for f in filenames]


    genova_pics = Storage()
    genova_pics.control   = list(cache.ram('control pics', lambda: load_pics('control'), time_expire=60))
    genova_pics.treatment = list(cache.ram('treatment pics', lambda: load_pics('treatment'), time_expire=60))
    #genova_pics.food      = load_pics('food')
    return genova_pics