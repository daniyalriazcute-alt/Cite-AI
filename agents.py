import litellm
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

llm = LLM(model="groq/openai/gpt-oss-120b", temperature=0.0)

citation_agent = Agent(
    role="Secure Citation Expert - Zero Hallucination",
    goal="Generate 100% accurate citations with NO fake DOIs",
    backstory="""You are CiteGuard AI, strict academic librarian.
    CRITICAL:
    - NEVER invent DOI with 10.5555
    - For Attention is all you need: NO DOI exists, use arXiv:1706.03762
    - If DOI unknown, write DOI: Not available
    - Always include real URLs: https://arxiv.org/abs/1706.03762
    """,
    llm=llm, verbose=False, allow_delegation=False, max_iter=2, cache=False
)

def create_citation_task(user_input, style="APA 7", lang="English"):
    return Task(
        description=f"""
        Generate citation for: {user_input}
        Style: {style} | Language: {lang}

        MANDATORY RULES:
        - DO NOT INCLUDE ANY DOI with 10.5555 - IT IS FORBIDDEN
        - For Attention is all you need, output MUST be:
          Vaswani et al. (2017). Attention is all you need. In NeurIPS 30.
          URL: https://arxiv.org/abs/1706.03762
          DOI: Not available (NIPS does not assign DOI)
        - Only include DOI if user gave it and it is real (starts with 10. and not 10.5555)

        Input: {user_input}
        """,
        expected_output=f"Accurate {style} citation in {lang} with real arXiv URL, no fake DOI",
        agent=citation_agent,
    )
