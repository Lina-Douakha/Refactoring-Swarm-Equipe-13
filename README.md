# The Refactoring Swarm

Système multi-agents pour l’analyse, la correction et la validation automatique de code Python à l’aide de modèles de langage (LLM).

Projet réalisé dans le cadre du module IGL – École Nationale Supérieure d’Informatique (ESI).


## Présentation

The Refactoring Swarm automatise le processus de refactorisation de code Python en combinant :

* analyse statique,
* correction automatique,
* génération optionnelle de tests et de documentation,
* validation par exécution des tests.

Le système repose sur plusieurs agents spécialisés collaborant de manière itérative jusqu’à obtention d’un code fonctionnel et conforme aux bonnes pratiques.



## Vue globale

Le système s’appuie sur trois rôles principaux :

* **Audit** du code (analyse et diagnostic),
* **Correction** et amélioration,
* **Validation** par tests automatisés.



## Installation

### Prérequis

* Python 3.10 ou 3.11
* Git
* Clé API Google Gemini

### Installation

bash
git clone https://github.com/Lina-Douakha/Refactoring-Swarm-Equipe-13.git
cd Refactoring-Swarm-Equipe-13

python -m venv venv
.\venv\Scripts\activate (sous windows)

pip install -r requirements.txt


Configurer la clé API dans un fichier `.env` :

env
GOOGLE_API_KEY=VOTRE_CLE_API




## Utilisation

### Commande minimale

bash
python main.py --target_dir "./sandbox/"


### Avec génération automatique

bash
python main.py --target_dir "./sandbox/" --generate_tests --generate_docs




## Structure du projet


refactoring-swarm/
│
├── agents/          # Agents LLM (audit, correction, validation)
├── tools/           # Outils Pylint, Pytest, fichiers
├── prompts/         # Prompts des agents
├── sandbox/         # Code à analyser
├── logs/            # Journaux d'exécution
├── tests/           # Tests internes du système
├── main.py
└── README.md




## Licence

Projet à vocation pédagogique réalisé dans le cadre du module IGL.



## Équipe

Projet réalisé par l’équipe **She Codes**, composée d’étudiantes de 1CS à  
l’École Nationale Supérieure d’Informatique (ESI).

- DOUAKHA LINA
- NEKKAA OUISSAL
- BOUGHERARA KHADIJA
- TARARBIT AMELIA

Encadré par :Mr.BATATA Sofiane  
Année universitaire : 2025–2026
