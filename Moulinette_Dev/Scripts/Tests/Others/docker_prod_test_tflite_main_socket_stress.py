import socket
import time
from tqdm import tqdm  # Importing tqdm for loading bar

###########################################################################
# Parameters 
###########################################################################
HOST = '127.0.0.1'  
PORT = 3000      

###########################################################################
# Testing the server
###########################################################################
print("\n###############################################@")
print(" Client asking to server SQL:", HOST, " Port:", PORT)
print("###############################################@")

# Readfile 
mix_payload_file_path = '/Users/enilles/Documents/Projet5A/Idefix/Moulinette_Dev/Scripts/Tests/Samples/stress-payload-docker-prod.txt'  # Path to the XSS payload file
def read_mix_payloads(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines

payloads = read_mix_payloads(mix_payload_file_path)
total_requests = len(payloads)  # Get total number of requests

start_time = time.time()
response_count = 0
count = 0

# tqdm for the loading bar
with tqdm(total=total_requests, desc="Processing stress-test", unit=" queries") as pbar:
    for query in payloads:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            count += 1
            s.connect((HOST, PORT))
            s.sendall(query.encode('utf-8'))
            
            # Receiving response
            data = s.recv(1024)
            data.decode('utf-8')
            
            # You can uncomment this line if you want specific outputs:
            # print(f'[{count}] Server response:', data.decode('utf-8'))  
            
            # In case you want to suppress all output, leave it commented.
            response_count += 1

            # Closing socket
            s.close()
            
            # Update the loading bar and calculate rate per second
            elapsed_time = time.time() - start_time
            rate_per_second = response_count / elapsed_time if elapsed_time > 0 else 0
            pbar.set_postfix({'Total rate:': f'{rate_per_second:.2f}'})
            pbar.update(1)  # Move the loading bar forward by 1

end_time = time.time()
duration = end_time - start_time
responses_per_second = response_count / duration

print(f"\nTotal responses: {response_count}")
print(f"Total duration: {duration:.2f} seconds")
print(f"Responses per second: {responses_per_second:.2f}")