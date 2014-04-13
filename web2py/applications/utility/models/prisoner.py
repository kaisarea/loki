options.prisoner = {'price' : [.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0],
                    # 'experimental_dimension' : ['none',                # control
                    #                             'disagreeable',        #'agreeableness'
                    #                             'training',            #'learning',
                    #                             'improbability_rate',  #'success_rate',
                    #                             'work_limit'],

                    'disagreeable' : [True, False],
                    'training' : [True, False],
                    'improbability_rate' : [94, 51],
                    'work_limit' : [10, 91],

                    'mystery_task': True,
                    'pay_delay' : 30 * 60,
                    'first_time_bonus' : 0.25,
                    'hit_params' : {'title' : 'Clearing House - Different Task Each Day! (Pays Bonus)',
                                    'description' : 'We aggregate tasks from many clients.  Tasks and task details change each day.  View today\'s HIT to see it and decide if you like it.',
                                    'keywords' : 'CrowdClearinghouse, Clearing House, Clearinghouse, random, bonus',
                                    'block_india' : True},
                    'phase_change_time' : 24 * 60 * 60
                    }


    
bad_workers = ['A3IKU2UUVMXBCQ', 'A14S4LB7IKVIF3', 'AN6CLA8F8NZF2', 'A1ED8FKNV1RTBU']
bad_workers_2 = ['A341LHR7178BUY', 'A3MS21UJPMHLK0']
skeptical_workers_2 = ['A2QHK3FRFCEDBJ']