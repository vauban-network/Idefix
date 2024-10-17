###########################################################################@
# This script is the client example for stresstest
###########################################################################@
import socket
import time

###########################################################################@
# Parameters 
###########################################################################@
HOST = '127.0.0.1'  
PORT = 3000      

###########################################################################@
# Testing the server
###########################################################################@
print("\n###############################################@")
print(" Client asking to server SQL:", HOST, " Port:", PORT)
print("###############################################@")

# Readfile 
mix_payload_file_path = './Scripts/Tests/Samples/mix-payload-list.txt'  # Path to the XSS payload file
def read_mix_payloads(file_path, limit=None):
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
        if limit:
            lines = lines[:limit]
        return lines

payloads = read_mix_payloads(mix_payload_file_path)

start_time = time.time()
response_count = 0
count = 0
for query in payloads:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        count +=1
        s.connect((HOST, PORT))
        s.sendall(query.encode('utf-8'))
        # Receiving response
        data = s.recv(1024)
        data.decode('utf-8')
        # Printing answer
        if(data == "" or not data):
            data = "TIMEOUT".encode('utf-8')
        print(f'[{count}] Server response:', data.decode('utf-8'))
        response_count += 1
        # Closing socket
        s.close()

end_time = time.time()
duration = end_time - start_time
responses_per_second = response_count / duration

print(f"\nTotal responses: {response_count}")
print(f"Total duration: {duration:.2f} seconds")
print(f"Responses per second: {responses_per_second:.2f}")
