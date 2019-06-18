# -*- coding: utf-8 -*-
"""Final Project - No Graphs.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QdXtaq_xIuP48Y63jsDx92_fggk0fjM5
"""

# All imports

import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
import warnings 
warnings.filterwarnings('ignore')
import gc
import string
import time

from itertools import islice
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import model_selection, preprocessing, metrics, ensemble, naive_bayes, linear_model
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix


import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem.snowball import SnowballStemmer

pd.options.mode.chained_assignment = None
pd.options.display.max_columns = 999


from sklearn import svm, datasets
from sklearn.metrics import confusion_matrix

import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

# UPLOAD FILES TO COLAB.  RUN TWICE FOR TRAINING AND TESTING FILES.

from google.colab import files
uploaded = files.upload()

# DISPLAY THE UPLOADED FILES

os.listdir()

# LOAD THE TRAINING AND TESTING DATA AND DO ALL PREPROCESSING

def reload_data(maxTrain = 0, maxTest = 0):
  global train
  global test
  
  # load training and testing data from file
  train=pd.read_csv("drugsComTrain_raw.tsv",parse_dates=["date"], sep='\t')
  if maxTrain > 0: train = train.head(maxTrain)
  
  test=pd.read_csv("drugsComTest_raw.tsv",parse_dates=["date"], sep='\t')
  if maxTest > 0: test = test.head(maxTest)
  
  # preprocessing steps
  
  # dropping null values
  train=train.dropna()
  test=test.dropna()

  # remove conditions with HTML markup
  train = train[train.condition.str.contains('</span>')==False]
  test = test[test.condition.str.contains('</span>')==False]
  
  # remove the Not Listed condition category
  train = train[train.condition !='Not Listed / Othe']
  test = test[test.condition !='Not Listed / Othe']


  # remove testing data that has conditions not in the training set
  conditionList=train.condition.unique()
  test = test[test.condition.isin(conditionList)]

  # Stem the reviews
  stemmer = SnowballStemmer("english")
  train['stemmed'] = train.review.map(lambda x: ' '.join([stemmer.stem(y) for y in x.split(' ')]))
  test['stemmed'] = test.review.map(lambda x: ' '.join([stemmer.stem(y) for y in x.split(' ')]))
  
  # create numeric condition column
  conds = train.condition.unique()
  cond_dict = dict(zip(conds, range(len(conds))))
  cond_dict_inv = dict([[v,k] for k,v in cond_dict.items()])
  
  train['condid'] = 0
  test['condid'] = 0

  train['condid'] = train['condition'].apply(lambda x: cond_dict[x])
  test['condid'] = test['condition'].apply(lambda x: cond_dict[x])
  
reload_data()

# GENERATE STOP WORDS LIST

def get_stop_words(data, max_df=0.5):
  global train
  
  cvec = CountVectorizer(stop_words='english', min_df=0.0, max_df=0.5, ngram_range=(1,1))
  cvec.fit(data)
  list(islice(cvec.vocabulary_.items(), 20))
  
  return text.ENGLISH_STOP_WORDS.union(list(islice(cvec.stop_words_, 20)))

# MODEL TRAINING AND TESTING ROUTINES

# MODEL TRAINING 

def train_model(clf, data, y, ngrams = 2, max_features = None, stop_words = text.ENGLISH_STOP_WORDS):
  global cvect
  global tf
  
  cvect = CountVectorizer(stop_words=stop_words, min_df=0.000, max_features=max_features, ngram_range=(1,ngrams))
  X = cvect.fit_transform(data)
  tf = TfidfTransformer(use_idf=True).fit(X)
  X_train_tf = tf.transform(X)
  start = time.time()
  clf.fit(X, y)
  end = time.time()
  print("training time: %s" % str(end-start))

# TEST MODEL, RETURNS PREDICTION SERIES

def test_model(clf, data):
  global cvect
  global tf
  
  start = time.time()
  X = cvect.transform(data)
  X_new_tf = tf.transform(X)
  predicted = clf.predict(X_new_tf)
  end = time.time()
  print("classify time: %s" % str(end-start))
  return predicted

# TEST OPTIMAL NUMBER OF NGRAMS

reload_data()

for ngrams in range(1,5):
  print("ngrams = " + str(ngrams))
  train_model(clf, train.stemmed, train.condid.values, max_features = 15000, stop_words = my_stop_words, ngrams = ngrams)
  predicted = test_model(clf, test.stemmed)  
  print(round(np.mean(predicted == test.condid) * 100.0,1))

# FIND OPTIMAL max_features PARAMETER

my_stop_words = get_stop_words(train.stemmed, max_df = 0.5)

for num in range(1000, 36000, 1000):
  clf = MultinomialNB()
  print("max_features = " + str(num))
  train_model(clf, train.stemmed, train.condid.values, max_features = num, stop_words = my_stop_words, ngrams = 2)

  predicted = test_model(clf, test.stemmed)  
  print(round(np.mean(predicted == test.condid) * 100.0,2))

# FIND A PRELIMINARY SET OF STOP WORDS
for num in range(3, 0, -1):
  clf = MultinomialNB()
  df = num / 10.0
  print("stop words = " + str(df))
  my_stop_words = get_stop_words(train.stemmed, max_df = df)
  train_model(clf, train.stemmed, train.condid.values, max_features = 25000, stop_words = my_stop_words, ngrams = 2)

  predicted = test_model(clf, test.stemmed)  
  print(round(np.mean(predicted == test.condid) * 100.0,2))

# TEST DIFFERENT CLASSIFIERS

names = [
    "MultinomialNB",
    "Nearest Neighbors",
    "Linear SVM",
    "Random Forest",
    "AdaBoost",
    #"Neural Net",
    "SGD"
    ]

classifiers = [
    MultinomialNB(),
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    RandomForestClassifier(max_depth=20, n_estimators=20, max_features=1),
    AdaBoostClassifier(),
    #MLPClassifier(alpha=1),
    SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=10, tol=None)
    ]

# loop each classifier/name pair and print accuracy and timing

for name, clf in zip(names, classifiers):
  print("classifier " + name)
  train_model(clf, train.stemmed, train.condid.values, max_features = 25000, ngrams = 2)
  predicted = test_model(clf, test.stemmed)
  print(round(np.mean(predicted == test.condid) * 100.0,2))

# TEST REMOVING usefulCount VALUES BELOW THRESHOLD

reload_data()

for count in range(0,10):
  train = train[train.usefulCount > count]
  print("min usefulCount = " + str(count))
  print("# rows training data " + str(train.shape[0]))
  train_model(clf, train.stemmed, train.condid.values, max_features = 25000, stop_words = my_stop_words, ngrams = 2)
  predicted = test_model(clf, test.stemmed)  
  print(np.mean(predicted == test.condid))

# PRINT STATISICS ON FINAL CLASSIFIER

reload_data()

clf = MultinomialNB()
my_stop_words = get_stop_words(train.stemmed, max_df = 0.5)
train_model(clf, train.stemmed, train.condid.values, max_features = 25000, stop_words = my_stop_words, ngrams = 2)
predicted = test_model(clf, test.stemmed)  
print(round(np.mean(predicted == test.condid) * 100.0,2))

print(classification_report(test.condid.values, predicted))
