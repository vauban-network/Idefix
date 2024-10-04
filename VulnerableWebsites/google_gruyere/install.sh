docker pull karthequian/gruyere:latest
docker run -d -p 8008:8008 --name google_gruyere karthequian/gruyere
docker start google_gruyere