
# Architecture du Refactoring Swarm

## Vue d'ensemble

Le système utilise une architecture multi-agents basée sur LangGraph pour réparer automatiquement du code bugué.

## Workflow

\`\`\`
Code bugué
    ↓
[Analyzer Agent] → Analyse le code
    ↓
[Bug Detector Agent] → Détecte les bugs
    ↓
[Refactor Agent] → Corrige le code
    ↓
[Validator Agent] → Valide le résultat
    ↓
Code corrigé ✅
\`\`\`

## Agents

### 1. Analyzer Agent
- **Rôle**: Analyse statique du code
- **Output**: Rapport d'analyse avec métriques

### 2. Bug Detector Agent
- **Rôle**: Détection des bugs (syntaxe, logique, sécurité)
- **Output**: Liste des bugs avec gravité

### 3. Refactor Agent
- **Rôle**: Correction et refactoring du code
- **Output**: Code corrigé

### 4. Validator Agent
- **Rôle**: Validation du code corrigé
- **Output**: Décision d'approbation

## Retry Logic

Le système peut effectuer jusqu'à 3 itérations de correction si le code n'est pas validé.

## Utilisation

\`\`\`bash
# Traiter un fichier
python scripts/run_swarm.py

# Évaluer sur un dataset
python scripts/evaluate.py
