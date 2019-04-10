"""
Generate network graphs and user sentiment scores from Tweets.
@author: tjwied
Usage: python build_graph.py
"""


from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import pickle
import re
import os
import glob
import networkx as nx


csv_list = glob.glob("/home/rubisco/Desktop/insight/dash/final/csv/*.csv")

# == Simple function to find all words in Tweets ==
#

def getWords(text):
    return re.compile('.\w+').findall(text)



# == Generates lists of Twitter accounts that sent or received Tweets ==
#

def tweeters(users, text):

    total = [] # All users who sent or received Tweets
    senders = [] # Users who SENT Tweets
    for user in users:
        if user not in senders:
            senders.append(user)
            total.append(user)
    
    receiver = [] # Users who RECEIVED Tweets
    i = 0
    for element in text:
        if element != None:
            words = getWords(element)
        for word in words:
            if word[0] == '@':
                if word[1:] not in receiver:
                    receiver.append(word[1:])
                    total.append(word[1:])
    return senders, receiver, total


# Calculate a per-user average sentiment score
#

def sentiment_score(tweets):
    
    # Iterate over all Tweets and assign raw sentiment score to each user
    sentiment_dic = {}
    times = {}
    analyzer = SentimentIntensityAnalyzer()
    for index, row in tweets.iterrows():
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

    # Calculate user average sentiment: divide each users raw sentiment score by the number of Tweets they sent 
    normalize = {}
    for element in sentiment_dic:
        amount = times[element]
        normalize[element] = sentiment_dic[element] / times[element]

    return normalize


# == Generates graph ==
#

def build_graph(filepathtocsv):

    # Open CSV file and create dataframe from data
    csv_extract = os.path.basename(filepathtocsv)
    basename_extract = os.path.basename(filepathtocsv[:-4])
    x = pd.read_csv(filepathtocsv)   # SWITCH OUT FOR VARIABLE
    y = x.dropna()

    normalize = sentiment_score(y)

    # Extract text of tweets and users that sent them
    text = y.loc[:, 'text']
    users = y.loc[: , "username"]
    senders, receiver, total = tweeters(users, text) 


    # Generates a list of interactions between users
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


    # Initialize graph from users (nodes) and interactions (edges)
    G=nx.Graph()
    G.add_nodes_from(total)
    G.add_edges_from(interaction)

    # Filter nodes by centrality criterion
    # This is SLOW!
    betweenness = nx.betweenness_centrality(G)
    influencer = []
    for element in betweenness:
        if betweenness[element] > 0.0003: #This betweenness parameter can be tuned. Higher values = higher strigency for importance.
            influencer.append(element)

    # Subgraph k of only filtered nodes
    k = G.subgraph(influencer) 

    normalize = sentiment_score(y)

    #Write out files that will be used by dash_app.py visualization
    nx.write_edgelist(k, path=basename_extract+'.grid', delimiter=":") 
    pickle.dump(normalize, open( basename_extract+".pkl", "wb" ))
    pickle.dump(betweenness, open( basename_extract+"_between.pkl", "wb"))

if __name__ == "__main__":
    for element in csv_list:
        build_graph(element)
