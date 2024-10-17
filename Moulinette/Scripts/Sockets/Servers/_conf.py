#Main server configuration
MAIN_IP = "127.0.0.1"
MAIN_PORT = 3000
MAIN_TIMEOUT_DELAY = 0.5

#List of hearts
HEARTS = ["SQL", "XSS"]
#Set IPs for the hearts
HEART_SQL_IP = "127.0.0.1"
HEART_XSS_IP = "127.0.0.1"
#Set ports for the hearts
HEART_SQL_PORT = 3001
HEART_XSS_PORT = 3002
#Set the paranoia level for the hearts
HEART_SQL_PARANOIA = 0.78
HEART_XSS_PARANOIA = 0.5
