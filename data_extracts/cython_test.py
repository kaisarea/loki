import pandas
from urllib import urlopen
import json
import csv
import psycopg2
from pandas import read_csv
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
from nltk.book import *
import numpy as np

def import_conditions():
   conditions_df = pandas.DataFrame(columns=['condition_id', 'availability', 'disagreeable', 'price', 'training'])
   condition_ids = set()
   conn = psycopg2.connect("dbname=nail_utility user=econ")
   cur = conn.cursor()
   cur.execute("SELECT DISTINCT condition FROM actions WHERE study = 9 AND action = 'accept';")
   rows = cur.fetchall()
   for row in rows:
      condition_ids.add(row[0])
   conn.commit()
   cur.close()
   conn.close()

   with open('/tmp/conditions_jul20_2015_tab.csv', 'rb') as csvfile:
      conditions_reader = csv.reader(csvfile, delimiter='@')
      index = 0
      for row in conditions_reader:
         #print(row)
         condition_id = int(row[0])
         if int(condition_id) in condition_ids:
            index += 1
            #if index > 500:
            #   break
            condition_data = json.loads(row[1])
            #if condition_data['availability'] != "high": 
            #   print(condition_data['availability'])
            conditions_df.loc[index-1] = pandas.Series({
               'condition_id': int(row[0]),
               'availability': 1 if condition_data['availability'] == "high" else 0, 
               'disagreeable': condition_data['disagreeable'], 
               'price': condition_data['price'],
               'training': int(condition_data['training'])})

   return conditions_df
                                                                                                                                                                                                                                                                        
def get_action_columns():
   columns_from_actions = ['hitid', 'assid', 'workerid', 'accept_time', 'finished_time', 'wage', 'survey_time', 'with pic_time', 'js log on user leaving_time', 'display_time',
                           'preview_time', 'pay_delay', 'wait_time', 'rating_misses', 'similarity_index', 'similarity_indices',
                           'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
                           'image_1_condition', 'image_2_condition', 'image_3_condition', 'image_4_condition', 'image_5_condition', 
                           'tag_1_1', 'tag_1_2', 'tag_1_3', 'tag_1_4', 'tag_1_5',
                           'tag_2_1', 'tag_2_2', 'tag_2_3', 'tag_2_4', 'tag_2_5',
                           'tag_3_1', 'tag_3_2', 'tag_3_3', 'tag_3_4', 'tag_3_5',
                           'tag_4_1', 'tag_4_2', 'tag_4_3', 'tag_4_4', 'tag_4_5',
                           'tag_5_1', 'tag_5_2', 'tag_5_3', 'tag_5_4', 'tag_5_5',
                           'disturbing_1', 'disturbing_2', 'disturbing_3', 'disturbing_4', 'disturbing_5',
                           'js_events', 'netprog', 'js_start', 'js_end', 'training_fails', 'image_tag_focus', 'first_image_tag_focus_time',
                           'last_image_tag_focus_time', 'radio_change', 'training_entered', 'exit_training', 'training_form_input', 'total_treatment_images',
                           'mean_focus_time', 'work_limit', 'work quota reached_time', 'first time_time', 'condition', 'phase', 'improbability_rate']
   return columns_from_actions


