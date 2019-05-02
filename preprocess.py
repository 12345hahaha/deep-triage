import numpy as np
np.random.seed(1337)
import json, re, nltk, string
from nltk.corpus import wordnet
from gensim.models import Word2Vec


def clean_word_list(item):
    #1. Remove \r 
    current_title = item['issue_title'].replace('\r', ' ')
    current_desc = item['description'].replace('\r', ' ')    
    #2. Remove URLs
    current_desc = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', current_desc)    
    #3. Remove Stack Trace
    start_loc = current_desc.find("Stack trace:")
    current_desc = current_desc[:start_loc]    
    #4. Remove hex code
    current_desc = re.sub(r'(\w+)0x\w+', '', current_desc)
    current_title= re.sub(r'(\w+)0x\w+', '', current_title)    
    #5. Change to lower case
    current_desc = current_desc.lower()
    current_title = current_title.lower()    
    #6. Tokenize
    current_desc_tokens = nltk.word_tokenize(current_desc)
    current_title_tokens = nltk.word_tokenize(current_title)
    #7. Strip trailing punctuation marks    
    current_desc_filter = [word.strip(string.punctuation) for word in current_desc_tokens]
    current_title_filter = [word.strip(string.punctuation) for word in current_title_tokens]      
    #8. Join the lists
    current_data = current_title_filter + current_desc_filter
    current_data = [x for x in current_data if x]#list(filter(None, current_data))

    return current_data

# The JSON file location containing the data for deep learning model training as follows:
open_bugs_json = './data/chrome/deep_data.json'

# Word2vec parameters
min_word_frequency_word2vec = 5
embed_size_word2vec = 200
context_window_word2vec = 5

# The bugs are loaded from the JSON file and the preprocessing is performed as follows:

with open(open_bugs_json) as data_file:
    data = json.load(data_file, strict=False)

all_data = []
for item in data:
    current_data =clean_word_list(item)
    all_data.append(current_data)  

# A vocabulary is constructed and the word2vec model is learnt using the preprocessed data. The word2vec model provides a semantic word representation for every word in the vocabulary.
wordvec_model = Word2Vec(all_data, min_count=min_word_frequency_word2vec, size=embed_size_word2vec, window=context_window_word2vec)
vocabulary = wordvec_model.wv.vocab
vocab_size = len(vocabulary)

# Save word2vec model to use in the model again and again
wordvec_model.save("./data/chrome/word2vec.model")

# The data used for training and testing the classifier is loaded and the preprocessing is performed as follows:
for min_train_samples_per_class in [0,5,10,20]:
    closed_bugs_json = './data/chrome/classifier_data_{0}.json'.format(min_train_samples_per_class)

    with open(closed_bugs_json) as data_file:
        data = json.load(data_file, strict=False)

    all_data = []
    all_owner = []    
    for item in data:
        current_data = clean_word_list(item)
        all_data.append(current_data)
        all_owner.append(item['owner'])

    # Save all data arrays to use in the model again and again
    np.save("./data/chrome/all_data_{0}.npy".format(min_train_samples_per_class), all_data)
    np.save("./data/chrome/all_owner_{0}.npy".format(min_train_samples_per_class), all_owner)