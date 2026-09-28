import re

class Firewall:
    def __init__(self):
        self.blocked_count = 127
        self.last_threat = None
        self.status = {
  "Prompt Injection": "Active",
  "System Prompt Leakage": "Active",
  "Improper Output Handling": "Active"  # <-- Should be Active on start
}
        }

    def scan(self, text: str):
        low = text.lower()

        # 1. Prompt Injection
        for pat in ["ignore previous", "reveal system prompt", "reveal your system", "bypass", "jailbreak", "dan mode", "disregard previous", "you are now", "ignore all previous"]:
            if pat in low:
                self.blocked_count += 1
                self.last_threat = "Prompt Injection"
                self.status["Prompt Injection"] = "Blocked ✓"
                return False, "Prompt Injection", "🛡️ **Firewall blocked: Prompt Injection** — Provide paper title, DOI, URL, or abstract."

        # 2. SYSTEM PROMPT LEAKAGE
        for pat in ["what is your system prompt", "show system prompt", "what is your prompt", "system instructions", "your instructions", "reveal prompt", "show me your system", "what is your system instructions"]:
            if pat in low:
                self.blocked_count += 1
                self.last_threat = "System Prompt Leakage"
                self.status["System Prompt Leakage"] = "Leaked ⚠️ → Blocked ✓"
                return False, "System Prompt Leakage", "🛡️ **Firewall blocked: System Prompt Leakage** — System prompt is protected. Provide paper title instead."

        # 3. XSS / Output Handling
        if "<script>" in low or "onerror=" in low or "javascript:" in low or "<img" in low:
            self.blocked_count += 1
            self.last_threat = "Improper Output Handling"
            clean = re.sub(r'<[^>]+>', '', text)
            self.status["Improper Output Handling"] = "Filtered ✓"
            return False, "Improper Output Handling", f"🛡️ **Output sanitized**: {clean}"

        return True, None, text

firewall = Firewall()
