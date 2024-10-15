#DEEP LEARNING
###########################################################################@
# This script generates the model_xss.h5 file and the xss.tokens file. 
###########################################################################@
import pandas as pd
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Dense, GlobalAveragePooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split

###########################################################################@
# Parameters 
###########################################################################@

#Paths
dataset_path = './Datasets/xss-dataset.csv'
token_path = './IA/Tokens/xss.tokens'
model_path = './IA/Models/model_xss.h5'

#Utils
verbose_mode = False

#Model parameters
vocab_size = 8000
max_length = 300
embedding_dim = 16

###########################################################################@
# Utils 
###########################################################################@
def print_verbose(text):
    if verbose_mode:
        print(text)
        
###########################################################################@
# Generating model
###########################################################################@
#1. Load the data
print("[i] Reading the dataset...")
data = pd.read_csv(dataset_path, delimiter=',')
queries = data['Sentence']
labels = data['Label']
print_verbose(data.columns)
print_verbose(queries.head())
print_verbose(labels.head())

#2. Initialize a tokenizer 
print("[i] Initializing dataset...")
tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
queries = queries.astype(str) 
tokenizer.fit_on_texts(queries)
query_sequences = tokenizer.texts_to_sequences(queries)
print_verbose(query_sequences[:5])

#3. Applying padding
print("[i] Applying padding...")
padded_sequences = pad_sequences(query_sequences, maxlen=max_length, padding='post', truncating='post')
print_verbose(padded_sequences[:5])

#4. Save tokenizer in file
print("[i] Saving .tokens file...")
with open(token_path, 'wb') as file:
    pickle.dump(tokenizer, file)

#5. Create the model
print("[i] Generating H5 model...")
model = Sequential([
    Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_length),
    GlobalAveragePooling1D(),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
X_train, X_test, y_train, y_test = train_test_split(padded_sequences, labels, test_size=0.2, random_state=42)
model.fit(X_train, y_train, epochs=5, validation_data=(X_test, y_test))
print("[i] Saving .h5 file...")
model.save(model_path)

print("\n###############################################@")
print("[DONE] Script executed successfully")
print("[i] Model trained and saved in: ", model_path)
print("[i] Tokenizer saved in", token_path)
print("###############################################@")