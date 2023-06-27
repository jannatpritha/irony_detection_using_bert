# -*- coding: utf-8 -*-
"""Bert Implementation 01.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oIEzbcMowpk5g5HS3Izi9BmPbu9KZu0G

# Installation Section
"""

!pip install ekphrasis
!pip install krovetzstemmer
!pip install emoji
!pip install emoticon-fix

"""# Preprocessing"""

# Import Section
import csv
import codecs
import sys
import io
import string    #to lower
import unicodedata    #for accented
import io
from nltk.tokenize import TweetTokenizer #for Lexical Normalization
import re #for url
import emoji

#Before using HashtagSegmenter - "pip install ekphrasis"
from ekphrasis.classes.segmenter import Segmenter
from krovetzstemmer import Stemmer
from emoticon_fix import emoticon_fix


#Global Initialization Section
seg = Segmenter(corpus="twitter")

#Customized Function Definition

def noWhiteSpaces(text):
  noSpaceSentence = ' '.join(text.split())
  noSpaceSentence = noSpaceSentence.strip()
  return noSpaceSentence

def noemojitext(text):

  without_emoji = emoji.demojize(text, language='en')
  without_emoticon= emoticon_fix.emoticon_fix(without_emoji)
  return without_emoticon

def peformStemming(text):
  text_list=text.split()
  stem=[]
  for t in text_list:
    stemmer = Stemmer()
    stem.append(stemmer.stem(t))

  stemmedText = ' '.join(map(str, stem))
  return stemmedText

#remove Stop Word

def removeStopWord(text):
  with open('/content/drive/MyDrive/Colab Notebooks/IronyDetection/SampleTemplateCode/stopwords_english.txt', 'r') as f:
   reader=csv.reader(f, dialect="excel-tab")

   text_list=text.split()
   removed_words=[]
   stopword_list=[]

   for line in reader:
     stopword_list.append(line[0])

   for t in text_list:
     if t not in stopword_list:
       removed_words.append(t)

  withoutstopword = ' '.join(map(str, removed_words))

  return withoutstopword


#removing URL
def removingUrl(text):
  processed_text= re.sub(r"http\S+", " url ", text)
  return processed_text

#removing Accented Characters

def removedAccentedCharacter(text):
  removedAccByteCode = unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
  removedAccentedChar=removedAccByteCode.decode()
  return removedAccentedChar

#lexical normalization

def tokenizer(text):
  tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
  global tokenizedtxt
  tokenizedtxt=tknzr.tokenize(text)
  return tokenizedtxt


def lexicalNormalization(text,thisdict,TweetTokenizer):
  normalizedText=""
  text=tokenizer(text)
  for word in text:
        if word in thisdict:
          s=thisdict[word]
          normalizedText=normalizedText+s+" "
        else:
          normalizedText=normalizedText+word+" "
  return normalizedText

def lexicalNormalizationmain(text):
  thisdict={}
  with open("/content/drive/MyDrive/Colab Notebooks/IronyDetection/SampleTemplateCode/LexicalNormalizationData.txt","r") as f:
    for line in f:
      (key, val) = line.split()
      thisdict[key] = val

  lexicallyNormalizedText = lexicalNormalization(text, thisdict, TweetTokenizer)
  return  lexicallyNormalizedText


#make all punctuations disappear

def noPunctuationText(text):
  string.punctuation
  punctuationfree="".join([i for i in text if i not in string.punctuation])
  return punctuationfree



#make all lowercase letters
def lowerLetters(text):
  return text.lower()


#hashtag segmentation . words are appended to the line
def hashtagSegmentation(text):
  givenText=text
  getHashTagFromText = [t for t in givenText.split() if t.startswith('#')]
  segmented_Hash = text
  #getHashtagSegmentedText = givenText
  if getHashTagFromText:
      for eachHashTag in getHashTagFromText:
           # print(eachHashTag)
           eachHashTag=eachHashTag[1:]
           # print(eachHashTag)
           segmented_Hash += ' '+seg.segment(eachHashTag)
           #getHashtagSegmentedText = getHashtagSegmentedText+" "+ segmented_Hash


  return segmented_Hash


