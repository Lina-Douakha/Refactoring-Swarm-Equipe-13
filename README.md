@"
# 🐝 The Refactoring Swarm

Système multi-agents intelligent pour la réparation et maintenance autonome de code Python.

## 🎯 Objectif

Ce projet implémente une architecture d'agents LLM capable de:
- Analyser du code bugué
- Détecter les erreurs automatiquement
- Corriger le code
- Valider les corrections

## 📁 Structure

\`\`\`
refactoring-swarm/
├── src/
│   ├── agents/         # Agents intelligents
│   ├── core/           # Orchestrateur et workflow
│   └── utils/          # Utilitaires
├── data/
│   ├── input/          # Code bugué à corriger
│   └── output/         # Code corrigé
├── scripts/            # Scripts d'exécution
└── tests/              # Tests unitaires
\`\`\`

## 🚀 Installation

\`\`\`bash
# 1. Cloner le projet
cd refactoring-swarm

# 2. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'API
cp .env.example .env
# Éditer .env avec votre clé OpenRouter
\`\`\`

## 💻 Utilisation

### Test rapide

\`\`\`bash
python scripts/run_swarm.py
\`\`\`

### Évaluation sur dataset

\`\`\`bash
# Placer vos fichiers .py buggés dans data/input/
python scripts/evaluate.py
# Les résultats seront dans data/output/
\`\`\`

## 🏗️ Architecture

Le système utilise **LangGraph** pour orchestrer 4 agents:

1. **Analyzer** - Analyse le code
2. **Bug Detector** - Détecte les bugs
3. **Refactor** - Corrige le code
4. **Validator** - Valide le résultat

## 📊 Évaluation

Le système est évalué sur:
- Taux de correction des bugs
- Préservation de la fonctionnalité
- Qualité du code produit

## 👥 Équipe

- DOUAKHA LINA
- NEKKAA OUISSAL
- TARARBIT AMELIA
- BOUGHERARA KHADIJA

## 📄 License

Projet académique - IGL Module
