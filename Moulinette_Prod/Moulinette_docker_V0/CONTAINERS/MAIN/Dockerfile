FROM python:3.9-slim
WORKDIR /app
COPY . /app
#COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3000
#Fast mode
#CMD ["python", "server_socket_main.py"]
#Debug mode 
CMD ["python", "-u", "server_socket_main.py"]
