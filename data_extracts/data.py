#!/usr/bin/python
# coding: utf-8

import pandas
import json

import csv
df = pandas.DataFrame(columns=['hitid', 
                               'assid', 
                               'workerid', 
                               'accept_time', 
                               'finished_time',
                               'wage',
                               'survey_time',
                               'with pic_time',
                               'js log on user leaving_time',
                               'display_time',
                               'preview_time',
                               'disagreeable_rate',
                               'pay_delay',
                               'wait_time',
                               'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
                               'tag_1_1', 'tag_1_2', 'tag_1_3', 'tag_1_4', 'tag_1_5',
                               'tag_2_1', 'tag_2_2', 'tag_2_3', 'tag_2_4', 'tag_2_5',
                               'tag_3_1', 'tag_3_2', 'tag_3_3', 'tag_3_4', 'tag_3_5',
                               'tag_4_1', 'tag_4_2', 'tag_4_3', 'tag_4_4', 'tag_4_5',
                               'tag_5_1', 'tag_5_2', 'tag_5_3', 'tag_5_4', 'tag_5_5',
                               'disturbing_1', 'disturbing_2', 'disturbing_3', 'disturbing_4', 'disturbing_5',
                               'js_events',
                               'netprog',
                               'js_start',
                               'js_end',
                               'training_fails',
                               'image_tag_focus',
                               'first_image_tag_focus_time',
                               'last_image_tag_focus_time',
                               'radio_change',
                               'training_entered',
                               'exit_training',
                               'training_form_input',
                               'mean_focus_time',
                               'work_limit',
                               'work quota reached_time',
                               'first time_time',
                               'condition', 
                               'training',
                               'availability',
                               'phase',
                               'improbability_rate'])
