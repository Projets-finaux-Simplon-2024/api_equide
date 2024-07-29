# API de la base de données équidé
## :heavy_plus_sign: Installlation
### Prérequis
Pour faire fonctionner l'API il faut commencer par créer la base de données qui correspond via le dépôt github [:link:build_bdd_equide](https://github.com/Projets-finaux-Simplon-2024/build_bdd_equide)

> [!IMPORTANT]
> Il est nécéssaire d'installer [:link:docker](https://docs.docker.com/desktop/) pour pouvoir récupérer container nécéssaire au fonctionnement de toute l'API.

### Pull de l'image de l'API

```
docker pull ghcr.io/projets-finaux-simplon-2024/api_equide:latest
```

### Création du container
Voici la ligne générique de création du container 

```
docker run -e DATABASE_URL=[chaine_de_connexion] -e API_USERNAME=[yourusername] -e API_PASSWORD=[yourpassword] -e SECRET_KEY=[your_generated_secret_key] -p 8000:8000 [container_name]
```

Exemple par défaut 
```
docker run -e DATABASE_URL=postgresql://admin:admin@172.17.0.2:5432/bdd_equide -e API_USERNAME=admin -e API_PASSWORD=admin -e SECRET_KEY=75bdaa1397df51c94112f76b70cd62221b3bd97fd9ae35d07edc5fcd02dff068 -p 8000:8000 api_equide
```

> [!NOTE]
> ### Variables d'environnement du container
> - **DATABASE_URL**: Chaîne de connexion à la base de données, déterminer au moment de la création de la bdd avec le programme de remplissage [:link:build_bdd_equide](https://github.com/Projets-finaux-Simplon-2024/build_bdd_equide)
> - **API_USERNAME**: Username pour se connecter à l'API
> - **API_PASSWORD**: Password pour se connecter à l'API
> - **SECRET_KEY**: Signature des tokens pour l'utilisation de l'API. Pour plus d'informations voir la section Algorithme
> ### Variables d'environnement optionnelles
> - **ALGORITHM**: Algorithme utilisé dans l'API *HS256*, *HS384*, *HS512*. Par défaut **HS256**
> - **ACCESS_TOKEN_EXPIRE_MINUTES**: Durée d'expiration du token en minutes. Par défaut **30 minutes**.
> ### Plus d'explications
> - **8000:8000**: Mappage des ports entre intérieur et extérieur du container
> - **[container_name]**: Nom du container après création

## :heavy_plus_sign: Author
### Algorithme
L'API utilise par défaut l'algorithme **HS256**. L'agorithme utilisé conditonne la clé de signature des tokens. Tel que : 
- HS256 (HMAC avec SHA-256) : Au moins 256 bits (32 octets) :point_left:
- HS384 (HMAC avec SHA-384) : Au moins 384 bits (48 octets)
- HS512 (HMAC avec SHA-512) : Au moins 512 bits (64 octets)

### Secret Key
Il est nécéssaire de générer une clé de signature pour faire fonctionner l'API.
- **Première possibilité, en python :** 
```
import os

SECRET_KEY = os.urandom(32).hex()  # Pour HS256, 32 octets
print(SECRET_KEY)
```
- **Seconde possibilité, utilisation d'un générateur :** [:link:jwtsecret.com](https://jwtsecret.com/generate)
> [!TIP]
> Avec le générateur il est possible de faire varier le bouton pour régler le nombre d'octets nécéssaire.
> ![Capture d'écran 2024-07-29 180342](https://github.com/user-attachments/assets/fb485c46-7931-406f-8a75-b1d3ad151acf)

## :heavy_plus_sign: Endpoints
### Base de données
Schéma de la base de données utilisé pour l'API
![Diagram equide](https://github.com/user-attachments/assets/d0282c82-e713-4a16-b396-f28735384525)


### Accés à la documentation SWAGGER
Il est possible d'accéder à la documentation de l'API générer par SWAGGER
```
http://127.0.0.1:8000/docs
```
### Résumer des endpoints
:door:**Méthode(s) POST** 
- ```/auth/token``` : Récupération d'un token d'authentification

:lock:**Méthode(s) GET** 
- ```/stats-ifce/{nomCheval}``` : Permet de savoir si un cheval a des données IFCE dans la table trotteur français (chevaux_trotteur_francais) et/ou dans la table des courses PMU. Ce endpoint n'est utile que pour les tests.
- ```/chevaux/``` : Liste des chevaux de la table trotteur français paginer afin de pouvoir faire un menu paginer dans le front.
- ```/infos-cheval/{idCheval}``` : Recupération des informations d'un cheval de la table trotteur français pour compléter la fiche d'un cheval.
- ```/stat-cheval/{nomCheval}``` : Récupération des statistiques PMU d'un cheval pour compléter la fiche d'un cheval.
- ```/genealogie-cheval/{nomCheval}/{idCheval}/{depth}``` : Récupération de la généalogie d'un cheval via la table trotteur français pour compléter la fiche d'un cheval.

## :heavy_plus_sign: Annexes
### Librairies
:computer:**Système**

- **FastAPI** : Framework web moderne et rapide pour construire des APIs avec Python 3.6+ basé sur les standards OpenAPI et JSON Schema.
- **Uvicorn** : Serveur ASGI léger et performant, utilisé pour déployer des applications FastAPI.
- **SQLAlchemy** : Toolkit SQL et ORM pour Python, permettant de travailler avec des bases de données de manière déclarative.

 :floppy_disk:**Traitement**

- **NumPy** : Bibliothèque pour le calcul scientifique avec Python, offrant support pour des tableaux multidimensionnels et des fonctions mathématiques avancées.
- **Pandas** : Bibliothèque fournissant des structures de données flexibles et des outils d'analyse de données puissants pour Python.

:lock:**Sécurité**

- **python-jose** : Une bibliothèque pour la gestion des JSON Web Tokens (JWT) en Python, utilisée pour l'authentification et l'autorisation. Elle permet de créer, signer, vérifier et déchiffrer des tokens JWT de manière sécurisée.

:mag_right:**Tests**

- **Pydantic** : Bibliothèque de validation de données pour Python, utilisée principalement avec FastAPI pour définir et valider des modèles de données.
- **Pytest** : Framework de test pour Python, permettant d'écrire des tests simples et évolutifs avec des fonctionnalités avancées comme les fixtures et les plugins.


### Chevaux a tester
Liste de chevaux générant une ou des singularités(peut évoluer)
```
OBJECTION JENILOU
```







