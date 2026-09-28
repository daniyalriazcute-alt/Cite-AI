import os
import litellm

# HARD FIX FOR GROQ cache_breakpoint error
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

from crewai import Agent, Task, LLM

llm = LLM(model="groq/openai/gpt-oss-120b", temperature=0.2)

citation_agent = Agent(
    role="Secure Citation Expert",
    goal="Generate accurate citations in APA/MLA/Chicago/IEEE/Harvard",
    backstory="You are CiteGuard AI. Generate perfect citations. Never hallucinate. If missing, say 'Not found'.",
    llm=llm, verbose=False, allow_delegation=False, max_iter=3, cache=False
)

def create_citation_task(user_input, style="APA 7", lang="English"):
    return Task(
        description=f"Generate citation. Input: {user_input} Style: {style} Language: {lang} No hallucination, include DOI/URL if found.",
        expected_output=f"Perfect {style} citation in {lang}",
        agent=citation_agent,
    )
