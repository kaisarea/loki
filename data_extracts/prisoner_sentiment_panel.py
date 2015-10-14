"""
Transform prisoner quality data and create a panel

Take data with the following schema:
time_period,workerid,hitid,assid,submit,training_dummy,work_limit,
disagreeable_dummy,improbability_rate,letter
and add sentiment analysis to it
"""
import requests
import json
import csv
import pandas

class ExperimentData:
    """
    encapsulates the data to be worked with

    this class will contain methods working on the data, like import, save, 
    transform etc
    """

    def __init__(self, filename):
        self.filename = filename
        

    def load_input(self):
        """Load csv file into the class property for later use"""
        self.dataframe = pandas.read_csv(self.filename)
       
    def add_sentiment(self):
        """call evaluate_sentiment() method for every row in the dataset"""
        letter_series = self.dataframe.letter        
        sentiment_data = letter_series.apply(self._evaluate_sentiment)
        self.dataframe['sentiment'] = sentiment_data
     
    def _unpack_sentiment_data(self):
        """break up the sentiment data into four columns within the dataset"""
        self.dataframe.apply( 
            'negative_sentiment': letter_data['probability']['neg'],
            'positive_sentiment': letter_data['probability']['pos'],
            'neutral_sentiment': letter_data['probability']['neutral'],
            'label': letter_data['label']})

    def _evaluate_sentiment(text):
        """uses the API to determine a score for sentiment"""
        payload = {'text': text}
        r = requests.post("http://text-processing.com/api/sentiment/", data=payload)
        #print(r.status_code)
        sentiment_data = json.loads(r.text)
        #sentiment_data_prob = sentiment_data['probability']

        #neg, neutral, pos
        #negative_sentiment = sentiment_data_prob['neg']
        #positive_sentiment = sentiment_data_prob['pos']
        #neutral_sentiment = sentiment_data_prob['neutral']
        #sentiment_label = sentiment_data['label']
        return sentiment_data

    def add_word_count(self):

    def add_unique_word_count(self):

    def save_data(self):
        modified_dataset = pandas.DataFrame(columns=
        [   # list is an ordered collection 
            'time_period',
      'workerid',
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
        modified_dataset.to_csv('/home/econ/data/prisoner_quality_sentiment.csv', 
         sep=',', 
         encoding='utf-8')


filename_ = '/home/econ/data/prisoner_quality_panel_data.csv'
#schema_ = ['time_period',
#               'workerid',
#               'hitid',
#               'assid',
#               'submit',
#               'training_dummy',
#               'work_limit',
#               'disagreeable_dummy',
#               'improbability_rate',
#               'letter']
prisoner_quality = ExperimentData(filename_)
prisoner_quality.load_input()
prisoner_quality.add_sentiment()
prisoner_quality.add_word_count()
prisoner_quality.add_unique_word_count()


   


