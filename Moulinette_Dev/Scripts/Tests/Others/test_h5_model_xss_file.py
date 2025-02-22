###########################################################################@
# This script is for testing the model_xss.h5 file with file input
###########################################################################@
import pandas as pd
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

###########################################################################@
# Parameters 
###########################################################################@

#Paths
token_path = './IA/Tokens/xss.tokens'
model_path = './IA/Models/model_xss.h5'
xss_payload_file_path = './Scripts/Tests/Samples/xss-payload-list.txt'  # Path to the XSS payload file
xss_safe_file_path = './Scripts/Tests/Samples/xss-safe-list.txt'  # Path to the XSS safe file
#Test
limit_test = 1000
#Model parameters
paranoia = 0.5
vocab_size = 8000
max_length = 300
embedding_dim = 16

###########################################################################@
# Testing the model
###########################################################################@

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
        return "Verdict: MALICIOUS, Score:"+ str(result), "MALICIOUS"
    else:
        return "Verdict: SAFE, Score:"+ str(result), "SAFE" 

#4. Read XSS payloads from file with a limit
def read_xss_payloads(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines
    
#4. Read XSS safe from file with a limit
def read_xss_safe(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines

#5. List of SAFE queries to test
print("\n###############################################@")
print(" Testing the model with SAFE queries")
print("###############################################@")
queries_known_as_safe = read_xss_safe(xss_safe_file_path, limit=limit_test)

safe_correct = 0
for query_text in queries_known_as_safe:
    result, verdict = verify_query(query_text)
    print(f"This query is considered as : {result}")
    if verdict == "SAFE":
        safe_correct += 1

#6. List of MALICIOUS queries to test
print("\n###############################################@")
print(" Testing the model with MALICIOUS queries")
print("###############################################@")
queries_known_as_malicious = read_xss_payloads(xss_payload_file_path, limit=limit_test)

malicious_correct = 0
total = 0
for query_text in queries_known_as_malicious:
    result, verdict = verify_query(query_text)
    total += 1
    print(f"[{total}] --> This query is considered as : {result}")
    if verdict == "MALICIOUS":
        malicious_correct += 1

#7. Calculate and print statistics
total_safe = len(queries_known_as_safe)
total_malicious = len(queries_known_as_malicious)

safe_accuracy = (safe_correct / total_safe) * 100
malicious_accuracy = (malicious_correct / total_malicious) * 100

print("\n###############################################@")
print(" Statistics")
print("###############################################@")
print(f"Safe queries success rate: {safe_accuracy:.2f}%")
print(f"Malicious queries success rate: {malicious_accuracy:.2f}%")
print("")
