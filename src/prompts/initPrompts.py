"""
Centralized prompt initialization
"""

from .auditor_prompts import AUDITOR_SYSTEM_PROMPT
from .fixer_prompts import FIXER_SYSTEM_PROMPT, FIXER_RETRY_PROMPT
from .judge_prompts import JUDGE_SYSTEM_PROMPT

# Export main prompts
__all__ = [
    'AUDITOR_SYSTEM_PROMPT',
    'FIXER_SYSTEM_PROMPT',
    'FIXER_RETRY_PROMPT',
    'JUDGE_SYSTEM_PROMPT'
]

def get_prompt_summary():
    """Display prompt summary"""
    prompts = {
        "Auditor": len(AUDITOR_SYSTEM_PROMPT),
        "Fixer": len(FIXER_SYSTEM_PROMPT),
        "Fixer (retry)": len(FIXER_RETRY_PROMPT),
        "Judge": len(JUDGE_SYSTEM_PROMPT)
    }
    
    print("📋 Prompt Summary:")
    print("-" * 30)
    for name, length in prompts.items():
        print(f"{name:15} : {length:6} chars")
    print(f"\nTotal : {sum(prompts.values()):6} chars")
    
    return prompts

# Quick test
if __name__ == "__main__":
    get_prompt_summary()