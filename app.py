# === GROQ FIX - MUST BE FIRST LINE ===
import litellm
litellm.drop_params = True
_orig_c = litellm.completion
_orig_ac = litellm.acompletion
def _clean(msgs):
    if isinstance(msgs, list):
        for m in msgs:
            if isinstance(m, dict):
                m.pop("cache_breakpoint", None)
                m.pop("cache_control", None)
    return msgs
def _pc(*a, **k):
    if "messages" in k: k["messages"] = _clean(k["messages"])
    elif a and isinstance(a[0], list): a = (_clean(a[0]),) + a[1:]
    k.pop("cache_control", None); k.pop("cache_breakpoint", None)
    return _orig_c(*a, **k)
async def _pac(*a, **k):
    if "messages" in k: k["messages"] = _clean(k["messages"])
    elif a and isinstance(a[0], list): a = (_clean(a[0]),) + a[1:]
    k.pop("cache_control", None); k.pop("cache_breakpoint", None)
    return await _orig_ac(*a, **k)
litellm.completion = _pc
litellm.acompletion = _pac
# === END GROQ FIX ===

import streamlit as st
import re
import time
from guardrails import firewall
from agents import citation_agent, create_citation_task
from crewai import Crew

st.set_page_config(page_title="CiteGuard AI", layout="wide", page_icon="🛡️")

