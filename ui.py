import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.core.orchestrator import RefactoringOrchestrator
from src.utils.code_utils import is_valid_python, count_lines
import time

# Configuration de la page
st.set_page_config(
    page_title="The Refactoring Swarm",
    page_icon="🐝",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 1.2rem;
        padding: 0.5rem;
        border-radius: 10px;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialiser l'état de session
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = RefactoringOrchestrator()
if 'history' not in st.session_state:
    st.session_state.history = []

# En-tête
st.markdown('<div class="main-header">🐝 The Refactoring Swarm</div>', unsafe_allow_html=True)
st.markdown("### Système Multi-Agents pour la Correction Automatique de Code")

# Layout en colonnes
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("#### 📝 Code Bugué")
    
    # Zone de texte pour le code
    code_input = st.text_area(
        "Collez votre code Python bugué ici:",
        height=400,
        placeholder="""def calculate_average(numbers):
    total = 0
    for num in numbers
        total += num
    return total / len(numbers)"""
    )
    
    # Description optionnelle
    description = st.text_input(
        "Description de la tâche (optionnel):",
        placeholder="Ex: Corriger les erreurs de syntaxe"
    )
    
    # Statistiques du code original
    if code_input:
        st.markdown("**📊 Statistiques:**")
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Lignes de code", count_lines(code_input))
        with col_stat2:
            is_valid = is_valid_python(code_input)
            st.metric("Syntaxe valide", "✅" if is_valid else "❌")

with col2:
    st.markdown("#### ✅ Code Corrigé")
    
    # Placeholder pour le code corrigé
    corrected_placeholder = st.empty()
    
    # Placeholder pour les statistiques
    stats_placeholder = st.empty()

# Bouton de correction
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    fix_button = st.button("🚀 Corriger le Code", type="primary", use_container_width=True)

with col_btn2:
    clear_button = st.button("🗑️ Effacer", use_container_width=True)

with col_btn3:
    download_button = st.empty()

# Logique de correction
if fix_button and code_input:
    with st.spinner('🐝 Les agents travaillent...'):
        # Barre de progression
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📊 Analyse du code...")
        progress_bar.progress(25)
        time.sleep(0.5)
        
        status_text.text("🐛 Détection des bugs...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        status_text.text("🔧 Refactoring en cours...")
        progress_bar.progress(75)
        time.sleep(0.5)
        
        # Traitement réel
        result = st.session_state.orchestrator.process_code(
            code=code_input,
            description=description
        )
        
        status_text.text("✅ Validation finale...")
        progress_bar.progress(100)
        time.sleep(0.3)
        
        # Effacer la barre de progression
        progress_bar.empty()
        status_text.empty()
    
    # Afficher les résultats
    if result['success']:
        corrected_code = result['corrected_code']
        
        with col2:
            # Afficher le code corrigé
            corrected_placeholder.code(corrected_code, language='python')
            
            # Statistiques du code corrigé
            stats_placeholder.markdown("**📊 Statistiques:**")
            with stats_placeholder:
                col_stat3, col_stat4, col_stat5 = st.columns(3)
                with col_stat3:
                    st.metric("Lignes", count_lines(corrected_code))
                with col_stat4:
                    st.metric("Itérations", result['iterations'])
                with col_stat5:
                    approved = "✅" if result['approved'] else "⚠️"
                    st.metric("Validé", approved)
        
        # Message de succès
        if result['approved']:
            st.markdown('<div class="success-box">✅ <b>Code validé et prêt à l\'utilisation!</b></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">⚠️ <b>Code corrigé mais validation incomplète</b></div>', unsafe_allow_html=True)
        
        # Bouton de téléchargement
        with col_btn3:
            st.download_button(
                label="💾 Télécharger",
                data=corrected_code,
                file_name="code_corrected.py",
                mime="text/plain",
                use_container_width=True
            )
        
        # Ajouter à l'historique
        st.session_state.history.append({
            'original': code_input,
            'corrected': corrected_code,
            'approved': result['approved'],
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Afficher les détails
        with st.expander("🔍 Détails de l'analyse"):
            tab1, tab2, tab3 = st.tabs(["📊 Analyse", "🐛 Bugs", "✅ Validation"])
            
            with tab1:
                st.json(result['analysis'])
            
            with tab2:
                st.json(result['bugs'])
            
            with tab3:
                st.json(result['validation'])
    
    else:
        st.error(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")

elif fix_button and not code_input:
    st.warning("⚠️ Veuillez entrer du code à corriger")

# Bouton effacer
if clear_button:
    st.rerun()

# Historique
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📚 Historique des Corrections")
    
    for idx, entry in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Correction {len(st.session_state.history) - idx} - {entry['timestamp']}"):
            col_hist1, col_hist2 = st.columns(2)
            
            with col_hist1:
                st.markdown("**Code Original:**")
                st.code(entry['original'][:200] + "..." if len(entry['original']) > 200 else entry['original'], language='python')
            
            with col_hist2:
                st.markdown("**Code Corrigé:**")
                st.code(entry['corrected'][:200] + "..." if len(entry['corrected']) > 200 else entry['corrected'], language='python')
                status = "✅ Validé" if entry['approved'] else "⚠️ Non validé"
                st.markdown(f"**Statut:** {status}")

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    **The Refactoring Swarm** utilise 4 agents IA:
    
    1. 📊 **Analyzer** - Analyse le code
    2. 🐛 **Bug Detector** - Détecte les bugs
    3. 🔧 **Refactor** - Corrige le code
    4. ✅ **Validator** - Valide le résultat
    
    **Technologies:**
    - LangChain / LangGraph
    - OpenRouter API
    - Multi-Agent System
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques")
    if st.session_state.history:
        total = len(st.session_state.history)
        approved = sum(1 for h in st.session_state.history if h['approved'])
        st.metric("Total corrections", total)
        st.metric("Taux de validation", f"{approved/total*100:.0f}%")
    else:
        st.info("Aucune correction effectuée")
    
    st.markdown("---")
    st.markdown("### 🔗 Liens")
    st.markdown("- [Documentation](docs/architecture.md)")
    st.markdown("- [GitHub](https://github.com)")
    
    # Bouton pour effacer l'historique
    if st.button("🗑️ Effacer l'historique", use_container_width=True):
        st.session_state.history = []
        st.rerun()