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
import numpy
import time

class ExperimentData:
    """
    encapsulates the data to be worked with

    this class will contain methods working on the data, like import, save, 
    transform etc

    methods:
    load_input -- loads the data
    add_sentiment -- takes a text of a letter and returns sentiment score
    add_letter_count -- adds information about letter count to the dataset
    add_unique_word_count -- adds information about number of unique words
    add_word_count -- adds number of words from the letter to the data
    save_data -- cleans the dataset from unnecessary columnsn and saves 
    """

    def __init__(self, filename):
        self.filename = filename
        

    def load_input(self, number_of_rows_to_read):
        """Load csv file into the class property for later use"""
        self.dataframe = pandas.read_csv(self.filename, nrows=number_of_rows_to_read)
        #self._describe_input_data()
       
    def _describe_input_data(self):
        """Show the imported data for inspection and diagnostics."""
        print(self.dataframe.describe()) # only describes numeric columns

    def add_sentiment(self):
        """call evaluate_sentiment() method for every row in the dataset"""
        self.record = 0
        letter_series = self.dataframe.letter        
        sentiment_call = lambda letter_text: self._evaluate_sentiment(letter_text)
        sentiment_data = letter_series.map(sentiment_call)
        self.dataframe['sentiment'] = sentiment_data
        self._unpack_sentiment_data()
     
    def _unpack_sentiment_data(self):
        """break up the sentiment data into four columns within the dataset"""
        get_neg = lambda x: x.get('probability').get('neg')
        get_pos = lambda x: x.get('probability').get('pos')
        get_neutral = lambda x: x.get('probability').get('neutral')
        get_label = lambda x: x.get('label')
        self.dataframe['negative_sentiment'] = self.dataframe['sentiment'].map(get_neg)
        self.dataframe['positive_sentiment'] = self.dataframe['sentiment'].map(get_pos)
        self.dataframe['neutral_sentiment'] = self.dataframe['sentiment'].map(get_neutral)
        self.dataframe['sentiment_label'] = self.dataframe['sentiment'].map(get_label)


    def _evaluate_sentiment(self, text):
        """uses the API to determine a score for sentiment"""
        na_record = {
            'probability': {
                'neg': numpy.nan, 
                'pos': numpy.nan, 
                'neutral': numpy.nan},
            'label': numpy.nan} 
        if text is not numpy.nan:
            payload = {'text': text}
            r = requests.post("http://text-processing.com/api/sentiment/", data=payload)
            if int(r.status_code) == 503:
                print("We're being throttled! Going to sleep for 55672 seconds.")
                time.sleep(55672) # delays for 5 seconds
            sentiment_data = json.loads(r.text)
            #except ValueError:
                #print(text)
                #print(r.status_code)
                #print(r.text)
                #return na_record
            
            self.record += 1
            return sentiment_data
        else:
            print(text)
            print(type(text))
            return na_record

    def add_letter_count(self):
        """count number of letters in a letter"""
        self.dataframe['letter_count'] = self.dataframe['letter'].str.len()

    def add_word_count(self):
        """count the number of words in the letter and save it to a new column"""
        self.dataframe['word_count'] = self.dataframe.letter.str.count('\w+')
        
    def add_unique_word_count(self):
        """add information about unique words to the dataset"""
        call_count = lambda letter_: self._count_unique_words(letter_)
        self.dataframe['unique_words'] = self.dataframe['letter'].map(call_count)

    def _count_unique_words(self, text):
        """helper function to implement the logic for counting unique words"""
        if text is not numpy.nan:
            count = len(set(text.split()))
            return count
        else:
            return 0

    def _remove_redundant_columns(self):
        """Remove the letter itself from the dataset along with other columns."""
        self.dataframe.drop(['letter', 'sentiment'], axis=1, inplace=True)

    def save_data(self, output_file):
        """Save the result to a file."""
        self._remove_redundant_columns()
        self.dataframe.to_csv(output_file, sep=',', encoding='utf-8')


filename_ = '/home/econ/data/prisoner_quality_panel_data.csv'
output = '/home/econ/data/prisoner_panel_data.csv'
prisoner_quality = ExperimentData(filename_)
prisoner_quality.load_input(None) # choose None to read all rows
prisoner_quality.add_sentiment()
prisoner_quality.add_letter_count()
prisoner_quality.add_word_count()
prisoner_quality.add_unique_word_count()
prisoner_quality.save_data(output)

   


