import os
import pandas as pd
import pickle
import time
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from tqdm import tqdm  # Pour les barres de progression

###########################################################################@
# Parameters 
###########################################################################@

# Paths
token_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Tokens/general.tokens'
model_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Models/model_general.h5'

# Attack types and corresponding files
attack_files = {
    "GENERAL": {
        "safe": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/general-safe-list.txt',
        "malicious": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/general-payload-list.txt'
    },
    "XSS": {
        "safe": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/xss-safe-list.txt',
        "malicious": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/xss-payload-list.txt'
    },
    "SQL": {
        "safe": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/sql-safe-list.txt',
        "malicious": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/sql-payload-list.txt'
    },
    "TRAVERSAL": {
        "safe": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/traversal-safe-list.txt',
        "malicious": '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/traversal-payload-list.txt'
    },
}

# Limits
test_limits = {
    "safe": 100,  # Limite pour les requêtes SAFE
    "malicious": 10000  # Limite pour les requêtes MALICIOUS
}

# Model parameters
paranoia = 0.5

###########################################################################@
# Functions
###########################################################################@

# Vérification des fichiers
def verify_files_exist(token_path, model_path, attack_files):
    missing_files = []
    
    # Vérifier le tokenizer et le modèle
    if not os.path.isfile(token_path):
        missing_files.append(token_path)
    if not os.path.isfile(model_path):
        missing_files.append(model_path)
    
    # Vérifier les fichiers pour chaque type d'attaque
    for attack, paths in attack_files.items():
        for query_type, file_path in paths.items():
            if not os.path.isfile(file_path):
                missing_files.append(file_path)
    
    # Retourner les fichiers manquants
    if missing_files:
        print("Les fichiers suivants sont manquants :")
        for file in missing_files:
            print(f" - {file}")
        raise FileNotFoundError("Tous les fichiers nécessaires ne sont pas présents. Vérifiez les chemins ci-dessus.")
    else:
        print("Tous les fichiers nécessaires sont présents.")

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
        return "MALICIOUS"
    else:
        return "SAFE"

# 4. Read queries from a file with a limit
def read_queries(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines

# 5. Evaluate accuracy and average time
def evaluate_accuracy(queries, expected_verdict, description):
    correct_predictions = 0
    total_queries = len(queries)
    total_time = 0  # Accumulate total processing time

    with tqdm(total=total_queries, desc=description, unit="query") as pbar:
        for i, query_text in enumerate(queries):
            start_time = time.time()
            verdict = verify_query(query_text)
            end_time = time.time()

            # Calculate time for this query
            total_time += (end_time - start_time)

            if verdict == expected_verdict:
                correct_predictions += 1
            accuracy = (correct_predictions / (i + 1)) * 100
            pbar.set_postfix(accuracy=f"{accuracy:.2f}%")
            pbar.update(1)
    
    avg_time = (total_time / total_queries) * 1000 if total_queries > 0 else 0  # Convert to milliseconds
    return correct_predictions, total_queries, avg_time

###########################################################################@
# Main testing loop
###########################################################################@

# Vérifier les fichiers avant de lancer les tests
verify_files_exist(token_path, model_path, attack_files)

attack_results = {}  # Pour stocker les résultats par attaque

for attack, paths in attack_files.items():
    print(f"\n###############################################@")
    print(f" Testing the model for {attack} attacks")
    print(f"###############################################@")
    
    attack_results[attack] = {}

    combined_total_time = 0
    combined_total_queries = 0

    # Test SAFE queries
    safe_queries = read_queries(paths["safe"], limit=test_limits["safe"])
    correct, total, avg_time = evaluate_accuracy(safe_queries, "SAFE", f"{attack} SAFE queries")
    attack_results[attack]["safe_accuracy"] = (correct / total) * 100 if total > 0 else 0
    combined_total_time += avg_time * total  # Weighted total time
    combined_total_queries += total

    # Test MALICIOUS queries
    malicious_queries = read_queries(paths["malicious"], limit=test_limits["malicious"])
    correct, total, avg_time = evaluate_accuracy(malicious_queries, "MALICIOUS", f"{attack} MALICIOUS queries")
    attack_results[attack]["malicious_accuracy"] = (correct / total) * 100 if total > 0 else 0
    combined_total_time += avg_time * total  # Weighted total time
    combined_total_queries += total

    # Calculate overall average time for this attack
    attack_results[attack]["avg_time"] = combined_total_time / combined_total_queries if combined_total_queries > 0 else 0

###########################################################################@
# General statistics
###########################################################################@

print("\n###############################################@")
print(" Final Statistics")
print("###############################################@")
for attack, results in attack_results.items():
    print(f"Attack: {attack}")
    print(f"  SAFE Accuracy: {results['safe_accuracy']:.2f}%")
    print(f"  MALICIOUS Accuracy: {results['malicious_accuracy']:.2f}%")
    print(f"  Avg Time (SAFE + MALICIOUS): {results['avg_time']:.2f} ms")
    print("")
