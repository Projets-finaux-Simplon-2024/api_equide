# Utilisez une image Python officielle comme image de base
FROM python:3.12-slim

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installez les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiez tout le contenu de l'application dans le répertoire de travail
COPY . .

# Exposez le port sur lequel l'application va fonctionner
EXPOSE 8000

# Définissez la commande par défaut pour exécuter l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
