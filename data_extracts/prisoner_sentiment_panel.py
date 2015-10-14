import requests
import json
import csv
import pandas

#workerid,assid,hitid,time,work_limit,disagreeable,improbability_rate,training,wage,letter
# in previous version we created pandas data set on the fly and the new data appended there

def transform_data():
   modified_dataset = pandas.DataFrame(columns=[
      'workerid',
      'assid',
      'hitid',
      'time',
      'work_limit',
      'disagreeable',
      'success_rate',
      'test',
      'wage',
      'negative_sentiment',
      'positive_sentiment',
      'neutral_sentiment',
      'label'])

   with open('/home/econ/sql/data_extract_prisoner_quality.csv') as csv_source:
      prisoner_reader = csv.reader(csv_source, delimiter=',')
      index = 0
      for row in prisoner_reader:
         index += 1
         print(index)
         if index == 1:
            continue
         #print(len(row))
         letter_from_worker = row[9]
         letter_data = evaluate_sentiment(letter_from_worker)
         #print(letter_data['probability']['pos'])
         modified_dataset.loc[index-1] = pandas.Series({
            'workerid': row[0],
            'assid': row[1],
            'hitid': row[2],
            'time': row[3],
            'work_limit': row[4],
            'disagreeable': row[5],
            'success_rate': row[6],
            'test': row[7],
            'wage': row[8],
            'negative_sentiment': letter_data['probability']['neg'],
            'positive_sentiment': letter_data['probability']['pos'],
            'neutral_sentiment': letter_data['probability']['neutral'],
            'label': letter_data['label']})
         if index > 5000:
            #print(modified_dataset)
            break
      modified_dataset.to_csv('/home/econ/data/prisoner_quality_sentiment.csv', 
         sep=',', 
         encoding='utf-8')

def evaluate_sentiment(text):
   payload = {'text': text}

   r = requests.post("http://text-processing.com/api/sentiment/", data=payload)
   print(r.status_code)
   sentiment_data = json.loads(r.text)
   sentiment_data_prob = sentiment_data['probability']

   #neg, neutral, pos
   negative_sentiment = sentiment_data_prob['neg']
   positive_sentiment = sentiment_data_prob['pos']
   neutral_sentiment = sentiment_data_prob['neutral']
   sentiment_label = sentiment_data['label']
   return sentiment_data


transform_data()