# Data Preprocessing Module
def preProcessingModule(text):
  returnPreProcessedText=""
  getHashtagSegmentedText = hashtagSegmentation(text)
  getnoAccentedCharacter= removedAccentedCharacter(getHashtagSegmentedText)
  getAllSmallLetterText= lowerLetters(getnoAccentedCharacter)
  lexicallyNormalizedText = lexicalNormalizationmain(getAllSmallLetterText)
  urlRemovedText=removingUrl(lexicallyNormalizedText)
  noStopWord = removeStopWord(urlRemovedText)
  stemmedText =  peformStemming(noStopWord)
  no_emojiText = noemojitext(stemmedText)
  getnoPunctuationText = noPunctuationText(no_emojiText)
  removeWhitespaces=noWhiteSpaces(getnoPunctuationText)

  returnPreProcessedText = removeWhitespaces

  return returnPreProcessedText


tweets = []
label_test = []
csv.field_size_limit(500 * 1024 * 1024)
with open('/content/drive/MyDrive/Colab Notebooks/CodeForSKLearnClassifier/SemEval2018-IronyDetection_Gold_Test.txt', 'r') as f:
  next(f) # skip headings
  reader=csv.reader(f, dialect="excel-tab")
  for line in reader:
   #print(line[2])
    preProcessedTweetText= preProcessingModule(line[2])
    #print(preProcessedTweetText)
    #print('\n')
    tweets.append(preProcessedTweetText)
    label_test.append(int(line[1]))

label_test

for i in range(len(tweets)):
    text=tweets[i]
    print(text)

"""# Bert Implementation"""

# Transformers installation
! pip install transformers

from transformers import AutoTokenizer, TFAutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-irony')
model = TFAutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-irony')

from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
import numpy as np
from scipy.special import softmax
import csv
import urllib.request

predicted_result = []

task='irony'
MODEL = f"cardiffnlp/twitter-roberta-base-{task}"

tokenizer = AutoTokenizer.from_pretrained(MODEL)

# download label mapping
labels=[]
mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/{task}/mapping.txt"
with urllib.request.urlopen(mapping_link) as f:
    html = f.read().decode('utf-8').split("\n")
    csvreader = csv.reader(html, delimiter='\t')
labels = [row[1] for row in csvreader if len(row) > 1]

# PT
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
model.save_pretrained(MODEL)

for i in range(len(tweets)):
  text=tweets[i]
  encoded_input = tokenizer(text, return_tensors='pt')
  output = model(**encoded_input)
  scores = output[0][0].detach().numpy()
  scores = softmax(scores)

# # TF
# model = TFAutoModelForSequenceClassification.from_pretrained(MODEL)
# model.save_pretrained(MODEL)

# text = "Great, it broke the first day..."
# encoded_input = tokenizer(text, return_tensors='tf')
# output = model(encoded_input)
# scores = output[0][0].numpy()
# scores = softmax(scores)

  ranking = np.argsort(scores)
  ranking = ranking[::-1]
  print(labels[ranking[0]])
  if labels[ranking[0]] == 'irony':
    predicted_result.append(1)
  else:
    predicted_result.append(0)

print(predicted_result)
print(label_test)

from sklearn.metrics._plot.confusion_matrix import confusion_matrix
results = confusion_matrix(label_test, predicted_result)

results

from sklearn.metrics import *

print ('Recall Score :',recall_score(label_test, predicted_result, labels=['notIrony','irony'], pos_label=1))
print ('Precision Score :',precision_score(label_test, predicted_result, labels=['notIrony','irony'], pos_label=1))
print ('F1 Score :',f1_score(label_test, predicted_result, labels=['notIrony','irony'], pos_label=1))
print ('Accuracy :',accuracy_score(label_test, predicted_result))

print ('Evaluation Report : ')
print (classification_report(label_test, predicted_result))