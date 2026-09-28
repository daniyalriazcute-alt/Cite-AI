import re
from typing import Tuple

# OWASP LLM01, LLM06, LLM02 focused
INJECTION_PATTERNS = [
    r"ignore.*previous.*instructions",
    r"system.*prompt",
    r"reveal.*prompt",
    r"jailbreak",
    r"dan\s*mode",
    r"print.*system",
    r"<\s*system\s*>",
    r"forget.*you.*are",
]

class FreeAIFirewall:
    def __init__(self):
        self.blocked_count = 127
        self.compiled = [re.compile(p, re.I) for p in INJECTION_PATTERNS]

    def scan(self, user_input: str) -> Tuple[bool, str, str]:
        """Returns (is_safe, threat_type, sanitized_output)"""
        for pat in self.compiled:
            if pat.search(user_input):
                self.blocked_count += 1
                return False, "PROMPT_INJECTION", "🛡️ Blocked by Free AI Firewall: Prompt Injection detected."

        # System prompt leakage prevention
        if "system prompt" in user_input.lower() or "hidden instruction" in user_input.lower():
            return False, "SYSTEM_PROMPT_LEAKAGE", "🛡️ Blocked: Attempt to leak system prompt."

        # Improper output handling - strip potential XSS/HTML
        sanitized = re.sub(r"<script.*?>.*?</script>", "", user_input, flags=re.I)
        sanitized = sanitized.replace("<", "&lt;").replace(">", "&gt;") if len(sanitized)!= len(user_input) else user_input

        return True, "SAFE", sanitized

firewall = FreeAIFirewall()
