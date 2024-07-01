# Di-Clutter Flask Applicatie

## Overzicht
Di-Clutter is een webapplicatie ontwikkeld met Flask. Deze applicatie biedt functionaliteiten voor het beheren en weergeven van projecten, onderzoekers, en gerelateerde gegevens. In deze handleiding wordt uitgelegd hoe je de applicatie kunt installeren, configureren en gebruiken.

## Installatie

### Vereisten
Zorg ervoor dat je de volgende software op je systeem hebt geïnstalleerd:
- Python 3.12+
- pip (Python package installer)

### Stappen
1. **Clone de repository**
   ```bash
   git clone <repository-url>
   cd di-clutter
   ```

2. **Maak een virtual environment aan (optioneel maar aanbevolen)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Voor Windows gebruik: venv\Scripts\activate
   ```

3. **Installeer de vereiste pakketten**
   ```bash
   pip install -r requirements.txt
   ```

4. **Maak een `.env` bestand aan in de root directory van het project en configureer de benodigde omgevingsvariabelen** (zie sectie "Omgevingsvariabelen")

5. **Start de applicatie**
   ```bash
   python run.py
   ```

6. **Uitrollen**
   Om de Flask applicatie uit te rollen, kun je de documentatie van Flask volgen voor implementaties. Deze handleiding biedt gedetailleerde instructies over hoe je je applicatie kunt voorbereiden en implementeren voor productieomgevingen. Voor meer informatie kun je de officiële Flask documentatie bekijken over het implementeren van Flask applicaties op: [Flask - Het implementeren van een Flask Applicatie](https://flask.palletsprojects.com/en/2.0.x/deploying/).


## Gebruik

### Navigatie
De applicatie bevat verschillende routes voor het beheren en bekijken van gegevens. De belangrijkste pagina's zijn:
- **Index**: De startpagina van de applicatie.
- **Onderzoekers**: Overzicht van alle onderzoekers.
- **Projecten**: Overzicht van alle projecten.
- **Configuratie**: Pagina om configuraties te beheren.

### Functionaliteiten

- **Toevoegen en bewerken van onderzoekers en projecten**

Het systeem maakt het mogelijk om nieuwe projecten, onderzoekers en andere relevante entiteiten toe te voegen en bestaande gegevens te bewerken. Gebruikers kunnen projectdetails invoeren en bijwerken, inclusief de synchronisatie met GitHub repositories voor versiebeheer.

- **Weergeven van projectdetails**

Projectdetails worden uitgebreid weergegeven, inclusief informatie over bijbehorende onderzoekers, onderwijsinstellingen en overkoepelende projecten. Gebruikers kunnen gedetailleerde informatie bekijken, inclusief GitHub repository-informatie en andere gekoppelde gegevens.

- **Beheer van configuraties**

Het systeem biedt een configuratiebeheerfunctionaliteit waarmee gebruikers dynamisch instellingen kunnen configureren voor verschillende aspecten van het systeem. Dit omvat het definiëren en beheren van configuratieopties zoals veldtypes, activeringsopties en specifieke instellingen per gebruiker.

Elke functionaliteit wordt ondersteund door een intuïtieve gebruikersinterface die interacties mogelijk maakt met de backend-API's en databases. Gebruikers kunnen navigeren door verschillende secties van het systeem, gegevens invoeren, bewerken, verwijderen en gedetailleerde informatie bekijken over projecten, onderzoekers en configuraties.


### GitHub API Integratie

Deze webapplicatie maakt gebruik van de GitHub API om gegevens op te halen en te integreren met de functionaliteiten van de Di-Clutter app. Hieronder wordt uitgelegd hoe je de GitHub API-sleutel kunt integreren en gebruiken in de applicatie.

#### GitHub API Sleutel

Om toegang te krijgen tot de GitHub API, heb je een geldige API-sleutel nodig. Volg de onderstaande stappen om de sleutel toe te voegen aan je project:

1. **Genereer een GitHub Token**
   - Ga naar de [GitHub Settings](https://github.com/settings/tokens) pagina.
   - Klik op "Generate new token" en geef je token een beschrijvende naam.
   - Selecteer de juiste scopes of rechten die nodig zijn voor je applicatie (bijvoorbeeld `repo` voor toegang tot repositories).

2. **Voeg de Token toe aan je Omgevingsvariabelen**
   - Maak een bestand aan met de naam `.env` in de hoofdmap van je project, als dit nog niet bestaat.
   - Voeg de gegenereerde token toe aan dit bestand als volgt:
     ```
     GH_TOKEN2=<jouw-github-token>
     ```
   - Sla het `.env` bestand op. Dit bestand wordt gebruikt om gevoelige informatie zoals API-sleutels buiten je broncode op te slaan.

3. **Integratie in de Code**
   - In je Python code, zoals in het voorbeeld hierboven, kun je de GitHub API-sleutel ophalen uit de omgevingsvariabele:
     ```python
     import os
     from ghapi.all import GhApi

     token = os.environ.get('GH_TOKEN2')
     gh = GhApi(token=token)
     ```

4. **Gebruik van de GitHub API**
   - Met de `gh` object geïnstantieerd met je token, kun je nu GitHub API calls uitvoeren binnen je applicatie, zoals het ophalen van gegevens van repositories of gebruikers.

### Vereiste GitHub Token Scopes:

1. **repo (Volledige controle over privé repositories)**
   - **Uitleg**: Nodig voor het aanmaken, beheren en verwijderen van repositories binnen de organisatie.

2. **delete_repo (Verwijderen van repositories)**
   - **Uitleg**: Specifiek vereist voor het verwijderen van repositories zoals aangegeven in je code.

3. **admin:org (Volledige controle over organisaties en teams, lezen en schrijven van organisatieprojecten)**
   - **Uitleg**: Vereist om repositories binnen de organisatie aan te maken en om organisatie-instellingen te beheren.

### Waarom Elke Scope Nodig Is:

- **repo**: Deze scope biedt volledige controle over privé repositories, inclusief het aanmaken en beheren van repositories, wat nodig is voor de `create_in_org` methode in je code.
- **delete_repo**: Deze specifieke scope is vereist om repositories te verwijderen, zoals je code snippet aangeeft.
- **admin:org**: Deze scope biedt volledige controle over organisatie- en teaminstellingen, wat nodig is voor het beheren van repositories binnen een organisatie.



#### Belangrijke Opmerkingen
- Zorg ervoor dat je je GitHub token veilig bewaart en niet deelt met anderen.
- Gebruik alleen de nodige rechten die vereist zijn voor de functionaliteiten van je applicatie om de beveiliging te waarborgen.



### Installatie en Configuratie van MongoDB

Di-Clutter maakt gebruik van MongoDB om project- en onderzoeksgegevens op te slaan en te beheren. Hieronder worden de stappen uitgelegd om MongoDB lokaal te installeren, de benodigde omgevingsvariabelen te configureren, en de applicatie te starten.

#### Stap 1: MongoDB Lokaal Installeren

1. **Download MongoDB**:
   - Ga naar de [MongoDB Download Center](https://www.mongodb.com/try/download/community) en download de versie die compatibel is met jouw besturingssysteem.

2. **Installeer MongoDB**:
   - Volg de installatie-instructies voor jouw besturingssysteem:
     - **Windows**: Volg de wizard om MongoDB te installeren.
     - **macOS**: Gebruik Homebrew:
       ```bash
       brew tap mongodb/brew
       brew install mongodb-community
       ```
     - **Linux**: Volg de installatie-instructies op de MongoDB website voor jouw specifieke distributie.

3. **Start MongoDB**:
   - Start de MongoDB server:
     - **Windows**: Start de MongoDB service via de Services app of gebruik de Command Prompt:
       ```bash
       mongod
       ```
     - **macOS en Linux**: Gebruik de terminal:
       ```bash
       mongod --config /usr/local/etc/mongod.conf
       ```

#### Stap 2: MongoDB Configureren

1. **Maak een MongoDB Gebruiker aan**:
   - Open een nieuwe terminal of Command Prompt en start de MongoDB shell:
     ```bash
     mongo
     ```
   - Maak een nieuwe database gebruiker:
     ```js
     use admin
     db.createUser({
       user: "$USERNAME",
       pwd: "$PASSWORD",
       roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
     })
     ```

2. **Verbind met MongoDB met Authenticatie**:
   - Stop de huidige MongoDB server en start deze opnieuw met authenticatie:
     ```bash
     mongod --auth --config /usr/local/etc/mongod.conf
     ```
   - Verbind opnieuw met de MongoDB shell met de nieuwe gebruiker:
     ```bash
     mongo -u $USERNAME -p $PASSWORD --authenticationDatabase "admin"
     ```

#### Stap 2.5: MongoDB draaien via Docker of andere methoden

Als je MongoDB op een andere manier wilt inzetten, zoals via een Docker-container, volg dan de onderstaande stappen:

1. **Docker Installeren**:
   - Zorg ervoor dat je Docker hebt geïnstalleerd. Volg de installatie-instructies op de [Docker website](https://docs.docker.com/get-docker/).


2. **MongoDB Container Starten**:
   - Gebruik het volgende Docker-commando om een MongoDB-container te starten:
     ```bash
     docker pull mongodb/mongodb-community-server:latest
     docker run -d -p 27017:27017 --name mongodb -e MONGO_INITDB_ROOT_USERNAME=$USERNAME -e MONGO_INITDB_ROOT_PASSWORD=$PASSWORD -d mongodb mongodb-community-server:latest
     ```

3. **Controleer de Docker Container**:
   - Verifieer dat de container draait:
     ```bash
     docker ps
     ```

4. **Verbind met MongoDB in Docker**:
   - Pas je omgevingsvariabelen aan zodat de `MONGODB_SERVER` wijst naar de Docker-host (`localhost:27017` als je lokaal werkt):
     ```plaintext
     MONGODB_SERVER=localhost:27017
     ```


#### Stap 3: Omgevingsvariabelen Configureren

1. **Maak een `.env` Bestand aan**:
   - Maak een bestand genaamd `.env` in de hoofdmap van je project.
   - Voeg de volgende regels toe aan het `.env` bestand:
     ```plaintext
     MONGODB_USERNAME=$USERNAME
     MONGODB_PASSWORD=$PASSWORD
     MONGODB_SERVER=localhost:27017 # als je lokaal werkt
     ```

#### Stap 4: Integratie in de Code

1. **Gebruik de Omgevingsvariabelen in je Code**:
   - In je Python code, laad de MongoDB inloggegevens uit de omgevingsvariabelen en maak verbinding met de database:
     ```python
     import os
     from pymongo import MongoClient
     from pymongo.server_api import ServerApi

     # Laad MongoDB inloggegevens uit omgevingsvariabelen
     mongodb_username = os.environ.get('MONGODB_USERNAME')
     mongodb_password = os.environ.get('MONGODB_PASSWORD')
     mongodb_server = os.environ.get('MONGODB_SERVER')

     # MongoDB verbinding URI
     uri = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_server}"

     # Maak een nieuwe client en verbind met de server
     client = MongoClient(uri, server_api=ServerApi('1'))
     db = client['projectdatabase']

     # Verzend een ping om een succesvolle verbinding te bevestigen
     try:
         client.admin.command('ping')
         print("Pinged your deployment. You successfully connected to MongoDB!")
     except Exception as e:
         print(e)
     ```

#### Belangrijke Opmerkingen

- Zorg ervoor dat je je MongoDB inloggegevens veilig bewaart en niet deelt met anderen.
- Geef alleen de nodige rechten aan de MongoDB gebruiker die vereist zijn voor de functionaliteiten van je applicatie om de beveiliging te waarborgen.
- Voor productieomgevingen, overweeg om de MongoDB server op een veilige en betrouwbare manier te configureren, bijvoorbeeld door middel van een firewall en toegangslijsten.


