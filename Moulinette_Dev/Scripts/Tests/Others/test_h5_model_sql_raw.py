###########################################################################@
# This script is for testing the model_sql.h5 file generated by generate_model_sql.py
###########################################################################@
import pandas as pd
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

###########################################################################@
# Parameters 
###########################################################################@

#Paths
token_path = './IA/Tokens/sql.tokens'
model_path = './IA/Models/model_sql.h5'

#Model parameters
paranoia = 0.8
vocab_size = 8000
max_length = 300
embedding_dim = 16

###########################################################################@
# Testing the model
###########################################################################@

#1.Load the tokenizer
with open(token_path, 'rb') as file:
    tokenizer = pickle.load(file)
#2.Load the model
model = load_model(model_path)

#3. Predict function
def verify_query(query):
    query_sequence = tokenizer.texts_to_sequences([query])
    padded_sequence = pad_sequences(query_sequence, maxlen=max_length, padding='post', truncating='post')
    prediction = model.predict(padded_sequence)
    result = prediction[0][0]
    if result > paranoia:
        return str(result) + " Verdict: MALICIOUS", "MALICIOUS"
    else:
        return str(result) + " Verdict: SAFE", "SAFE"

#4. List of SAFE queries to test
print("\n###############################################@")
print(" Testing the model with SAFE queries")
print("###############################################@")
queries_known_as_safe = [
'SELECT banner FROM v$version WHERE banner LIKE ‘Oracle%’;',
'SELECT banner FROM v$version WHERE banner LIKE ‘TNS%’;',
'SELECT version FROM v$instance;',
'SELECT 1 FROM users -- comment',
'SELECT username FROM all_users ORDER BY username;',
'SELECT name FROM sys.user$; — priv',
'SELECT name FROM v$database;',
'SELECT instance_name FROM v$instance;',
'SELECT column_name FROM all_tab_columns WHERE table_name = ‘blah’ and owner = ‘your_schema_name’;',
'SELECT table_name FROM all_tables;',
'SELECT owner, table_name FROM all_tables;',
'SELECT first_name || ' ' || last_name AS full_name FROM employees;',
'SELECT UTL_INADDR.get_host_address(‘microsoft.com’) FROM dual;',
'SELECT UTL_HTTP.REQUEST(‘<http://microsoft.com>’) FROM dual;'
]

safe_correct = 0
for query_text in queries_known_as_safe:
    result, verdict = verify_query(query_text)
    print(f"This query is considered as : {result}")
    if verdict == "SAFE":
        safe_correct += 1

#5. List of MALICIOUS queries to test
print("\n###############################################@")
print(" Testing the model with MALICIOUS queries")
print("###############################################@")
queries_known_as_malicious = [
    # 1. Basic injection with OR
    "SELECT * FROM Users WHERE UserId = 105 OR 1=1;",
    # 2. Authentication bypass
    "SELECT * FROM Users WHERE Username = 'admin' AND Password = '' OR '1'='1';",
    # 3. UNION to steal sensitive information
    "SELECT Name, Email FROM Users WHERE UserID = 1 UNION SELECT CreditCardNumber, ExpirationDate FROM CreditCards;",
    # 4. Table drop (destructive injection)
    "SELECT * FROM Products WHERE ProductID = 1; DROP TABLE Users;",
    # 5. SQL command with xp_cmdshell (Microsoft SQL Server)
    "SELECT * FROM Orders WHERE OrderID = 105; EXEC xp_cmdshell('dir');",
    # 6. Injection in LIKE with wildcard characters
    "SELECT * FROM Users WHERE Name LIKE '%John%' OR 'a'='a';",
    # 7. Comparison with injection
    "SELECT * FROM Orders WHERE OrderDate = '2024-01-01' OR 'a'='a';",
    # 8. UNION to bypass a condition
    "SELECT * FROM Products WHERE ProductID = 1 UNION SELECT username, password FROM admin_users;",
    # 9. Comment to ignore the end of the query
    "SELECT * FROM Accounts WHERE UserID = 105; -- AND Password = 'pass';",
    # 10. Basic injection in a login form
    "SELECT * FROM Users WHERE Username = 'admin' AND Password = 'wrong_pass' OR '1'='1';",
    # 11. Using char to execute code
    "SELECT * FROM Files WHERE ID = 1; EXEC('char(47,101,116,99,47,112,97,115,115,119,100)');",
    # 12. Conditional table drop
    "SELECT * FROM Users WHERE UserId = 105 OR 1=1; DROP TABLE Payments;",
    # 13. Variable substitution in SQL queries
    "SELECT * FROM Orders WHERE OrderID = @OrderID OR 1=1;",
    # 14. SQL substitution via UNION
    "SELECT * FROM Users WHERE UserId = 105 UNION SELECT NULL, NULL, @@version;",
    # 15. SQL error-based injection (forcing an error to reveal info)
    "SELECT * FROM Products WHERE ProductID = 1 AND 1=(SELECT COUNT(*) FROM information_schema.tables);",
    # 16. SQL boolean-based injection
    "SELECT * FROM Users WHERE Username = 'admin' AND 1=1;",
    # 17. Exploiting database functions (PostgreSQL sleep)
    "SELECT * FROM Users WHERE id = 1; SELECT pg_sleep(10);",
    # 18. Injection by adding commands via UNION
    "SELECT * FROM Orders WHERE OrderID = 1 UNION SELECT NULL, NULL, LOAD_FILE('/etc/passwd');",
    # 19. Bypass with function injection
    "SELECT * FROM Products WHERE Name = 'Laptop' AND LENGTH(Password) > 1;",
    # 20. SQLi authentication with nullification
    "SELECT * FROM Users WHERE Username = 'admin' AND Password = 'password' OR 'x'='x';"
]

malicious_correct = 0
for query_text in queries_known_as_malicious:
    result, verdict = verify_query(query_text)
    print(f"This query is considered as : {result}")
    if verdict == "MALICIOUS":
        malicious_correct += 1

#6. Calculate and print statistics
total_safe = len(queries_known_as_safe)
total_malicious = len(queries_known_as_malicious)

safe_accuracy = (safe_correct / total_safe) * 100
malicious_accuracy = (malicious_correct / total_malicious) * 100

print("\n###############################################@")
print(" Statistics")
print("###############################################@")
print(f"Safe queries success rate: {safe_accuracy:.2f}%")
print(f"Malicious queries success rate: {malicious_accuracy:.2f}%")
print("")