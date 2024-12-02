# Utilisez une image Python 3.10 compatible
FROM python:3.10-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers nécessaires
COPY . /app

# Met à jour pip et installe les dépendances
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir flask numpy tensorflow pickle-mixin

# Expose le port de l'application
EXPOSE 3000

# Commande pour exécuter l'application
CMD ["python", "app.py"]
