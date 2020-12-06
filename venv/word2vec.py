import re  # For preprocessing
import pandas as pd  # For data handling
from time import time  # To time our operations
from collections import defaultdict  # For word frequency
import spacy
from gensim.models.phrases import Phrases, Phraser
import multiprocessing
from gensim.models import Word2Vec

nlp = spacy.load("en_core_web_sm" ,disable=['ner', 'parser'])
df = pd.read_csv(r"E:\Desktop Novembre 2020\wikidata.csv", sep=';', header=None)
print(df.shape)


def cleaning(doc):
    txt = [token.lemma_ for token in doc if not token.is_stop]
    if len(txt) > 2:
        return ' '.join(txt)

t = time()

txt = [cleaning(doc) for doc in nlp.pipe((re.sub("[^A-Za-z']+", ' ', str(row)).lower() for row in df[1]), batch_size=5000, n_threads=-1)]

print('Time to clean up everything: {} mins'.format(round((time() - t) / 60, 2)))
df_clean = pd.DataFrame({'clean': txt})
df_clean = df_clean.dropna().drop_duplicates()
df_clean.shape
sent = [row.split() for row in df_clean['clean']]
bigram = Phrases(sent, min_count=30, progress_per=10000)
sentences = bigram[sent]
word_freq = defaultdict(int)

for sent in sentences:
    for i in sent:
        word_freq[i] += 1
len(word_freq)
print(str(sorted(word_freq, key=word_freq.get, reverse=True)[:10]))
cores = multiprocessing.cpu_count()
'''
PRECEDENTE
w2v_model = Word2Vec(min_count=20,
                     window=2,
                     size=300,
                     sample=6e-5,
                     alpha=0.03,
                     min_alpha=0.0007,
                     negative=20,
                     workers=cores-1,
                     sg = 1)
'''
#ATTUALE
w2v_model = Word2Vec(min_count=50,
                     window=2,
                     size=600,
                     sample=6e-5,
                     alpha=0.03,
                     min_alpha=0.0007,
                     negative=20,
                     workers=cores-1,
                     sg = 1)
t = time()

w2v_model.build_vocab(sentences, progress_per=10000)

print('Time to build vocab: {} mins'.format(round((time() - t) / 60, 2)))

t = time()

w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)

print('Time to train the model: {} mins'.format(round((time() - t) / 60, 2)))

print(str(w2v_model.wv.most_similar(positive=["action"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["detective"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["trip"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["killer"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["policeman"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["cowboy"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["zombie"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["christmas"])))
print('\n')
print(str(w2v_model.wv.most_similar(positive=["ghost"])))
print('\n')

w2v_model.save('word2vec.model')