# SoftDesk

API RESTful sécurisée permettant à des équipes de faire remonter des problèmes techniques et des tâches à réaliser de manière collaborative.

## Fonctionnalités

- **Gestion hiérarchique** : Projets > Issues > Commentaires avec routes imbriquées.
- **Workflow modulaire** : Attribution flexible avec contributeurs multiples  
- **Sécurité renforcée** : Permissions granulaires (auteur/contributeur), 
    avec accès unique des ressources aux contributeurs  
- **Gestion de projets** : 
    - Création avec modération par auteur original
    - Gestion par type (Back-end, Front-end, Android, iOS)
- **Signalement technique**: 
    - Création d'issues (problèmes ou tâches) avec attribution dynamique aux contributeurs.
    - Gestion par priorités (High, Medium, Low), tags (Bug, fonctionnalité, tâches),  
        et statut (To do, In progress, Finished,).

## Conformité 

- **OWASP** : 
    - Authentification avec JWT token et refresh
    - Permissions hiérarchiques
    - Filtrage QuerySet systématique

- **Normes RGPD** : 
    - Vérification de l'âge des utilisateurs lors de l'inscription
    - Choix de confidentialités
    - Droit à l'oubli lors de la suppression du compte

- **Green Code**:
    - Sérialisation dynamique suivant les actions
    - Faible imbrication des ressources
    - Pagination des résultats

## Stack

- Python `3.13`
- Django `6.0.4`
- Django REST Framework (DRF) `3.17.1`
- DRF Nested Routers `0.95.0`
- DRF SimpleJWT `5.5.1`

## Prérequis

- Python `3.8+` (version 3.13 conseillé pour une compatibilité optimale) ;
- (Optionnel) Git pour cloner le dépôt ;

## Installation

- Installer UV :
```bash
pip install uv
```
- Cloner ou sauvegarder le dépôt à l'emplacement de votre choix ;
- Déplacer vous dans le dossier du dépôt (`softdesk\`).
- Installer les dépendances, l'environnement virtuel et activer ce dernier avec UV : 
```bash
uv sync
```

## Usage

- Activer votre environnement virtuel via un terminal de commande depuis le dossier de dépot (`softdesk/`) :
```bash
source .venv/bin/activate # macOS et linux
.venv\Scripts\activate # windows
```
- Déplacer vous dans le dossier principal de l'application (`softdesk/sofdesk`) :
```bash
cd softdesk
```
- Appliquer les migrations si vous utilisez l'API pour la première fois :
```bash
python manage.py migrate
```
- Lancer le serveur localement : 
```bash
python manage.py runserver
```
L'API sera disponible à l'adresse par défaut http://127.0.0.1:8000/  
Une fois effectuées, il n'est pas nécessaire d'appliquer à nouveau les migrations lors d'utilisation future.

### Authentification

Toutes les requêtes - mise à part la création de compte - nécessite un JWT token.  
Pour en obtenir un et l'utiliser :  
 - Une requête POST doit être envoyée à `/api/token/` avec comme payload les identifiants de l'utilisateur.
    ```json
    {
        "username": "nom_utilisateur",
        "password": "mot_de_passe"
    }
    ```
- Utilisez le token retourné dans le header de la requête: `Authorization: Bearer <JWT_TOKEN>` 

### Permissions

- L'utilisateur courant doit être un contributeur du projet pour y accéder et accéder aux ressources associées (issues et commentaires).
- Seul l'auteur d'une ressource est autorisé à la supprimer ou à l'utiliser.
- Les utilisateurs authentifiés ont accès à la liste des utilisateurs (uniquement `id` et `username`) pour l'ajout de contributeur, mais pas aux détails d'un utilisateur.
- Seul l'auteur d'un projet peut ajouter un contributeur au projet ; il est également le seul avec le contributeur en question à pouvoir le supprimer.
- L'ensemble des ressources restent accessibles aux administrateurs via l'interface administrateur Django.

### Endpoints

Les méthodes GET, POST, PUT, PATCH, et DELETE sont supportées selon les permissions décrites ci-dessus.
Les principaux endpoints sont les suivants :

| méthode   | Endpoint     | Description   |
|-----------|--------------|---------------|
POST | /api/user/ | Créer un compte utilisateur |
GET | /api/user/ | Liste les utilisateurs enregistrés |
GET | /api/project/ | Liste les projets auxquels l'utilisateur courant est contributeur |
POST | /api/project/ | Créer un nouveau projet dont l'utilisateur courant sera auteur et contributeur |
GET | /api/project/{id_project}/ | Détail d'un projet spécifique |
POST | /api/project{id_project}/contributor/ | Ajouter un contributeur au projet |
POST | /api/project/{id_project}/issue | Créer une nouvelle tâche ou problème (issue) dans un projet* |
GET | /api/project/{id_project}/issue/{id_issue} | Détail d'une issue spécifique |
POST | /api/project/{id_project}/issue/{id_issue}/comment/ | Créer un nouveau commentaire dans une issue |
GET | /api/project/{id_project}/issue/{id_issue}/comment/{uuid_comment}/ | Voir un commentaire spécifique |

*Le payload `assignment`avec l'ID d'un contributeur peut être renseigné pour assigner un contributeur du projet à cette issue.

### Exemples

#### Pour créer un nouveau projet :

**Endpoint** : `http://127.0.0.1:8000/api/project/`  
**Méthode** : POST  
**Payload** :  
```json
{
"title": "Nom du projet",
"description": "Description détaillée",
"type": "BACK"
}
 ```
**Choix de type valide** :  
- `BACK`
- `FRONT`
- `IOS`
- `ANDROID`

#### Pour créer une nouvelle issue :  

**Endpoint** : `http://127.0.0.1:8000/api/project/{id_project}/issue/`  
**Méthode** : POST  
**Payload** :  
```json
{
    "name": "Nom de l'issue",
    "description": "Description détaillée",
    "priority": "HIGH",
    "tag": "BUG",
    "assignment":"Vide ou ID d'un contributeur du projet"
}
```
**Choix de priorité valide** :  
- `HIGH`
- `MEDIUM`
- `LOW`  

**Choix de tag valide** :  
- `BUG` 
- `FEATURE`
- `TASK`

