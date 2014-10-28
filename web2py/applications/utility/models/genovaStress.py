options.genovaStress = {'price' : [.05, .10, .15, .20, .25, .30, .35, .40, .45, .50],
      'disagreeable' : [0, 12.5, 25, 50, 75, 100],
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
