###########################################################################@
# This script is the server for the SQL MODEL
###########################################################################@
import pandas as pd
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import socket

###########################################################################@
# Parameters 
###########################################################################@

#Paths
token_path = './IA/Tokens/sql.tokens'
model_path = './IA/Models/model_sql.h5'

#Model parameters
paranoia = 0.8
vocab_size = 8000
max_length = 300
embedding_dim = 16

# Socket parameters
HOST = '127.0.0.1'  # Localhost
PORT = 3000         # Port to listen on

###########################################################################@
# Testing the model
###########################################################################@
#0. Deco

#1.Load the tokenizer
with open(token_path, 'rb') as file:
    tokenizer = pickle.load(file)
#2.Load the model
model = load_model(model_path)

#3. Predict function
def verify_query(query):
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_sequence = pad_sequences(query_sequence, maxlen=max_length, padding='post', truncating='post')
    prediction = model.predict(padded_sequence)
    result = prediction[0][0]
    if result > paranoia:
        print(str(result) + " Verdict: MALICIOUS")
        return str(result) + " Verdict: MALICIOUS", "MALICIOUS"
    else:
        print(str(result) + " Verdict: SAFE")
        return str(result) + " Verdict: SAFE", "SAFE"

###########################################################################@
# Socket server
###########################################################################@
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("\n###############################################@")
    print(" Server listening on IP:", HOST, " Port:", PORT)
    print("###############################################@")
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            data = conn.recv(1024)
            if not data:
                break
            query = data.decode('utf-8')
            print(query)
            result, verdict = verify_query(query)
            response = f"{result}\n"
            conn.sendall(response.encode('utf-8'))
