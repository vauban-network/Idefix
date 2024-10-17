from _conf import *
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

###########################################################################@
# Variables
###########################################################################@

# List of all hearts from _conf.py
list_of_hearts = HEARTS
# Main server configuration
HOST = MAIN_IP
PORT = MAIN_PORT
TIMEOUT_DELAY = MAIN_TIMEOUT_DELAY

###########################################################################@
# Functions
###########################################################################@

# Function to check if a heart is running
def check_heart_health(socket_name, socket_ip, socket_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_ip, socket_port))
            healthcheck_message = "HEALTHCHECK"
            s.sendall(healthcheck_message.encode('utf-8'))
            print(f"[OK] Socket {socket_name} is open")
            s.close()
            return True
    except Exception as e:
        print(f"[ERROR] Socket {socket_name} is closed: {e}")
        return False

# Function to query a single heart
def query_heart(heart_name, query):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            verdict = 404
            s.connect((globals()[f"HEART_{heart_name}_IP"], globals()[f"HEART_{heart_name}_PORT"]))
            s.sendall(query.encode('utf-8'))
            response = float(s.recv(1024).decode('utf-8'))
            if response > globals()[f"HEART_{heart_name}_PARANOIA"]:
                verdict = "1"
            else:
                verdict = "0"
            return (heart_name, response, verdict)
    except Exception as e:
        return (heart_name, "404", "404")

# Function to query the hearts and get the score
def check_query_to_hearts(query):
    responses = []
    with ThreadPoolExecutor() as executor:
        future_to_heart = {executor.submit(query_heart, heart_name, query): heart_name for heart_name in list_of_hearts}
        for future in as_completed(future_to_heart):
            heart_name = future_to_heart[future]
            try:
                response = future.result()
                responses.append(response)
            except Exception as e:
                responses.append((heart_name, "404", "404"))
    return responses

# Function to calculate the final result with scores from all hearts
def calculate_final_result(responses):
    has_one = False
    all_zeros = True
    all_404 = True
    for response in responses:
        if response[2] == "1":
            has_one = True
            all_zeros = False
        elif response[2] == "0":
            all_404 = False
        elif response[2] == "404":
            all_zeros = False
    if has_one:
        return "MALICIOUS"
    elif all_404:
        return "ERROR"
    elif all_zeros:
        return "SAFE"
    else:
        return "ERROR"

###########################################################################@
# Main code - Heart check and server start
###########################################################################@

# Checking if all hearts are running
print("\n###############################################@")
print("[i] Starting... Checking heart states...")
print("###############################################@")
all_hearts_running = True
for heart_name in list_of_hearts:
    if not check_heart_health(heart_name, globals()[f"HEART_{heart_name}_IP"], globals()[f"HEART_{heart_name}_PORT"]):
        all_hearts_running = False
if all_hearts_running:
    print("\n###############################################@")
    print("[OK] All hearts are running. Starting the main server...")
    print("###############################################@")
else:
    print("\n###############################################@")
    print("[ERROR] Some hearts are down, stopping...")
    print("###############################################@")
    exit(1)

###########################################################################@
# Main code - Server core
###########################################################################@

# Socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("\n###############################################@")
    print("[i] Main server listening on IP:", HOST, " Port:", PORT)
    print("###############################################@")
    while True:
        conn, addr = s.accept()
        try:
            with conn:
                # Receiving connections
                print(f"\n[NET-IN] --> Connected by {addr}")
                conn.settimeout(TIMEOUT_DELAY)
                print(f"[NET-IN] Waiting for data from {addr}")
                data = conn.recv(1024)
                #print(f"[NET-IN] Data received: {data}")    
                if not data or len(data) == 0:
                    print(f"[NET-IN] --> No data received from {addr}")
                    print(f"[NET-OUT] <-- Default result: UNKNOWN")
                    conn.sendall("UNKNOWN".encode('utf-8'))
                    conn.close()
                else:
                    query = data.decode('utf-8')
                    # Received query
                    print(f"[NET-IN] --> Received query: {query}")
                    # Querying hearts
                    print(f"[i] Querying hearts...")
                    responses = check_query_to_hearts(query)
                    print(f"[i] Responses: {responses}")
                    # Calculating final result
                    print(f"[i] Calculating final result...")
                    final_result = calculate_final_result(responses)
                    print(f"[i] Verdict: {final_result}")
                    # Sending final result to client
                    print(f"[NET-OUT] <-- Final result: {final_result}")
                    conn.sendall(final_result.encode('utf-8'))
                    conn.close()

        except socket.timeout:
            print(f"[ERROR] Timeout occurred with {addr}")
            # Send a response only if the socket is still active
            try:
                conn.sendall("TIMEOUT".encode('utf-8'))
            except OSError:
                print(f"[ERROR] Could not send TIMEOUT message, socket already closed for {addr}")
        except Exception as e:
            print(f"[ERROR] An error occurred with {addr}: {e}")