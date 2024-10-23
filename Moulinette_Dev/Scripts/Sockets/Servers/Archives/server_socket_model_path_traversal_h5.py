
###########################################################################@
# This script is the server for the XSS MODEL
###########################################################################@
import pandas as pd
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import socket
from _conf import HEART_XSS_IP, HEART_XSS_PORT, HEART_XSS_PARANOIA, HEART_PATH_TRAVERSAL_PORT, HEART_PATH_TRAVERSAL_IP
###########################################################################@
# Parameters 
###########################################################################@

#Paths
token_path = './IA/Tokens/xss.tokens'
model_path = './IA/Models/model_xss.h5'

#Model parameters
#paranoia = HEART_XSS_PARANOIA
vocab_size = 10000
max_length = 500
embedding_dim =32

# Socket parameters
HOST = HEART_PATH_TRAVERSAL_IP
PORT = HEART_PATH_TRAVERSAL_PORT

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
    print(str(result))
    return str(result)

###########################################################################@
# Socket server
###########################################################################@
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("\n###############################################@")
    print(" Server XSS listening on IP:", HOST, " Port:", PORT)
    print("###############################################@")
    print("###############################################@")
    while True:
        conn, addr = s.accept()
        try:
            with conn:
                #Receiving connections
                print(f"\n[NET-IN] --> Connected by {addr}")
                data = conn.recv(1024)
                #If healthcheck
                if(data == b'HEALTHCHECK'):
                    print(f"[NET-IN] --> Healthcheck received from {addr}")
                    print(f"[NET-OUT] --> Responded OK.")
                    conn.sendall(b'OK')
                    continue
                if not data:
                    print(f"[ERROR] No data received from {addr}")
                #Decoding query
                query = data.decode('utf-8')
                print("[NET-IN] --> Query received:", query)
                #Verifying query
                print("[i] --> Verifying query...")
                score = verify_query(query)
                #Sending score
                print(f"[i] --> Score predicted: {score}")
                response = f"{score}"
                print(f"[NET-OUT] --> Sending response: {response}")
                conn.sendall(response.encode('utf-8'))
                conn.close()
        except Exception as e:
            print(f"[ERROR] An error occurred with {addr}: {e}")
