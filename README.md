# The Refactoring Swarm

Système multi-agents intelligent pour la réparation et maintenance autonome de code Python.

## Objectif

* Ce projet implémente une architecture d'agents LLM capable de :
  * Analyser du code bugué
  * Détecter les erreurs automatiquement
  * Corriger le code
  * Valider les corrections


* Évaluation sur dataset :


placer vos fichiers .py buggés dans data/input/
python scripts/evaluate.py

Les résultats seront dans data/output/

## Architecture

* Le système utilise LangGraph pour orchestrer 4 agents :
* Analyzer - Analyse le code
* Bug Detector - Détecte les bugs
* Refactor - Corrige le code
* Validator - Valide le résultat

## Évaluation

* Le système est évalué sur :
* Taux de correction des bugs
* Préservation de la fonctionnalité
* Qualité du code produit

## Équipe

* DOUAKHA LINA
* NEKKAA OUISSAL
* TARARBIT AMELIA
* BOUGHERARA KHADIJA

## License

* Projet académique - IGL Module

## Installation 
1. Cloner le projet :
git clone https://github.com/Lina-Douakha/refactoring-swarm.git
cd refactoring-swarm
2. Créer un environnement virtuel :
python -m venv venv
3. Activer l’environnement virtuel :
venv\Scripts\activate
4. Installer les dépendances :
pip install -r requirements.txt
5. Configurer l’API :
cp .env.example .env
6. Vérifier que ça marche :
Pour tester rapidement :
streamlit run ui.py
ou bien:
dans data/input mettre un exemple de code buggé
utiliser le commande python scripts/evaluate.py pour avoir le code corrigé dans data/output
