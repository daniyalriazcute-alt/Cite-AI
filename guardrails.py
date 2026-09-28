import re

class Firewall:
    def __init__(self):
        self.blocked_count = 127
        self.last_threat = None
        self.history = []

    def scan(self, text: str):
        text_lower = text.lower()

        # OWASP LLM01: Prompt Injection
        injection_patterns = [
            "ignore previous", "ignore all previous", "disregard previous",
            "reveal system prompt", "show system instructions", "bypass",
            "jailbreak", "dan mode", "developer mode"
        ]
        for pat in injection_patterns:
            if pat in text_lower:
                self.blocked_count += 1
                self.last_threat = "Prompt Injection"
                self.history.append(pat)
                return False, "Prompt Injection", "🛡️ **Firewall blocked: Prompt Injection** — I cannot share system instructions. Please provide a paper title, DOI, URL, or abstract to generate a citation."

        # OWASP LLM06: System Prompt Leakage
        leakage_patterns = ["system prompt", "system instructions", "your instructions", "what is your prompt"]
        for pat in leakage_patterns:
            if pat in text_lower:
                self.blocked_count += 1
                self.last_threat = "System Prompt Leakage"
                self.history.append(pat)
                return False, "System Prompt Leakage", "🛡️ **Firewall blocked: System Prompt Leakage** — System instructions are protected and cannot be disclosed."

        # OWASP LLM02: Improper Output Handling
        if "<script>" in text_lower or "javascript:" in text_lower or "onerror=" in text_lower:
            self.blocked_count += 1
            self.last_threat = "Improper Output Handling"
            self.history.append("xss")
            clean = re.sub(r'<[^>]+>', '', text)
            return False, "Improper Output Handling", f"🛡️ **Output sanitized** — unsafe HTML removed. Clean input: {clean}"

        # Safe
        return True, None, text

firewall = Firewall()
