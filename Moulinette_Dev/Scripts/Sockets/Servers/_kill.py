import subprocess
import os
import signal

def kill_process_by_name(name):
    try:
        # Get the list of all running processes
        proc = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
        out, err = proc.communicate()

        # Iterate over the lines of the output
        for line in out.splitlines():
            if name in line.decode('utf-8'):
                # Extract the PID and kill the process
                print("Killing process", name)
                pid = int(line.split(None, 2)[1])
                os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print(f"Error killing process {name}: {e}")

# Kill existing processes if running
print("[!] Killing MAIN")
kill_process_by_name("server_socket_main.py")
print("[!] Killing SQL HEART")
kill_process_by_name("server_socket_model_sql.py")
print("[!] Killing XSS HEART")
kill_process_by_name("server_socket_model_xss.py")
print("[!] Killing PATH HEART")
kill_process_by_name("server_socket_model_path_traversal.py")
