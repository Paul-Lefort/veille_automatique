# Veille Automatique (Google Alerts)

Ce projet permet d'automatiser une veille technologique en récupérant les e-mails envoyés par **Google Alerts**, en extrayant les liens, et en les traitant via une IA locale (Ollama).

> ️**IMPORTANT** : Ce projet est conçu spécifiquement pour parser les e-mails générés par **Google Alerts**. Il ne fonctionnera pas avec d'autres types de newsletters ou e-mails.

## Installation

### 1. Configuration Google
1. Accédez à la [Google Cloud Console](https://console.cloud.google.com).
2. Créez un nouveau projet nommé `veille-automatique`.
3. Allez dans **API et Services** pour configurer vos accès.
   * *Note : Si vous utilisez l'accès IMAP, assurez-vous également de générer un "Mot de passe d'application" dans les paramètres de sécurité de votre compte Google.*

### 2. Configuration de l'environnement
Créez un fichier `.env` à la racine du projet et remplissez les informations nécessaires :

    IMAP_SERVER=imap.gmail.com
    EMAIL_ADDRESS=votre.email@gmail.com
    APP_PASSWORD=votre_mot_de_passe_application

## Utilisation

Une fois l'environnement configuré, suivez ces étapes pour lancer le système :

### Lancement des services
Démarrez les conteneurs Docker :
```bash
  docker compose up -d
```

### Préparation de l'IA (Ollama)
Téléchargez le modèle localement (à faire une seule fois) :
```Bash
  docker exec -it veille_ollama ollama pull mistral
```

### Lancement de la veille
Exécutez le script de traitement :
```Bash
  docker exec -it veille_web python main.py
```