import time
from datetime import datetime
import tweepy
import pandas as pd
import numpy as np
import pickle
import json


enc = lambda x: x.encode('ascii', errors='ignore')

searchQuery = '"bitcoin"'
#searchQuery = '@rubisco_co2'


retweet_filter='-filter:retweets'

q = searchQuery+retweet_filter

tweetsPerQry = 100

fName = 'tweets.txt'

sinceId = None

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.
auth = tweepy.OAuthHandler('', '')
auth.set_access_token('', '')

api = tweepy.API(auth)

check = api.rate_limit_status()
reset_time = check['resources']['search']['/search/tweets']['reset']
import datetime
reset_formatted = datetime.datetime.fromtimestamp(reset_time).strftime('%X')
print(reset_formatted)
print(check['resources']['search'])

max_id = -1L
maxTweets = 75000

tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))
list_dic = []
with open(fName, 'w') as f:
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                tweetson = tweet._json
                #list_of_tweets.append(tweet._json)
                tweetdict = {}
                tweetdict['text'] = tweetson['text']
                tweetdict['mentions'] = tweetson['entities']['user_mentions']
                tweetdict['json'] = tweetson
                tweetdict['id'] = tweetson['id_str']
                tweetdict['username'] = tweetson['user']['screen_name']
                tweetdict['created_at'] = tweetson['created_at']
                #tweetdict['source'] = accountname
                list_dic.append(tweetdict)
            tweetCount += len(new_tweets)
            #print("Downloaded {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError:
            print 'Rate limited. Sleeping for 15 minutes.'
            time.sleep(15 * 60 + 15)
            continue



#a = open('testing1.json', 'w')
#json.dump([task for task in list_of_tweets], a)

df = pd.DataFrame(list_dic)
print(df)
df.to_csv('~/Desktop/search/bitcoin.csv', header=True, index=False, encoding='utf-8')

print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))
