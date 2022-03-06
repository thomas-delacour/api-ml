# API Machine Learning

Cette API permet de réaliser des prédictions grâce à des modèles de machines learning. L'API est déployable via Docker et Kubernetes.


## API avec FastAPI

L'API est dévelopée avec le framework [FastAPI](https://fastapi.tiangolo.com/)
Dans un environnement Python configuré avec les librairies de `requitements.txt`, le lancement de l'API se fait via la commande `python api_models.py`

L'API est alors accessible à l'adresse http://localhost:8000

### Modèles

L'entrainement des modèles a été réalisé via le script `train.py`.
Ce script va récupérer le fichier **rain.csv** qui contient les données météo brute, les nettoyer puis entraîner les différents modèles.
Chaque modèle est ensuite sauvegardé dans un fichier pour être utilisé par l'API.

### Enpoints

#### Authentification
Hormis pour les endpoints / et /docs il est nécessaire de  s'authentifier via le header **authorization-header**. Le header doit être de cette forme : *Basic b64string*
*b64string* est une chaîne de caractère en base64 correspond correspondant à un couple *user:password*

Par exemple on peut s'authentifier en envoyant comme **authorization-header**: *Basic YWxpY2U6d29uZGVybGFuZA==* avec *YWxpY2U6d29uZGVybGFuZA==* étant la chaîne de caratères *alice:wonderland* encodée en base64

#### /
Cet endpoint permet de contrôler si l'API est en fonctionnement
#### /docs
Fastapi fournit cet endpoint qui permet d'accèder à une documentation de l'API et de tester les différents endpoints
#### /info
Renvoie la liste des modèles entraînés disponibles
#### /score
Cet endpoint nécessite de sélectionner un modèle et va renvoyer le score obtenu par ce modèle sur les données de test
#### /predict/{model}
Un endpoint est disponible pour chaque modèle présent dans l'API et il est nécessaire d'envoyer un fichier CSV contenant les données pour lesquels on veut obtenir une prédiction.
L'API va charger le modèle entrainé et l'utiliser pour réaliser la prédiction.

## Fichiers DOCKER
Les images de l'API et des tests sont disponibles sur [DockerHub](https://hub.docker.com/repository/docker/tdde052021/api-ml)

Les tests de l'API peuvent être lancés avec la commande `docker-compose -f tests-docker-compose.yaml up`

## Déploiement

Le déploiement de l'API est fait avec Kubernetes. Il est possible de déployer localement en installant `minkube` et `kubectl`.
Une fois minikube installé et lancé la commande `kubectl create -f kubernetes` permet de déployer plusieurs pods contenant l'API à partir des fichiers du dossier *kubernetes*

L'API est accessible à l'adresse indiqué par la commande `kubectl get ingress`

