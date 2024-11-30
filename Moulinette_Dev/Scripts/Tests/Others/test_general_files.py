import pandas as pd
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from tqdm import tqdm  # Pour les barres de progression

###########################################################################@
# Parameters 
###########################################################################@

# Paths
token_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Tokens/general.tokens'
model_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Models/model_general.h5'
safe_queries_file_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/general-safe-queries.txt'  # Path to the SAFE queries file
malicious_queries_file_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/xss-payload-list.txt'  # Path to the MALICIOUS queries file

# Limits
safe_limit = 20  # Limite pour le fichier SAFE
malicious_limit = 100000  # Limite pour le fichier MALICIOUS

# Model parameters
paranoia = 0.5


###########################################################################@
# Testing the model
###########################################################################@

# 1. Load the tokenizer
with open(token_path, 'rb') as file:
    tokenizer = pickle.load(file)

# 2. Load the model
model = load_model(model_path)

# 3. Predict function
def verify_query(query):
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_sequence = pad_sequences(query_sequence, padding='post', truncating='post')
    prediction = model.predict(padded_sequence, verbose=0)
    result = prediction[0][0]
    if result > paranoia:
        return "Verdict: MALICIOUS, Score: " + str(result), "MALICIOUS"
    else:
        return "Verdict: SAFE, Score: " + str(result), "SAFE"

# 4. Read queries from a file with a limit
def read_queries(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines

# 5. Test SAFE queries
print("\n###############################################@")
print(" Testing the model with SAFE queries")
print("###############################################@")
queries_known_as_safe = read_queries(safe_queries_file_path, limit=safe_limit)

safe_correct = 0
total_safe = len(queries_known_as_safe)
with tqdm(total=total_safe, desc="SAFE queries progress", unit="query") as pbar:
    for i, query_text in enumerate(queries_known_as_safe):
        result, verdict = verify_query(query_text)
        if verdict == "SAFE":
            safe_correct += 1
        # Mise à jour de l'affichage de la barre avec l'accuracy
        accuracy = (safe_correct / (i + 1)) * 100
        pbar.set_postfix(accuracy=f"{accuracy:.2f}%")
        pbar.update(1)

# 6. Test MALICIOUS queries
print("\n###############################################@")
print(" Testing the model with MALICIOUS queries")
print("###############################################@")
queries_known_as_malicious = read_queries(malicious_queries_file_path, limit=malicious_limit)

malicious_correct = 0
total_malicious = len(queries_known_as_malicious)
with tqdm(total=total_malicious, desc="MALICIOUS queries progress", unit="query") as pbar:
    for i, query_text in enumerate(queries_known_as_malicious):
        result, verdict = verify_query(query_text)
        if verdict == "MALICIOUS":
            malicious_correct += 1
        # Mise à jour de l'affichage de la barre avec l'accuracy
        accuracy = (malicious_correct / (i + 1)) * 100
        pbar.set_postfix(accuracy=f"{accuracy:.2f}%")
        pbar.update(1)

# 7. Calculate and print statistics
safe_accuracy = (safe_correct / total_safe) * 100 if total_safe > 0 else 0
malicious_accuracy = (malicious_correct / total_malicious) * 100 if total_malicious > 0 else 0

print("\n###############################################@")
print(" Statistics")
print("###############################################@")
print(f"Safe queries success rate: {safe_accuracy:.2f}%")
print(f"Malicious queries success rate: {malicious_accuracy:.2f}%")
print("")
