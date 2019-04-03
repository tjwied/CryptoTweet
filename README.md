# Combine network analysis, sentiment analysis and topic modeling on Twitter

Scrape tweets, build graphs, identify central users, generate list of trending topics and gauge user sentiment. Visualize and interact with networks in a local Dash webapp.

### How to use.

Before running "dash_app.py", which is the visualization app, you must run two scripts:

1. Scrape Tweets with "tweet_scrape.py". You will need to obtain an API developer key from Twitter (this is free). Modify the 'searchQuery' field for keywords of interest. Currenty this will scrape 75,000 Tweets matching the keyword, or approx. 1 week, whichever comes first. Tweets will be saved to the file denoted in "df.to_csv". Make sure CSV files are saved to CSV directory.

2. Run "build_graph.py" script to initialize graph and generate sub-graph of important nodes based on network centrality.

3. Finally, run "dash_app.py" with python and navigate to localhost (http://127.0.0.1:8050/) in web browser.

### Required python libraries

tweepy, pandas, numpy, pickle, gensim, nltk, stop_words, dash, dash_html_components, dash_core_components, plotly, networkx, matplotlib, vaderSentiment

### Notes on Dash visualization:

Nodes are colored by user-averaged sentiment score (Red = negative sentiment, Blue = positive sentiment). Size of node corresponds to number of connections. Top 20 users and topics for each network is listed below. 
