from typing import Dict, Optional, Any
from src.utils.llm_helper import get_llm
import logging
import json
import re

logger = logging.getLogger(__name__)

def detect_language_with_llm(code: str, filename: str = '') -> Dict[str, Any]:
    """Détecte le langage de programmation via LLM"""
    
    llm = get_llm(temperature=0.0)
    llm.max_tokens = 150  # ✅ RÉDUIT pour économiser
    
    prompt = f"""Détecte le langage de programmation.

{'Fichier: ' + filename if filename else ''}

CODE:
```
{code[:300]}
```

Réponds UNIQUEMENT en JSON (sans markdown):
{{"language": "nom_du_langage", "confidence": "high/medium/low"}}
"""
    
    try:
        response = llm.invoke(prompt)
        result = response.content.strip()
        
        # ✅ NETTOYER les backticks markdown
        result = re.sub(r'```json\s*|\s*```', '', result).strip()
        
        # ✅ PARSER le JSON
        try:
            parsed = json.loads(result)
            language = parsed.get('language', 'unknown')
            logger.info(f"✅ Langage détecté: {language}")
            return {
                'language': language,
                'confidence': parsed.get('confidence', 'unknown'),
                'raw_response': result
            }
        except json.JSONDecodeError:
            # Fallback: extraire le langage manuellement
            match = re.search(r'"language"\s*:\s*"([^"]+)"', result)
            if match:
                language = match.group(1)
                logger.info(f"⚠️ Langage extrait manuellement: {language}")
                return {
                    'language': language,
                    'confidence': 'medium',
                    'raw_response': result
                }
            else:
                logger.warning(f"❌ Impossible de parser: {result}")
                return {
                    'language': 'unknown',
                    'error': 'Parse failed',
                    'raw_response': result
                }
        
    except Exception as e:
        logger.error(f"Erreur détection langage: {e}")
        return {
            'language': 'unknown',
            'error': str(e)
        }

def validate_syntax_with_llm(code: str, language: str) -> Dict[str, Any]:
    """Valide la syntaxe du code via LLM"""
    
    llm = get_llm(temperature=0.0)
    llm.max_tokens = 150  # ✅ RÉDUIT
    
    prompt = f"""Valide la syntaxe de ce code {language}:
```{language}
{code[:500]}
```

Réponds en JSON (sans markdown):
{{"is_valid": true/false, "has_errors": true/false}}
"""
    
    try:
        response = llm.invoke(prompt)
        result = response.content.strip()
        
        # Nettoyer les backticks
        result = re.sub(r'```json\s*|\s*```', '', result).strip()
        
        return {
            'validation_response': result,
            'checked_language': language
        }
        
    except Exception as e:
        logger.error(f"Erreur validation syntaxe: {e}")
        return {
            'is_valid': False,
            'error': str(e)
        }