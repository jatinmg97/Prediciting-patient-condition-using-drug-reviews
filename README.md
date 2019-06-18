# Prediciting-patient-condition-using-drug-reviews

Patient narrative data is plentiful in the healthcare industry and often some of the most inaccessible data.  Doctor’s notes have historically been in the form of hand written text in a patient’s chart.  With the advent of Electronic Medical Records (EMRs), this data has been digitized and placed in electronic form, however, much of it remains in hard to use, free-text format.

We use online patient reviews of medications to predict the patient’s medical condition.

# Data set overview

The data set used was pulled from two websites, drugs.com and druglib.com, by Surya Kallumadi of Kansas State University and Felix Gräßer of the Institut für Biomedizinische Technik in Germany.  The data contains patient reviews of medications posted by internet users describing their experience with the medication.

We obtained this data from the UCI Machine Learning Repository.  The original research focus of this data set was sentiment analysis (Gräßer et al., 2018).

The data contains 161,297 training instances and 53,766 testing instances.  This is an approximate 75%/25% split which is the general rule of thumb for data classification.

# Sentiment Analysis

 We theorize that the sentiment embedded on a review can be a key factor to determine the review rating, the review impact on people (usefulCount), or how good a drug is for a specific condition. We used the text blob library to do a sentiment analysis on the customer reviews. Text blob is a Python library for processing textual data. It provides a simple API for common natural language processing (NLP) tasks such as parts of speech tagging, noun phrase extraction, sentiment analysis, classification, translation and more. We found out that drugs with higher ratings had a more positive sentiment. There was a trend of increase in the positive sentiment for the drugs with higher ratings as the customer would be satisfied with the results and thus the positive comment. 
 
 
