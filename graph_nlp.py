from gensim import corpora, models
import re
import gensim
import os
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from stop_words import get_stop_words

def topic_modeling(filepathtocsv):
    csv_extract = os.path.basename(filepathtocsv)
    basename_extract = os.path.basename(filepathtocsv[:-4])

    x = pd.read_csv(filepathtocsv)   # SWITCH OUT FOR VARIABLE
    y = x.dropna()
    doc_set = y.loc[: , "text"]
    p_stemmer = PorterStemmer()
    en_stop = get_stop_words('en')
    wordnet_lemmatizer = WordNetLemmatizer()
    tokenizer = RegexpTokenizer(r'\w+')
    en_stop.append('http')
    en_stop.append('https')
    en_stop.append('t')
    en_stop.append('que')
    en_stop.append('el')
    en_stop.append('1')
    en_stop.append('0')
    en_stop.append('co')
    en_stop.append('rt')
    en_stop.append('000')
    en_stop.append('o')
    en_stop.append('los')
    en_stop.append('s')
    # compile sample documents into a list
    texts = []
    for doc in doc_set:
        if doc != None:
            raw = doc.lower() #lowercase all letters
            tokens = tokenizer.tokenize(raw) #divide document into list of strings
            stopped_tokens = [i for i in tokens if not i in en_stop] #remove common words
            #stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens] #combine words of identical meanings
            lemmatized_tokens = [wordnet_lemmatizer.lemmatize(i) for i in stopped_tokens]
            texts.append(lemmatized_tokens)

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    #lda_model = gensim.models.LdaMulticore(corpus, num_topics=10, id2word=dictionary, passes=2, workers=2)

    lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=20, id2word=dictionary, passes=2, workers=4)
    
    topics = []
    for top in lda_model_tfidf.print_topics(num_words=6):
        topics.append(top)

    topic_assignment = lda_model_tfidf[corpus]
    def getWords(text):
        return re.compile('".\w+"').findall(text)
    
    words = []
    for element in topics:
        words.append(getWords(element[1]))

    return(words)
