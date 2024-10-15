###########################################################################@
# This script is the client example for the SQL MODEL
###########################################################################@
import socket

###########################################################################@
# Parameters 
###########################################################################@
HOST = '127.0.0.1'  # L'adresse IP de l'hôte (localhost dans ce cas)
PORT = 3001         # Le port utilisé par le serveur

###########################################################################@
# Testing the server
###########################################################################@
print("\n###############################################@")
print(" Client asking to server XSS IP:", HOST, " Port:", PORT)
print("###############################################@")
while True:
    # Ask for SQL query
    query = input("Type XSS request (or 'q' to quit): ")   
    # q to quit
    if query.lower() == 'q':
        break
    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(query.encode('utf-8'))
        # Receiving response
        data = s.recv(1024)
        # Printing answer
        print('Server response:', data.decode('utf-8'))
        # Closing socket
        s.close()