with open('/tmp/actions_study_9.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    index = 0
    for row in spamreader:


        index += 1
        print(index)
        if index == 1:
            continue
        if index > 400000:
            # 5 other
            break
        action_time_var = row[0]+'_'+'time'
        if not any((df.hitid == row[1]) & (df.workerid == row[2]) & (df.assid == row[3])):
            # basic information later to be updated
            df.loc[index-1] = pandas.Series({
                                      'hitid': row[1],
                                      'workerid': row[2],
                                      'assid': row[3],
                                      'accept_time': None,
                                      'finished_time': None,
                                      'survey_time': None,
                                      'netprog': None,
                                      'with pic_time': None,
                                      'js log on user leaving_time': None,
                                      'display_time': None,
                                      'pay_delay': None,
                                      'availability': None,
                                      'work_limit': None,
                                      'image_1': None,
                                      'image_2': None,
                                      'image_3': None,
                                      'image_4': None,
                                      'image_5': None,
                                      'tag_1_1': None,
                                      'tag_1_2': None,
                                      'tag_1_3': None,
                                      'tag_1_4': None,
                                      'tag_1_5': None,
                                      'tag_2_1': None,
                                      'tag_2_2': None,
                                      'tag_2_3': None,
                                      'tag_2_4': None,
                                      'tag_2_5': None,
                                      'tag_3_1': None,
                                      'tag_3_2': None,
                                      'tag_3_3': None,
                                      'tag_3_4': None,
                                      'tag_3_5': None,
                                      'tag_4_1': None,
                                      'tag_4_2': None,
                                      'tag_4_3': None,
                                      'tag_4_4': None,
                                      'tag_4_5': None,
                                      'tag_5_1': None,
                                      'tag_5_2': None,
                                      'tag_5_3': None,
                                      'tag_5_4': None,
                                      'tag_5_5': None,
                                      'disturbing_1': None,
                                      'disturbing_2': None,
                                      'disturbing_3': None,
                                      'disturbing_4': None,
                                      'disturbing_5': None,
                                      'training': None,
                                      'js_events': None,
                                      'js_start': None,
                                      'first_image_tag_focus_time': None,
                                      'last_image_tag_focus_time': None,
                                      'js_end': None,
                                      'image_tag_focus': None,
                                      'radio_change': None,
                                      'training_fails': None,
                                      'disagreeable_rate': None,
                                      'improbability_rate': None,
                                      'wage': None,
                                      'preview_time': None,
                                      'wait_time': None,
                                      'work quota reached_time': None,
                                      'training_entered': None,
                                      'mean_focus_time': None,
                                      'exit_training': None,
                                      'training_form_input': None,
                                      'first time_time': None,
                                      'condition': row[5],
                                      'phase': row[7]})
        # add the time of the action information
        index_of_existing_record = df[(df.hitid == row[1]) & 
                                      (df.workerid == row[2]) & 
                                      (df.assid == row[3])].index.tolist()
        df[action_time_var][index_of_existing_record] = row[4]
                #print(row[6])
        if row[6] == '':
            print("empty!")
            continue
        #print(type(row[6]))
        #json.loads()
        #print(row[0])
        if row[0] == "accept":
            improbability_rate = json.loads(row[6])
            df['improbability_rate'][index_of_existing_record] = improbability_rate['improbability_rate']
            #print(type(improbability_rate['improbability_rate']))
            #print(type(improbability_rate))
        elif row[0] == "js log on user leaving":
            print("does this record already exist?")
            print(index_of_existing_record)
        #elif row[0] == "display":
        #    print(row[6])
            
        #elif row[0] == "with pic":
        #    print(row[6])
        elif row[0] == "finished":
            #print(row[6])
            behavior_data = json.loads(row[6])
            
            try:
                js_logs = behavior_data['request_vars']['activity_log']
                training_fail = 0
                image_tag_focus = 0
                radio_change = 0
                training_entered = 0
                exit_training = 0
                training_form_input = 0
                sum_focus_time_rel = 0
                for item in js_logs:
                    #print(item['action_type'])
                    if item['action_type'] == "training submission with mistakes":
                        training_fail += 1
                    elif item['action_type'] == "image tag focus":
                        image_tag_focus += 1
                        sum_focus_time_rel += item['relative_time']
                        if image_tag_focus == 1:
                            first_image_tag_focus_time = item['action_time']
                            first_focus_relative = item['relative_time']
                        #item['relative_time']
                    #else:
                        #tag_focus_dif = 
                        image_tag_focus_time = item['action_time']
                    elif item['action_type'] == "radio change":
                        radio_change += 1
                    elif item['action_type'] == "training entered":
                        training_entered += 1
                    elif item['action_type'] == "leave training in a training=false condition":
                        exit_training += 1
                    elif item['action_type'] == "training form input":
                        training_form_input += 1

                try:
                    mean_focus_dif = (sum_focus_time_rel-image_tag_focus*first_focus_relative)/image_tag_focus
                except ZeroDivisionError:
                    mean_focus_dif = None
                df['mean_focus_time'][index_of_existing_record] = mean_focus_dif
                df['first_image_tag_focus_time'][index_of_existing_record] = first_image_tag_focus_time
                df['last_image_tag_focus_time'][index_of_existing_record] = image_tag_focus_time
                df['training_fails'][index_of_existing_record] = training_fail
                df['image_tag_focus'][index_of_existing_record] = image_tag_focus
                df['radio_change'][index_of_existing_record] = radio_change
                df['training_entered'][index_of_existing_record] = training_entered
                df['exit_training'][index_of_existing_record] = exit_training
                df['training_form_input'][index_of_existing_record] = training_form_input
            #df['radio_change'][index_of_existing_record] = radio_change
            #df['radio_change'][index_of_existing_record] = radio_change

            
                first_js_event_time = js_logs[0]['action_time']
                last_js_event_time = js_logs[len(js_logs)-1]['action_time']
                df['js_start'][index_of_existing_record] = first_js_event_time
                df['js_end'][index_of_existing_record] = last_js_event_time
                df['js_events'][index_of_existing_record] = len(js_logs)
            except KeyError:
                print("js activity log not available for this HIT")
            df['wage'][index_of_existing_record] = behavior_data['approved_price']
            disagreeable_rate = behavior_data['request_vars']['study_number']['special_conditions'][0][1]['disagreeable']
            training = behavior_data['request_vars']['study_number']['special_conditions'][0][1]['training'] * 1
            availability = behavior_data['request_vars']['study_number']['special_conditions'][0][1]['availability']
            work_limit = behavior_data['request_vars']['study_number']['work_limit']
            improbability_rate =  behavior_data['request_vars']['study_number']['special_conditions'][0][1]['improbability_rate']
            for i in range(0,5):
                for j in range(0,5):
                    df_field = 'tag_' + str(i+1) + '_' + str(j+1)
                    other_field = 'image_tag_' + str(i) + '_' + str(j)
                    df[df_field][index_of_existing_record] = behavior_data['request_vars'][other_field]
                image_field = 'image_' + str(i+1)
                img_json_field = 'image_' + str(i)
                df[image_field][index_of_existing_record] = behavior_data['request_vars'][img_json_field]
                try:
                  df['disturbing_'+str(i+1)][index_of_existing_record] = behavior_data['request_vars']['disturbingness'+str(i)]
                except KeyError:
                  print("info about disagreeableness of the images missing")
                    
            df['work_limit'][index_of_existing_record] = work_limit
            df['netprog'][index_of_existing_record] = behavior_data['request_vars']['netprog']
            if availability == "low":
                availability = 1
            else: 
                availability = 0
            df['training'][index_of_existing_record] = training
            df['availability'][index_of_existing_record] = availability
            df['improbability_rate'][index_of_existing_record] = improbability_rate
            df['disagreeable_rate'][index_of_existing_record] = disagreeable_rate
            df['pay_delay'][index_of_existing_record] = behavior_data['request_vars']['study_number']['pay_delay']

        else:
            print(row[0])
            
df.to_csv('/tmp/transformed_experiment_data.csv', sep=',', encoding='utf-8')
