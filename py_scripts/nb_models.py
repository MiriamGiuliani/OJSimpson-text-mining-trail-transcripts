import re
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import fnmatch
import nltk
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from itertools import combinations


# Functions needed in notebooks_models\4_topic_modeling.ipynb

# Remove punctuation
def rem_punct(speech):
    speech = re.sub(r'[^\w\s]', '', str(speech))
    speech = re.sub(r'[0-9]', '', str(speech))
    return speech

# Tokenization
def tokenize(speech):
    token = nltk.word_tokenize(str(speech))
    return token

# Remove stopwords
def stopwords_rem(speech, list_stopwords):
    new = [word for word in speech if word not in list_stopwords]
    return new

# Stemming
ps = PorterStemmer()
def stemming(speech):
    stem = [ps.stem(el) for el in speech]
    return stem

def get_descriptor(terms, H, topic_index, top ):
    # reverse sort the values to sort the indices
    top_indices = np.argsort( H[topic_index,:] )[::-1]
    # now get the terms corresponding to the top-ranked indices
    top_terms = []
    for term_index in top_indices[0:top]:
        top_terms.append( terms[term_index] )
    return top_terms

def plot_top_term_weights( terms, H, topic_index, top ):
    # get the top terms and their weights
    top_indices = np.argsort( H[topic_index,:] )[::-1]
    top_terms = []
    top_weights = []
    for term_index in top_indices[0:top]:
        top_terms.append( terms[term_index] )
        top_weights.append( H[topic_index,term_index] )
    # note we reverse the ordering for the plot
    top_terms.reverse()
    top_weights.reverse()
    # create the plot
    fig = plt.figure(figsize=(13,8))
    # add the horizontal bar chart
    ypos = np.arange(top)
    ax = plt.barh(ypos, top_weights, align="center", color="green",tick_label=top_terms)
    plt.xlabel("Term Weight",fontsize=14)
    plt.tight_layout()
    plt.show()

def get_top_snippets( all_snippets, W, topic_index, top ):
    # reverse sort the values to sort the indices
    top_indices = np.argsort( W[:,topic_index] )[::-1]
    # now get the snippets corresponding to the top-ranked indices
    top_snippets = []
    for doc_index in top_indices[0:top]:
        top_snippets.append( all_snippets[doc_index] )
    return top_snippets

class TokenGenerator:
    def __init__( self, documents, stopwords ):
        self.documents = documents
        self.stopwords = stopwords
        self.tokenizer = re.compile( r"(?u)\b\w\w+\b" )

    def __iter__( self ):
        print("Building Word2Vec model ...")
        for doc in self.documents:
            tokens = []
            for tok in self.tokenizer.findall(doc):
                if tok in self.stopwords:
                    tokens.append( "<stopword>" )
                elif len(tok) >= 2:
                    tokens.append( tok )
            yield tokens

def calculate_coherence(w2v_model, term_rankings ):
    overall_coherence = 0.0
    single_coherence = list()
    for topic_index in range(len(term_rankings)):
        # check each pair of terms
        pair_scores = []
        for pair in combinations(term_rankings[topic_index], 2 ):
            if pair[0] not in w2v_model:
            #print(pair[0])
                continue
            if pair[1] not in w2v_model:
                #print(pair[1])
                continue
            else:
                pair_scores.append( w2v_model.similarity(pair[0], pair[1]))
        # get the mean for all pairs in this topic
        if len(pair_scores) == 0:
            continue
        else:       
            topic_score = sum(pair_scores) / len(pair_scores)
            single_coherence.append(topic_score)
            overall_coherence += topic_score
    # get the mean score across all topics
    return overall_coherence / len(term_rankings)

def calculate_singlecoherence(w2v_model, term_rankings ):
    overall_coherence = 0.0
    single_coherence = list()
    for topic_index in range(len(term_rankings)):
        # check each pair of terms
        pair_scores = []
        for pair in combinations(term_rankings[topic_index], 2 ):
            if pair[0] not in w2v_model:
            #print(pair[0])
                continue
            if pair[1] not in w2v_model:
            #print(pair[1])
                continue
            else:
                pair_scores.append( w2v_model.similarity(pair[0], pair[1]))
        # get the mean for all pairs in this topic
        if len(pair_scores) == 0:
            continue
        else:       
            topic_score = sum(pair_scores) / len(pair_scores)
            single_coherence.append(topic_score)
            overall_coherence += topic_score
    # get the mean score across all topics
    return single_coherence

def keep(speech, list_drop):
    keep = [ele for ele in speech if all(ch not in ele for ch in list_drop)]
    return keep