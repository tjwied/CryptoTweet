from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import json
import pickle
import re
import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import pylab as pl
from networkx.algorithms.community import k_clique_communities

def build_graph(filepathtocsv):

    csv_extract = os.path.basename(filepathtocsv)
    basename_extract = os.path.basename(filepathtocsv[:-4])
    print(filepathtocsv)

    x = pd.read_csv(filepathtocsv)   # SWITCH OUT FOR VARIABLE
    y = x.dropna()

    sentences = y.loc[:, 'text']
    text = y.loc[:, 'text']
    users = y.loc[: , "username"]

    senders = []
    for user in users:
        if user not in senders:
            senders.append(user)

    def getWords(text):
        return re.compile('.\w+').findall(text)

    receiver = []
    i = 0
    for element in text:
        if element != None:
            words = getWords(element)
        for word in words:
            if word[0] == '@':
                if word[1:] not in receiver:
                    receiver.append(word[1:])

    total = []
    for element in receiver:
        total.append(element)
    for element in senders:
        if element not in total:
            total.append(element)

    interaction = []
    for index, row in x.iterrows():
        string = str(row['text'])
        user = str(row['username'])
        words = getWords(string)
        if len(words) > 0:
            if words[0] != 'RT':
                for element in words:
                    if element[0] == '@':
                        if (user, element[1:]) not in interaction:
                            interaction.append((user, element[1:]))

    G=nx.Graph()
    G.add_nodes_from(total)
    G.add_edges_from(interaction)

    betweenness = nx.betweenness_centrality(G)

    influencer = []
    for element in betweenness:
        if betweenness[element] > 0.0003:
            influencer.append(element)

    k = G.subgraph(influencer) 
    #nx.draw(k, with_labels=False, node_size=5);

    interaction = []
    sentiment_dic = {}
    times = {}
    analyzer = SentimentIntensityAnalyzer()
    for index, row in y.iterrows():
        string = str(row['text'])
        user = str(row['username'])
        words = getWords(string)
        sentiment = analyzer.polarity_scores(string)
        if user in sentiment_dic:
            sentiment_dic[user] += sentiment['compound']
        elif user not in sentiment_dic:
            sentiment_dic[user] = sentiment['compound']
        if user in times:
            times[user] += 1
        elif user not in times:
            times[user] = 1

    normalize = {}
    for element in sentiment_dic:
        amount = times[element]
        normalize[element] = sentiment_dic[element] / times[element]

    nx.write_edgelist(k, path=basename_extract+'.grid', delimiter=":") #SWITCH OUT WITH VARIABLE NAME!!!!!

    def save_obj(name):
        with open('obj/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    pickle.dump(normalize, open( basename_extract+".pkl", "wb" ))
    pickle.dump(betweenness, open( basename_extract+"_between.pkl", "wb"))

