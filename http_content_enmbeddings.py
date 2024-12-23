import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Load the GloVe embeddings from the text file
def load_glove_model(glove_file, embedding_dim=50):
    embeddings_index = {}
    with open(glove_file, 'r', encoding='utf-8') as f:
        for line in f:
            values = line.split()
            word = values[0]
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs
    return embeddings_index

# Use the path to the 50-dimensional GloVe file
glove_model = load_glove_model('glove.6B.50d.txt', embedding_dim=50)

# Define text cleaning functions
def remove_unnecessary_words(s):
    tokenized_s = word_tokenize(s.lower())  # Convert to lowercase and tokenize
    add_to_stopwords = ['items', 'item', 'mails', 'mail', 'inboxes', 'inbox', 'threads', 'thread']
    to_remove = stopwords.words('english') + add_to_stopwords
    new_sent = [c for c in tokenized_s if c.isalnum() and c not in to_remove]
    return ' '.join(new_sent)

def remove_punctuation(s):
    return ''.join([char for char in s if char not in string.punctuation])

# Define vector embedding functions
def vector_rep(word, embedding_dim=50):
    return glove_model.get(word, np.zeros(embedding_dim))

def general_vector_rep(phrase, embedding_dim=50):
    tokenized = word_tokenize(phrase)
    if not tokenized:
        return np.zeros(embedding_dim)
    vectors = [vector_rep(word, embedding_dim) for word in tokenized if word in glove_model]
    return np.mean(vectors, axis=0) if vectors else np.zeros(embedding_dim)

# Load the CMU CERT email data
email_df = pd.read_csv("http_final.csv")

# Clean the email content and apply the embedding
email_df['content_cleaned'] = email_df['content'].apply(remove_unnecessary_words).apply(remove_punctuation)
email_df['content_vector'] = email_df['content_cleaned'].apply(lambda x: general_vector_rep(x, embedding_dim=50))

# Convert the embedded vectors into separate columns (c0, c1, ..., c49 for 50-dimensional embeddings)
embedded_df = pd.DataFrame(email_df['content_vector'].tolist(), columns=[f'c{i}' for i in range(50)])

# Concatenate the original email data (minus 'content') with the new embedded columns
email_df = pd.concat([email_df.drop(['content', 'content_cleaned'], axis=1), embedded_df], axis=1)

# Save to a new CSV file
email_df.to_csv("http_with_final.csv", index=False)
