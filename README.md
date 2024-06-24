### README.md

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

## Gebruik

### Navigatie
De applicatie bevat verschillende routes voor het beheren en bekijken van gegevens. De belangrijkste pagina's zijn:
- **Index**: De startpagina van de applicatie.
- **Onderzoekers**: Overzicht van alle onderzoekers.
- **Projecten**: Overzicht van alle projecten.
- **Configuratie**: Pagina om configuraties te beheren.

### Functionaliteiten
- **Toevoegen en bewerken van onderzoekers en projecten**
- **Weergeven van projectdetails**
- **Beheer van configuraties**




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

#### Belangrijke Opmerkingen
- Zorg ervoor dat je je GitHub token veilig bewaart en niet deelt met anderen.
- Gebruik alleen de nodige rechten die vereist zijn voor de functionaliteiten van je applicatie om de beveiliging te waarborgen.

Door deze stappen te volgen, kun je de GitHub API integreren in je Di-Clutter Flask applicatie en profiteren van de kracht van GitHub voor het beheren van projectgegevens.


### MongoDB Environment Variabele

Deze webapplicatie maakt gebruik van MongoDB voor het opslaan en beheren van gegevens. Hieronder wordt uitgelegd hoe je de MongoDB inloggegevens kunt integreren door gebruik te maken van environment variabelen.

#### MongoDB Inloggegevens

Om verbinding te maken met MongoDB, dien je de juiste inloggegevens (gebruikersnaam en wachtwoord) te configureren als environment variabelen. Volg de onderstaande stappen om dit te doen:

1. **Maak een MongoDB Cluster en Gebruiker**
   - Zorg ervoor dat je een MongoDB cluster hebt opgezet waarop je applicatie kan verbinden.
   - Maak een gebruiker aan met de juiste rechten om toegang te krijgen tot de databases en collecties die je applicatie nodig heeft.

2. **Voeg de Inloggegevens toe aan je Omgevingsvariabelen**
   - Maak of bewerk het `.env` bestand in de hoofdmap van je project.
   - Voeg de MongoDB gebruikersnaam en wachtwoord toe aan het `.env` bestand als volgt:
     ```
     MONGODB_USERNAME=<jouw-mongodb-gebruikersnaam>
     MONGODB_PASSWORD=<jouw-mongodb-wachtwoord>
     ```
   - Sla het `.env` bestand op. Dit bestand wordt gebruikt om gevoelige informatie zoals inloggegevens buiten je broncode op te slaan.

3. **Integratie in de Code**
   - In je Python code, zoals in het voorbeeld hierboven, kun je de MongoDB inloggegevens ophalen uit de omgevingsvariabelen:
     ```python
     import os

     # Load MongoDB credentials from environment variables
     mongodb_username = os.environ.get('MONGODB_USERNAME')
     mongodb_password = os.environ.get('MONGODB_PASSWORD')
     ```

4. **Gebruik van MongoDB**
   - Gebruik de verkregen `mongodb_username` en `mongodb_password` om verbinding te maken met je MongoDB cluster en om MongoDB operaties uit te voeren binnen je applicatie.

#### Belangrijke Opmerkingen
- Zorg ervoor dat je MongoDB inloggegevens veilig bewaart en niet deelt met anderen.
- Geef alleen de nodige rechten aan de MongoDB gebruiker die vereist zijn voor de functionaliteiten van je applicatie om de beveiliging te waarborgen.

Door deze stappen te volgen, kun je MongoDB integreren in je Di-Clutter Flask applicatie en gebruik maken van MongoDB als je database voor het beheren van projecten, onderzoekers en gerelateerde gegevens.