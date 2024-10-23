import asyncio
import json
import socket
from concurrent.futures import ThreadPoolExecutor

from _conf import *

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
async def check_heart_health(socket_name, socket_ip, socket_port):
    try:
        reader, writer = await asyncio.open_connection(socket_ip, socket_port)
        healthcheck_message = "HEALTHCHECK"
        writer.write(healthcheck_message.encode('utf-8'))
        await writer.drain()
        print(f"[OK] Socket {socket_name} is open")
        writer.close()
        await writer.wait_closed()
        return True
    except Exception as e:
        print(f"[ERROR] Socket {socket_name} is closed: {e}")
        return False

# Function to query a single heart
async def query_heart(heart_name, query):
    try:
        heart_ip = globals()[f"HEART_{heart_name}_IP"]
        heart_port = globals()[f"HEART_{heart_name}_PORT"]
        heart_paranoia = globals()[f"HEART_{heart_name}_PARANOIA"]

        reader, writer = await asyncio.open_connection(heart_ip, heart_port)
        writer.write(query.encode('utf-8'))
        await writer.drain()
        response = float((await reader.read(1024)).decode('utf-8'))
        writer.close()
        await writer.wait_closed()

        verdict = "1" if response > heart_paranoia else "0"
        return (heart_name, response, verdict)
    except Exception as e:
        return (heart_name, "404", "404")

# Function to query the hearts and get the score
async def check_query_to_hearts(query):
    tasks = [query_heart(heart_name, query) for heart_name in list_of_hearts]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
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

async def main():
    print("\n###############################################@")
    print("[i] Starting... Checking heart states...")
    print("###############################################@")
    all_hearts_running = False
    while not all_hearts_running:
        all_hearts_running = True
        for heart_name in list_of_hearts:
            if not await check_heart_health(heart_name, globals()[f"HEART_{heart_name}_IP"], globals()[f"HEART_{heart_name}_PORT"]):
                all_hearts_running = False
        if not all_hearts_running:
            print("\n###############################################@")
            print("[ERROR] Some hearts are down, retrying in 10 seconds...")
            print("###############################################@")
            await asyncio.sleep(10)

    print("\n###############################################@")
    print("[OK] All hearts are running. Starting the main server...")
    print("###############################################@")

    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        print("\n###############################################@")
        print(f"[i] Main server listening on IP: {HOST} Port: {PORT}")
        print("###############################################@")
        await server.serve_forever()

#RECEIVING REQUESTS FROM PROXY
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    try:
        print(f"\n[NET-IN] --> Connected by {addr}")
        data = await asyncio.wait_for(reader.read(1024), timeout=TIMEOUT_DELAY)
        if not data or len(data) == 0:
            print(f"[NET-IN] --> No data received from {addr}")
            print(f"[NET-OUT] <-- Default result: UNKNOWN")
            writer.write("UNKNOWN".encode('utf-8'))
        else:
            #Parsing request
            request = json.loads(data.decode('utf-8'))
            print(f"\n\n[NET-IN] --> Received query: {request}")
            uri = request.get('uri', '')
            body = request.get('body', '')
            #Querying hearts for URI
            print(f"[i] Querying hearts for URI...")
            responses = await check_query_to_hearts(uri)
            print(f"[i] Responses URI: {responses}")
            print(f"[i] Calculating final result URI...")
            uri_final_result = calculate_final_result(responses)
            print(f"[i] Verdict URI: {uri_final_result}")
            #Querying hearts for BODY
            print(f"[i] Querying hearts for BODY...")
            responses = await check_query_to_hearts(body)
            print(f"[i] Responses BODY: {responses}")
            print(f"[i] Calculating final result BODY...")
            body_final_result = calculate_final_result(responses)
            print(f"[i] Verdict BODY: {body_final_result}")
            #Final result
            final_result = "ERROR"
            if(body_final_result == "ERROR" and uri_final_result == "ERROR"):
                final_result = "ERROR"
            else: 
                if(body_final_result == "MALICIOUS" or uri_final_result == "MALICIOUS"):
                    final_result = "MALICIOUS"
                else:
                    final_result = "SAFE"
            print(f"[NET-OUT] <-- Final result: {final_result}")
            writer.write(final_result.encode('utf-8'))
        await writer.drain()
    except asyncio.TimeoutError:
        print(f"[ERROR] Timeout occurred with {addr}")
        writer.write("TIMEOUT".encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] An error occurred with {addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
