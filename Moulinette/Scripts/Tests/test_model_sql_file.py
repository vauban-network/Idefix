###########################################################################@
# This script is for testing the model_sql.h5 file with file input
###########################################################################@
import pandas as pd
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

###########################################################################@
# Parameters 
###########################################################################@

#Paths
token_path = './IA/Tokens/sql.tokens'
model_path = './IA/Models/model_sql.h5'
xss_payload_file_path = './Scripts/Tests/Samples/sql-payload-list.txt'  # Path to the SQL payload file

#Test
limit_test = 10000
#Model parameters
paranoia = 0.8
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

#5. List of SAFE queries to test
print("\n###############################################@")
print(" Testing the model with SAFE queries")
print("###############################################@")
queries_known_as_safe = [
'SELECT banner FROM v$version WHERE banner LIKE ‘Oracle%’;',
'SELECT banner FROM v$version WHERE banner LIKE ‘TNS%’;',
'SELECT version FROM v$instance;',
'SELECT 1 FROM users -- comment',
'SELECT username FROM all_users ORDER BY username;',
'SELECT name FROM sys.user$; — priv',
'SELECT name FROM v$database;',
'SELECT instance_name FROM v$instance;',
'SELECT column_name FROM all_tab_columns WHERE table_name = ‘blah’ and owner = ‘your_schema_name’;',
'SELECT table_name FROM all_tables;',
'SELECT owner, table_name FROM all_tables;',
'SELECT first_name || ' ' || last_name AS full_name FROM employees;',
'SELECT UTL_INADDR.get_host_address(‘microsoft.com’) FROM dual;',
'SELECT UTL_HTTP.REQUEST(‘<http://microsoft.com>’) FROM dual;'
]

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
