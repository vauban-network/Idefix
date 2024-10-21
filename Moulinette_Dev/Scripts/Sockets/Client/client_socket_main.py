###########################################################################@
# This script is the client example for the MAIN
###########################################################################@
import socket

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
while True:
    # Ask for query
    query = input("Type any web request (or 'q' to quit): ")   
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
