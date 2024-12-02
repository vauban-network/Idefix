from flask import Flask, request, jsonify
import numpy as np
import os
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import time 

import sys
sys.stdout.reconfigure(line_buffering=True)

# Modèle et port configurables
model_path = "general.tflite"
token_path = "general.tokens"
port = 3000
paranoia = 0.5  # Seuil de classification

# Charger le tokenizer
with open(token_path, 'rb') as file:
    tokenizer = pickle.load(file)

# Charger le modèle TensorFlow Lite
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Obtenir les détails des entrées et sorties
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Initialisation de l'application Flask
app = Flask(__name__)

def predict_with_tflite(query):
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_sequence = pad_sequences(query_sequence, padding='post', truncating='post', maxlen=input_details[0]['shape'][1])
    input_data = np.array(padded_sequence, dtype=np.float32)    
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_details[0]['index'])[0][0]
    return prediction

def analyze_field(key, value):
    if isinstance(value, str):  # Analyse uniquement les valeurs textuelles
        prediction = predict_with_tflite(value)        
        verdict = "MALICIOUS" if prediction > paranoia else "SAFE"
        if(verdict == "MALICIOUS"):
            print(f"Field: {key}, Value: {value}, Prediction: {prediction:.2f}, Verdict: {verdict}")
        return {"field": key, "value": value, "prediction": prediction, "verdict": verdict}
    else:
        return {"field": key, "value": value, "error": "Unsupported value type for analysis"}

def recursive_analysis(data, parent_key=""):
    results = []
    malicious_detected = False  # Vérifie si un champ est MALICIOUS

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, (dict, list)):
                sub_results, sub_malicious = recursive_analysis(value, full_key)
                results.extend(sub_results)
                malicious_detected = malicious_detected or sub_malicious
            else:
                result = analyze_field(full_key, value)
                results.append(result)
                if result.get("verdict") == "MALICIOUS":
                    malicious_detected = True
    elif isinstance(data, list):
        for index, item in enumerate(data):
            full_key = f"{parent_key}[{index}]"
            if isinstance(item, (dict, list)):
                sub_results, sub_malicious = recursive_analysis(item, full_key)
                results.extend(sub_results)
                malicious_detected = malicious_detected or sub_malicious
            else:
                result = analyze_field(full_key, item)
                results.append(result)
                if result.get("verdict") == "MALICIOUS":
                    malicious_detected = True
    else:
        result = analyze_field(parent_key, data)
        results.append(result)
        if result.get("verdict") == "MALICIOUS":
            malicious_detected = True

    return results, malicious_detected

@app.route('/', methods=['POST'])
def home():
    print("\n############# REQUEST RECEIVED ###################@")
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "Invalid input, JSON body is required"}), 400

        start_time = time.time()
        analysis_results, malicious_detected = recursive_analysis(json_data)
        overall_verdict = "MALICIOUS" if malicious_detected else "SAFE"
        if overall_verdict == "SAFE":
            print(f"Overall Verdict: {overall_verdict}")
        response_time_ms = (time.time() - start_time) * 1000
        print(f"Response Time: {response_time_ms:.2f} ms")
        print("############# END OF ANALYSIS ###################@")
        return overall_verdict, 200

    except Exception as e:
        return "ERROR, ITS YOUR FAULT : " + str(e), 500


if __name__ == '__main__':
    print("\n###############################################@")
    print("[INFO] MOULINETTE V2 - Developpement build")
    print("###############################################@")
    app.run(host='0.0.0.0', port=port)