def import_actions_data():
   # define the schema of the dataset
   df = pandas.DataFrame(columns=get_action_columns())
   # load in the input from the database
   with open('/tmp/actions_study_9.csv', 'rb') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',')
      cdef int index = 0
      for row in spamreader:
         index += 1
         print(index)
         if index == 1:
            # skipping the header
            continue
         if index > 100:
            # 5 other
            break
            #print("hundred records finished")
        # what kind of action are we dealing with
         action_time_var = row[0]+'_'+'time'
         if not any((df.hitid == row[1]) & (df.workerid == row[2]) & (df.assid == row[3])):
            # basic information later to be updated
            df.loc[index-1] = pandas.Series({
                                      'hitid': row[1], 'workerid': row[2], 'assid': row[3],
                                      'accept_time': None, 'finished_time': None, 'survey_time': None, 'netprog': None, 'with pic_time': None, 'js log on user leaving_time': None, 'display_time': None,
                                      'pay_delay': None, 'work_limit': None, 'total_treatment_images': None, 'rating_misses': None, 'similarity_index': None, 'similarity_indices': None,
                                      'image_1': None, 'image_2': None, 'image_3': None, 'image_4': None, 'image_5': None,
                                      'image_1_condition': None, 'image_2_condition': None, 'image_3_condition': None, 'image_4_condition': None, 'image_5_condition': None,
                                      'tag_1_1': None, 'tag_1_2': None, 'tag_1_3': None, 'tag_1_4': None, 'tag_1_5': None,
                                      'tag_2_1': None, 'tag_2_2': None, 'tag_2_3': None, 'tag_2_4': None, 'tag_2_5': None,
                                      'tag_3_1': None, 'tag_3_2': None, 'tag_3_3': None, 'tag_3_4': None, 'tag_3_5': None,
                                      'tag_4_1': None, 'tag_4_2': None, 'tag_4_3': None, 'tag_4_4': None, 'tag_4_5': None,
                                      'tag_5_1': None, 'tag_5_2': None, 'tag_5_3': None, 'tag_5_4': None, 'tag_5_5': None,
                                      'disturbing_1': None, 'disturbing_2': None, 'disturbing_3': None, 'disturbing_4': None, 'disturbing_5': None,
                                      'js_events': None, 'js_start': None, 'first_image_tag_focus_time': None, 'last_image_tag_focus_time': None,
                                      'js_end': None, 'image_tag_focus': None, 'radio_change': None, 'training_fails': None,
                                      'improbability_rate': None, 'wage': None, 'preview_time': None, 'wait_time': None,
                                      'work quota reached_time': None, 'training_entered': None, 'mean_focus_time': None,
                                      'exit_training': None, 'training_form_input': None, 'first time_time': None,
                                      'condition': None, 'phase': None})
        # add the time of the action information
        # record already exists either because we just created it
        # or because it had existed before
         index_of_existing_record = df[(df.hitid == row[1]) & (df.workerid == row[2]) & (df.assid == row[3])].index.tolist()
        # add time of this action
         df[action_time_var][index_of_existing_record] = row[4]
                #print(row[6])
         if row[6] == '':
            print("If there is no other field we can move on, %s!" % row[0])
            continue
         if row[0] == "accept":
            df['condition'][index_of_existing_record] = int(row[5])
            df['phase'][index_of_existing_record] = row[7]
            improbability_rate = json.loads(row[6])
            df['improbability_rate'][index_of_existing_record] = improbability_rate['improbability_rate']
         elif row[0] == "js log on user leaving":
            print("does this record already exist? -- %s" % str(index_of_existing_record))
         elif row[0] == "finished":
            # this where the biggest json is stored
            behavior_data = json.loads(row[6])
            #print(behavior_data)
            try:
               js_logs = behavior_data['request_vars']['activity_log']
               cdef int training_fail = 0
               cdef int image_tag_focus = 0
               cdef int radio_change = 0
               cdef int training_entered = 0
               cdef int exit_training = 0
               cdef int training_form_input = 0
               cdef int sum_focus_time_rel = 0
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
               first_js_event_time = js_logs[0]['action_time']
               last_js_event_time = js_logs[len(js_logs)-1]['action_time']
               df['js_start'][index_of_existing_record] = first_js_event_time
               df['js_end'][index_of_existing_record] = last_js_event_time
               df['js_events'][index_of_existing_record] = len(js_logs)
            except KeyError:
               print("js activity log not available for this HIT")
            df['wage'][index_of_existing_record] = behavior_data['approved_price']
            work_limit = behavior_data['request_vars']['study_number']['work_limit']
            cdef int treatment_images_count = 0
            cdef int rating_misses = 0
            similarity_results = []  ### we will use this to create the similarity index   
            for i in range(0,5):
               words = []  # we will use this for the similarity index, will store synonyms
               for j in range(0,5):
                  df_field = 'tag_' + str(i+1) + '_' + str(j+1)
                  other_field = 'image_tag_' + str(i) + '_' + str(j)
                  tag_from_worker = behavior_data['request_vars'][other_field]
                  df[df_field][index_of_existing_record] = tag_from_worker 

                  ### now we would like to create the similarity index
                  #tag_from_worker = data_frame['tag_1_'+str(i)][data_frame['tag_1_'+str(i)].notnull()][7]
                  try:
                     first_syn = wn.synsets(tag_from_worker)[0]
                     words.append(first_syn)
                  except IndexError:
                     print(tag_from_worker)
                     print("no synonyms here?")
                     print(words)

               if len(words) > 1:     
                  for k in range(0,len(words)):
                     for l in range(0,len(words)):
                        if k < l:
                           similarity_index = words[k].path_similarity(words[l])
                           if similarity_index is None:
                              similarity_index = 0
                           similarity_results.append(similarity_index)
                  ### end of the similarity index code

               image_field = 'image_' + str(i+1)
               img_json_field = 'image_' + str(i)
               df[image_field][index_of_existing_record] = behavior_data['request_vars'][img_json_field]
               if behavior_data['request_vars'][img_json_field].split('/')[3] == 'treatment':
                  treatment_images_count += 1
               df['image_' + str(i+1) + '_condition'][index_of_existing_record] = int(behavior_data['request_vars'][img_json_field].split('/')[3]=='treatment')   
               try:
                  df['disturbing_'+str(i+1)][index_of_existing_record] = behavior_data['request_vars']['disturbingness'+str(i)]
                  if int(behavior_data['request_vars'][img_json_field].split('/')[3]=='treatment') !=  int(behavior_data['request_vars']['disturbingness'+str(i)]):
                     rating_misses += 1
               except KeyError:
                  print("user rating of appropriateness not found")
                  #print(behavior_data)
            print("Number of image for which similarity could be calculated: %s" % str(len(similarity_results)))
            if len(similarity_results) > 0:
               df['similarity_index'][index_of_existing_record] = np.asarray(similarity_results).mean() ### for the similarity index
               df['similarity_indices'][index_of_existing_record] = len(similarity_results)
            else:
               df['similarity_index'][index_of_existing_record] = None
               df['similarity_indices'][index_of_existing_record] = 0
            df['total_treatment_images'][index_of_existing_record] = treatment_images_count
            df['work_limit'][index_of_existing_record] = work_limit
            df['netprog'][index_of_existing_record] = behavior_data['request_vars']['netprog']
            df['pay_delay'][index_of_existing_record] = behavior_data['request_vars']['study_number']['pay_delay']
            df['rating_misses'][index_of_existing_record] = rating_misses
   
   return df

#def CustomParser(data):
#   if data == "":
#      return dict()
#   else:
#      j1 = json.loads(data)
#      return j1

def read_actions_data():
  data_file = urlopen("/tmp/actions_study_9.csv")
  actions_df = read_csv(data_file, low_memory=False)
  test = actions_df.pop('other')
  df5 = pandas.concat([actions_df, test.apply(pandas.Series)], axis=1)
  print(df5[df5['action'] == 'finished'].ix[0:10])
  df2 = actions_df.drop_duplicates(['hitid', 'workerid', 'assid', 'action'])
  df3 = df2.set_index(['hitid', 'workerid', 'assid', 'action'])
  df4 = df3.unstack(3)

def run_long_process():
   conditions_df = import_conditions()
   actions_df = import_actions_data()
   merged_left = pandas.merge(left=actions_df,right=conditions_df, how='left', left_on='condition', right_on='condition_id')
   merged_left.to_csv('/tmp/actions_with_conditions-IV.csv', sep=',', encoding='utf-8')


run_long_process()
