FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3002
#Fast mode
#CMD ["python", "server_socket_model_xss.py"]
#Debug mode 
CMD ["python", "-u", "server_socket_model_xss.py"]
