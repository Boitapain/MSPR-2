# MSPR 3 & 4

Vous trouverez ci-dessous une description détaillée de notre projet, ainsi que la méthode d'installation grâce à Docker.

## Présentation

Notre projet est une application du nom de Disease Track ayant pour but de prévoir l'impact des prochaines pandémies sur une zone géographique donnée.

Grâce à cette application, l'ONU aura accès à un outil de prédiction poussé capable d'aider à la prise de décision au niveau national et international.

## Initialisation de la base de données

Avant de lancer les conteneurs Docker, il est nécessaire d'initialiser la base de données.  
Depuis le dossier `app`, exécutez la commande suivante :

```sh
cd app
touch disease_track.db
```

## Installation et utilisation avec Docker

Pour lancer l'application en local, assurez-vous d'avoir [Docker](https://www.docker.com/) et [docker-compose](https://docs.docker.com/compose/) installés sur votre machine.

- **Démarrer les conteneurs (avec reconstruction) :**
  ```sh
  docker-compose up --build
  ```
- **Arrêter et supprimer les conteneurs, volumes et réseaux créés :**
  ```sh
  docker-compose down -v
  ```

## Analyse de code

Nous utilisons SonarCloud pour l'analyse de la qualité du code :
- [Voir l’analyse SonarCloud](https://sonarcloud.io/summary/new_code?id=Boitapain_MSPR-3-4&branch=main)

## Déploiement en ligne

L'application est également disponible en ligne via Render :
- [Frontend Render](https://frontend-ursm.onrender.com)
- [Backend Render](https://backend-l0n0.onrender.com)

## Structure du projet

- `app/` : Contient le code source principal de l'application (API, logique métier, etc.)
- `docker-compose.yml` : Configuration des services Docker
- `requirements.txt` : Dépendances Python

## Tests

Les tests sont automatisés et peuvent être lancés avec un workflow GitHub Actions à chaque push ou pull request sur la branche `main`.

---
