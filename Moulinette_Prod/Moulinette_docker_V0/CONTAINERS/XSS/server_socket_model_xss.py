import pandas as pd
import pickle
import socket
import threading
import tensorflow as tf  # Pour TensorFlow Lite
import time  # Pour mesurer le délai
from tensorflow.keras.preprocessing.sequence import pad_sequences
from _conf import HEART_XSS_IP, HEART_XSS_PORT, HEART_XSS_PARANOIA

###########################################################################
# Parameters 
###########################################################################

# Paths
token_path = 'xss.tokens'
tflite_model_path = 'model_xss_lite.tflite'  # Utiliser le modèle optimisé TFLite

# Model parameters
vocab_size = 8000
max_length = 300
embedding_dim = 16

# Socket parameters
HOST = HEART_XSS_IP
PORT = HEART_XSS_PORT

###########################################################################
# Testing the model
###########################################################################

# 1. Load the tokenizer
with open(token_path, 'rb') as file:
    tokenizer = pickle.load(file)

# 2. Load the TFLite model
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()  # Préparer le modèle TFLite

# Obtenir les détails des entrées/sorties
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# 3. Predict function using TFLite
def verify_query(query):
    # Tokenisation et padding de la requête
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_sequence = pad_sequences(query_sequence, maxlen=max_length, padding='post', truncating='post')
    
    # Assigner les données d'entrée
    interpreter.set_tensor(input_details[0]['index'], padded_sequence.astype('float32'))  # Assurez-vous du bon type

    # Mesurer le temps avant la prédiction
    start_time = time.time()
    
    # Effectuer la prédiction
    interpreter.invoke()
    
    # Mesurer le temps après la prédiction
    end_time = time.time()
    
    # Récupérer le résultat
    prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
    
    # Calculer le délai de réponse
    response_time = end_time - start_time
    print(f"[i] Prediction: {str(prediction)} (Delay: {response_time:.4f} secondes)")
    
    return str(prediction), response_time

###########################################################################
# Handle client connection
###########################################################################
def handle_client(conn, addr):
    try:
        with conn:
            # Receiving connections
            print(f"\n[NET-IN] --> Connected by {addr}")
            data = conn.recv(1024)
            # If healthcheck
            if data == b'HEALTHCHECK':
                print(f"[NET-IN] --> Healthcheck received from {addr}")
                print(f"[NET-OUT] --> Responded OK.")
                conn.sendall(b'OK')
                return
            if not data:
                print(f"[ERROR] No data received from {addr}")
                return
            # Decoding query
            query = data.decode('utf-8')
            print("[NET-IN] --> Query received:", query)
            # Verifying query
            print("[i] --> Verifying query...")
            score, response_time = verify_query(query)
            # Sending score
            print(f"[i] --> Score predicted: {score} (Delay: {response_time:.4f} secondes)")
            response = f"{score}"
            print(f"[NET-OUT] --> Sending response: {response}")
            conn.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] An error occurred with {addr}: {e}")

###########################################################################
# Socket server
###########################################################################
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("\n###############################################@")
    print(" ServerXSS listening on IP:", HOST, " Port:", PORT)
    print("###############################################@")
    while True:
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()