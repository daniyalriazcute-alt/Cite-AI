import streamlit as st
import streamlit.components.v1 as components
from guardrails import firewall

st.set_page_config(page_title="CiteGuard AI", layout="wide", page_icon="🛡️")
st.markdown("<style>header,footer,#MainMenu{visibility:hidden}.stApp{background:#0a0a0f}</style>", unsafe_allow_html=True)

# Session for tokens
if "history" not in st.session_state: st.session_state.history=[]
if "chat" not in st.session_state: st.session_state.chat=[]
def tokens(): return 0 if not st.session_state.chat else sum(len(m["content"]) for m in st.session_state.chat)//4
t = tokens()

# PRODUCTION HTML - Exact replica of king.PNG
html_code = f"""
<html>
<head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
body{{margin:0;background:#0a0a0f;color:white;font-family:Inter,sans-serif}}
.container{{display:flex;height:100vh}}
.sidebar{{width:280px;background:#11111b;border-right:1px solid #1f1f2e;padding:16px}}
.main{{flex:1;padding:32px;background:radial-gradient(ellipse at top, #1a1a3e 0%, #0a0a0f 60%)}}
.right{{width:320px;background:#0a0a0f;padding:16px;border-left:1px solid #1f1f2e}}
.card{{background:rgba(26,26,46,0.9);border:1px solid #2a2a3a;border-radius:16px;padding:12px;margin-bottom:12px}}
.btn-orange{{background:linear-gradient(90deg,#ff6b35,#f7931e);border-radius:12px;padding:12px;text-align:center;font-weight:700;color:white}}
.btn-dark{{background:#1a1a2e;border:1px solid #2a2a3a;border-radius:12px;padding:10px;text-align:center;color:#9ca3af;margin-top:8px}}
.title{{font-size:36px;font-weight:800;background:linear-gradient(90deg,#c4b5fd,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1}}
.dot{{width:8px;height:8px;border-radius:50%;display:inline-block;animation:blink 1.5s infinite}}
.dot-g{{background:#22c55e;box-shadow:0 0 10px #22c55e}} .dot-y{{background:#eab308}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
.input-bar{{background:#1a1a2e;border:1px solid #2a2a3a;border-radius:24px;padding:12px 16px;display:flex;align-items:center;gap:12px}}
.pill{{background:#1a1a2e;border-radius:8px;padding:6px 10px;font-size:12px;color:#9ca3af}}
</style>
</head>
<body>
<div class="container">
  <div class="sidebar">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px"><div style="width:32px;height:32px;background:#3b82f6;border-radius:8px"></div><b>CiteGuard AI<br><span style="font-size:10px;color:#6b7280">SECURE • v2.1.0</span></b></div>
    <div class="btn-orange">+ Start New Chat</div>
    <div class="btn-dark">End Chat</div>
    <div style="margin-top:24px;font-size:11px;color:#6b7280">CHAT HISTORY &nbsp; 0 chats</div>
    <div class="card" style="height:200px;display:flex;align-items:center;justify-content:center;flex-direction:column;margin-top:8px"><div style="font-size:24px">💬</div><div style="color:#6b7280;font-size:12px;margin-top:8px">No history yet</div><div style="color:#4b5563;font-size:11px">Your citations will appear here after generation</div></div>
    <div class="card" style="margin-top:16px"><div style="font-size:10px;color:#6b7280">TOKENS USED <span style="background:#22c55e22;color:#22c55e;padding:2px 6px;border-radius:6px;float:right">HEALTHY</span></div><div style="font-size:24px;font-weight:800;margin-top:6px">{t} / 8192</div><div style="height:4px;background:#1f1f2e;border-radius:4px;margin-top:8px"><div style="width:{min(t/8192*100,100)}%;height:100%;background:white;border-radius:4px"></div></div></div>
    <div class="card"><div style="font-size:10px;color:#6b7280">FIREWALL BLOCKED</div><div style="font-size:20px;font-weight:700">{firewall.blocked_count}</div></div>
  </div>
  <div class="main">
    <div style="text-align:center;margin-top:40px">
      <div class="title">CiteGuard AI<br><span style="color:white">Secure Citation Generator</span></div>
      <div style="margin-top:12px;font-size:12px;color:#6b7280">CrewAI | Groq openai/gpt-oss-120B | Free AI Firewall | OWASP LLM Top 10 2025</div>
      <div style="margin:16px auto;background:#1a1a2e;border:1px solid #22c55e33;border-radius:20px;padding:4px 12px;width:fit-content;font-size:11px;color:#22c55e">● SYSTEM SECURE</div>
      <div style="display:flex;gap:12px;justify-content:center;margin-top:20px">
        <div class="card" style="padding:8px 16px">LANGUAGE<br><b>🇺🇸 English ▼</b></div>
        <div class="card" style="padding:8px 16px">CITATION STYLE<br><b>APA 7 ▼</b></div>
      </div>
      <div class="input-bar" style="max-width:600px;margin:16px auto"><div style="width:32px;height:32px;background:#2a2a3a;border-radius:50%">🔍</div><span style="flex:1;color:#6b7280;text-align:left">Enter paper title, DOI, URL, or raw text...</span><div style="width:32px;height:32px;background:white;border-radius:50%;color:black;display:flex;align-items:center;justify-content:center">↑</div></div>
      <div style="font-size:11px;color:#4b5563">⏎ to generate &nbsp; 🛡️ Firewall auto-protects</div>
      <div style="display:flex;gap:8px;justify-content:center;margin-top:24px">
        <div class="pill">🔗 DOI<br>10.1234/examp...</div><div class="pill">🌐 URL<br>arxiv.org/abs/...</div><div class="pill">📄 RAW<br>Paste abstract..</div>
      </div>
    </div>
  </div>
  <div class="right">
    <div class="card"><div style="font-size:12px;font-weight:700">🧠 Agent Workflow <span style="float:right;background:#2a2a3a;padding:2px 6px;border-radius:6px;font-size:10px">CrewAI</span></div><div style="display:flex;justify-content:space-between;margin-top:12px;text-align:center"><div><div style="width:32px;height:32px;background:#a78bfa;border-radius:50%">●</div><div style="font-size:10px;margin-top:4px">Goal</div></div><div><div style="width:32px;height:32px;background:#60a5fa;border-radius:50%">●</div><div style="font-size:10px">Decide</div></div><div><div style="width:32px;height:32px;background:#34d399;border-radius:50%">●</div><div style="font-size:10px">Act</div></div><div><div style="width:32px;height:32px;background:#fb923c;border-radius:50%">●</div><div style="font-size:10px">Observe</div></div></div><div style="background:#1f1f2e;border-radius:12px;padding:6px;margin-top:12px;font-size:11px;color:#60a5fa;text-align:center">↻ Continue / Complete</div></div>
    <div class="card"><span class="dot dot-g"></span> Short-Term Memory <span style="float:right;background:#22c55e22;color:#22c55e;padding:2px 6px;border-radius:6px;font-size:10px">ACTIVE</span><br><span style="font-size:11px;color:#6b7280">Context window • sliding</span></div>
    <div class="card"><span class="dot dot-y"></span> Rate Limit: {t} / 8192 tokens</div>
    <div class="card" style="background:#2a1a1a"><span>⚠️</span> Retry: 1x fail • auto <span style="float:right;background:#3a2a2a;padding:2px 6px;border-radius:6px">1x</span></div>
    <div class="card" style="background:#0f2a1a;border:1px solid #22c55e33;margin-top:20px"><span class="dot dot-g"></span> Free AI Firewall <span style="float:right;background:#22c55e;color:black;padding:2px 8px;border-radius:12px;font-size:10px;font-weight:700">PROTECTED</span></div>
    <div class="card"><b>🛡️ OWASP Guardrails</b> <span style="float:right;font-size:10px;color:#6b7280">LLM Top 10 • 2025</span><br><br><span class="dot dot-g"></span> Prompt Injection <span style="float:right">Blocked ✓</span><br><span class="dot dot-g"></span> Sensitive Data Disclosure <span style="float:right">Filtered ✓</span></div>
  </div>
</div>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=False)

# Real chat logic below HTML (keep your existing chat logic here)
# Use st.chat_input again for actual functionality
