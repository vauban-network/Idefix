import socket
import time
from tqdm import tqdm

###########################################################################
# Parameters 
###########################################################################
HOST = '127.0.0.1'  
PORT = 3000      

# Paths
safe_payload_file_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/xss-safe-list.txt'  # Path to the SQL safe payload file
malicious_payload_file_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/xss-payload-list.txt'  # Path to the SQL malicious payload file

limit_test = 10000  # Limit for malicious queries

###########################################################################
# Read payloads from file
###########################################################################
def read_payloads(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines

safe_payloads = read_payloads(safe_payload_file_path)
malicious_payloads = read_payloads(malicious_payload_file_path, limit=limit_test)

total_requests = len(safe_payloads) + len(malicious_payloads)  # Get total number of requests

###########################################################################
# Testing the server
###########################################################################
print("\n###############################################@")
print(" Client asking server SQL:", HOST, " Port:", PORT)
print("###############################################@")

start_time = time.time()
response_count = 0
count = 0
safe_correct = 0
malicious_correct = 0

# tqdm for the loading bar
with tqdm(total=total_requests, desc="Processing stress-test", unit=" queries") as pbar:
    # Test safe queries
    for query in safe_payloads:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            count += 1
            s.connect((HOST, PORT))
            s.sendall(query.encode('utf-8'))
            
            # Receiving response
            data = s.recv(1024)
            verdict = data.decode('utf-8').strip()

            #print(f"[SAFE] [{count}] Server response: {verdict}")
            if "SAFE" in verdict:
                safe_correct += 1

            # Closing socket
            s.close()
            
            # Update loading bar
            response_count += 1
            pbar.update(1)

    # Test malicious queries
    for query in malicious_payloads:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            count += 1
            s.connect((HOST, PORT))
            s.sendall(query.encode('utf-8'))
            
            # Receiving response
            data = s.recv(1024)
            verdict = data.decode('utf-8').strip()

            #print(f"[MALICIOUS] [{count}] Server response: {verdict}")
            if "MALICIOUS" in verdict:
                malicious_correct += 1

            # Closing socket
            s.close()

            # Update loading bar
            response_count += 1
            pbar.update(1)

# Statistics calculation
total_safe = len(safe_payloads)
total_malicious = len(malicious_payloads)

safe_accuracy = (safe_correct / total_safe) * 100
malicious_accuracy = (malicious_correct / total_malicious) * 100

end_time = time.time()
duration = end_time - start_time
responses_per_second = response_count / duration

print("\n###############################################@")
print(" Statistics")
print("###############################################@")
print(f"Safe queries success rate: {safe_accuracy:.2f}%")
print(f"Malicious queries success rate: {malicious_accuracy:.2f}%")
print(f"Total duration: {duration:.2f} seconds")
print(f"Responses per second: {responses_per_second:.2f}")