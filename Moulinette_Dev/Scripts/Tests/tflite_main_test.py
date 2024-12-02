import os
import pandas as pd
import pickle
import numpy as np
import time
from tqdm import tqdm  # Pour les barres de progression
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences

###########################################################################@
# Parameters 
###########################################################################@

# Paths
token_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Tokens/general.tokens'
model_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/IA/Models/model_general_lite.tflite'

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
    "safe": 10000,  # Limite pour les requêtes SAFE
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
    
    if not os.path.isfile(token_path):
        missing_files.append(token_path)
    if not os.path.isfile(model_path):
        missing_files.append(model_path)
    
    for attack, paths in attack_files.items():
        for query_type, file_path in paths.items():
            if not os.path.isfile(file_path):
                missing_files.append(file_path)
    
    if missing_files:
        print("Les fichiers suivants sont manquants :")
        for file in missing_files:
            print(f" - {file}")
        raise FileNotFoundError("Tous les fichiers nécessaires ne sont pas présents. Vérifiez les chemins ci-dessus.")
    else:
        print("Tous les fichiers nécessaires sont présents.")

# Chargement du tokenizer
with open(token_path, 'rb') as file:
    tokenizer = pickle.load(file)

# Chargement du modèle TFLite
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Fonction de prédiction
def verify_query(query):
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_sequence = pad_sequences(query_sequence, padding='post', truncating='post', maxlen=input_details[0]['shape'][1])
    interpreter.set_tensor(input_details[0]['index'], padded_sequence.astype(np.float32))
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_details[0]['index'])
    result = prediction[0][0]
    if result > paranoia:
        return "MALICIOUS"
    else:
        return "SAFE"

# Lecture des requêtes
def read_queries(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines

# Évaluation de la précision et du délai moyen
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
    
    return correct_predictions, total_queries, total_time

###########################################################################@
# Main testing loop
###########################################################################@

# Vérifier les fichiers avant de lancer les tests
verify_files_exist(token_path, model_path, attack_files)

attack_results = {}

for attack, paths in attack_files.items():
    print(f"\n###############################################@")
    print(f" Testing the model for {attack} attacks")
    print(f"###############################################@")
    
    attack_results[attack] = {}

    # Combiner SAFE et MALICIOUS pour calculer le délai moyen global
    combined_total_time = 0
    combined_total_queries = 0

    # Test SAFE queries
    safe_queries = read_queries(paths["safe"], limit=test_limits["safe"])
    correct, total, total_time = evaluate_accuracy(safe_queries, "SAFE", f"{attack} SAFE queries")
    attack_results[attack]["safe_accuracy"] = (correct / total) * 100 if total > 0 else 0
    combined_total_time += total_time
    combined_total_queries += total

    # Test MALICIOUS queries
    malicious_queries = read_queries(paths["malicious"], limit=test_limits["malicious"])
    correct, total, total_time = evaluate_accuracy(malicious_queries, "MALICIOUS", f"{attack} MALICIOUS queries")
    attack_results[attack]["malicious_accuracy"] = (correct / total) * 100 if total > 0 else 0
    combined_total_time += total_time
    combined_total_queries += total

    # Calcul du délai moyen global
    attack_results[attack]["avg_time"] = (combined_total_time / combined_total_queries) * 1000 if combined_total_queries > 0 else 0

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
    print(f"  Avg Time : {results['avg_time']:.2f} ms")
    print("")