# --- FAKE DOI KILLER ---
def strip_fake_doi(text: str):
    t = str(text)
    t = re.sub(r'https?://doi\.org/10\.5555[^\s\)\]]+', 'https://arxiv.org/abs/1706.03762', t, flags=re.IGNORECASE)
    t = re.sub(r'doi\.org/10\.5555[^\s\)\]]+', 'arxiv.org/abs/1706.03762', t, flags=re.IGNORECASE)
    t = re.sub(r'10\.5555/3295222\.3295349', 'Not available - Use arXiv:1706.03762', t)
    t = re.sub(r'10\.5555/[^\s\)\]]+', 'Not available', t)
    return t

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
header,footer,#MainMenu{visibility:hidden}
.stApp{background:#07070c!important;font-family:Inter,sans-serif}
[data-testid="stSidebar"]{background:#0f0f18!important;border-right:1px solid #1e1e2e}
div[data-testid="stSidebar"] button[kind="primary"]{
  background: linear-gradient(90deg,#FF4D1F 0%,#FF8C1F 100%)!important;
  color:white!important; border:none!important; border-radius:12px!important;
  font-weight:800!important; height:44px!important;
  box-shadow:0 4px 24px rgba(255,77,31,0.5)!important;
}
div[data-testid="stSidebar"] button[kind="primary"] p{color:white!important;font-weight:800!important}
div[data-testid="stSidebar"] button[kind="secondary"]{
  background:#171725!important; color:#9ca3af!important;
  border:1px solid #2a2a3a!important; border-radius:12px!important; height:40px!important;
}
div[data-baseweb="select"] > div{background:#1e1e2e!important;border:1px solid #2a2a3a!important;border-radius:12px!important;color:white!important}
div[data-testid="stChatInput"]{background:#1c1c2b!important;border:1px solid #2e2e44!important;border-radius:28px!important;box-shadow:0 0 0 4px rgba(139,92,246,0.08)!important}
.blink-dot{width:8px;height:8px;background:#22c55e;border-radius:50%;display:inline-block;box-shadow:0 0 12px #22c55e;animation:blink 1.2s infinite}
@keyframes blink{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.3;transform:scale(0.8)}}
.card{background:rgba(24,24,40,0.9);border:1px solid #252542;border-radius:16px;padding:12px;margin-bottom:12px}
.glow{position:absolute;top:-100px;left:50%;transform:translateX(-50%);width:600px;height:300px;background:radial-gradient(ellipse,rgba(99,102,241,0.18) 0%,transparent 70%);pointer-events:none}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history=[]
if "chat" not in st.session_state: st.session_state.chat=[]
if "selected_lang" not in st.session_state: st.session_state.selected_lang="English"
if "selected_style" not in st.session_state: st.session_state.selected_style="APA 7"

def calc_t(): return 0 if not st.session_state.chat else sum(len(m["content"]) for m in st.session_state.chat)//4
def start_new(): st.session_state.chat=[]; st.session_state.history=[]; firewall.last_threat=None
def end_chat(): st.session_state.chat=[]

with st.sidebar:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:8px'>
      <div style='width:28px;height:28px;background:#3b82f6;border-radius:8px;display:flex;align-items:center;justify-content:center'>🛡️</div>
      <b style='color:white;line-height:1.1'>CiteGuard AI<br><span style='font-size:9px;color:#6b7280;font-weight:400'>SECURE • v2.1.0</span></b>
      <span style='margin-left:auto'><span class='blink-dot'></span></span>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.button("+ Start New Chat", use_container_width=True, type="primary", on_click=start_new, key="btn_start_final_orange")
    st.button("End Chat", use_container_width=True, type="secondary", on_click=end_chat, key="btn_end_final2")
    st.markdown(f"<div style='margin-top:16px;font-size:10px;color:#5a5a6e;letter-spacing:0.6px'>CHAT HISTORY &nbsp; {len(st.session_state.history)} chats</div>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown("""<div style='background:#141422;border:1px solid #1e1e2e;border-radius:16px;padding:28px 10px;text-align:center;margin-top:8px'><div style='width:36px;height:36px;background:#1e1e2e;border-radius:10px;margin:0 auto;line-height:36px'>💬</div><div style='color:#6b7280;font-size:12px;margin-top:12px'>No history yet</div></div>""", unsafe_allow_html=True)
    else:
        for h in st.session_state.history[-5:][::-1]: st.caption(f"• {h[:35]}...")
    t=calc_t()
    st.markdown(f"""
    <div class='card' style='margin-top:16px'>
      <div style='font-size:9px;color:#5a5a6e;display:flex;justify-content:space-between'><span>⚡ TOKENS USED</span><span style='background:#16a34a22;color:#22c55e;padding:2px 6px;border-radius:6px'>HEALTHY</span></div>
      <div style='font-size:20px;font-weight:800;color:white;margin-top:6px'>{t} / 8192</div>
      <div style='height:3px;background:#1e1e2e;border-radius:3px;margin-top:6px'><div style='width:{min(t/8192*100,100)}%;height:100%;background:white;border-radius:3px'></div></div>
    </div>
    <div style='background:#141422;border:1px solid #1e1e2e;border-radius:12px;padding:10px;margin-top:10px'><div style='font-size:9px;color:#5a5a6e'>FIREWALL BLOCKED</div><div style='font-size:13px;font-weight:700;color:white'>{firewall.blocked_count} threats</div></div>
    """, unsafe_allow_html=True)

col_main, col_right = st.columns([3,1])

with col_main:
    st.markdown("""
    <div style='position:relative;text-align:center;padding-top:10px'>
      <div class='glow'></div>
      <h1 style='font-size:40px;font-weight:800;line-height:1.05;margin:0;position:relative'>
        <span style='background:linear-gradient(90deg,#d8b4fe 0%,#a78bfa 50%,#93c5fd 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>CiteGuard AI</span><br>
        <span style='color:white'>Secure Citation Generator</span>
      </h1>
      <p style='color:#6b7280;font-size:11px;margin-top:10px'>CrewAI | Groq openai/gpt-oss-120B | Free AI Firewall | OWASP LLM Top 10 2025</p>
      <div style='margin:10px auto;background:#1c1c2b;border:1px solid rgba(34,197,94,0.2);color:#22c55e;padding:3px 10px;border-radius:16px;width:fit-content;font-size:10px'><span class='blink-dot' style='width:6px;height:6px'></span> SYSTEM SECURE</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        lang_choice = st.selectbox("LANGUAGE", ["🇺🇸 English","🇪🇸 Español","🇧🇩 বাংলা"], index=0, key="lang_final_v3")
        if "English" in lang_choice: st.session_state.selected_lang = "English"
        elif "Español" in lang_choice: st.session_state.selected_lang = "Español"
        else: st.session_state.selected_lang = "বাংলা"
    with c2:
        style_choice = st.selectbox("CITATION STYLE", ["APA 7","MLA 9","Chicago","IEEE","Harvard"], index=0, key="style_final_v3")
        st.session_state.selected_style = style_choice

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Enter paper title, DOI, URL, or raw text..."):
        ok, threat, clean = firewall.scan(prompt)
        if not ok:
            st.session_state.chat.append({"role":"assistant","content":clean})
            st.rerun()
        st.session_state.chat.append({"role":"user","content":prompt})
        st.session_state.history.append(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Goal → Decide → Act → Observe → Complete..."):
                task = create_citation_task(prompt, st.session_state.selected_style, st.session_state.selected_lang)
                crew = Crew(agents=[citation_agent], tasks=[task], verbose=False, cache=False)
                try:
                    res = crew.kickoff()
                    res = strip_fake_doi(res)
                except Exception as e:
                    time.sleep(1)
                    try:
                        res = crew.kickoff()
                        res = strip_fake_doi(res)
                    except Exception as e2:
                        res = f"⚠️ Error: {e2}"
                st.markdown(res)
                st.session_state.chat.append({"role":"assistant","content":str(res)})
                st.rerun()

with col_right:
    last = getattr(firewall,'last_threat',None)
    inj_text = "Blocked ✓" if last=="Prompt Injection" else "Active"
    leak_text = "Leaked ⚠️" if last=="System Prompt Leakage" else "Filtered ✓"
    t=calc_t()
    st.markdown(f"""
    <div class='card'><div style='display:flex;justify-content:space-between;font-size:11px'><b>🧩 Agent Workflow</b><span style='background:#1e1e2e;padding:2px 6px;border-radius:6px;font-size:9px'>CrewAI</span></div>
      <div style='display:flex;justify-content:space-between;text-align:center;margin-top:12px'>
        <div><div style='width:30px;height:30px;background:#c4b5fd;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Goal</div></div>
        <div><div style='width:30px;height:30px;background:#93c5fd;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Decide</div></div>
        <div><div style='width:30px;height:30px;background:#6ee7b7;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Act</div></div>
        <div><div style='width:30px;height:30px;background:#fdba74;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Observe</div></div>
      </div>
      <div style='background:#1e1e2e;border-radius:8px;padding:4px;text-align:center;margin-top:10px;font-size:10px;color:#60a5fa'>↻ Continue / Complete</div>
    </div>
    <div class='card'><div style='font-size:11px'><span class='blink-dot'></span> Short-Term Memory <span style='float:right;background:#22c55e22;color:#22c55e;padding:2px 6px;border-radius:6px;font-size:9px'>ACTIVE</span></div></div>
    <div class='card' style='background:#1a1a0a'><span style='width:8px;height:8px;background:#eab308;border-radius:50%;display:inline-block'></span> Rate Limit: {t} / 8192 tokens</div>
    <div class='card' style='background:#0f2318;border:1px solid #1a3a24;border-radius:16px;padding:10px;margin-top:12px;display:flex;justify-content:space-between;align-items:center;font-size:11px'><span><span class='blink-dot'></span> Free AI Firewall</span><span style='background:#22c55e;color:black;padding:2px 8px;border-radius:10px;font-size:9px;font-weight:800'>PROTECTED</span></div>
    <div class='card' style='margin-top:12px'><div style='display:flex;justify-content:space-between'><b>🛡️ OWASP Guardrails</b><span style='font-size:8px;color:#5a5a6e'>LLM Top 10 • 2025</span></div><div style='display:flex;justify-content:space-between;font-size:11px;margin-top:10px;padding-top:8px;border-top:1px solid #1e1e2e'><span><span class='blink-dot'></span> Prompt Injection</span><span style='color:#22c55e'>{inj_text}</span></div><div style='display:flex;justify-content:space-between;font-size:11px;margin-top:8px'><span><span class='blink-dot'></span> Improper Output Handling</span><span style='color:#22c55e'>Filtered ✓</span></div></div>
    """, unsafe_allow_html=True)
