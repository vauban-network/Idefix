docker pull raesene/bwapp
docker run -d -p 8080:80 --name bwapp raesene/bwapp
echo "THEN GO TO --> http://localhost:8080/install.php"