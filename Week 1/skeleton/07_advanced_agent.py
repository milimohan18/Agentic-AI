"""
07 · ADVANCED TRACK — native function calling.  (optional · for fast finishers)

In Labs 3–6 the agent chose tools by writing text like  ACTION: calc[...]  and
we parsed it with a regex. That works, but every serious provider now offers
NATIVE FUNCTION / TOOL CALLING: you describe your tools as JSON schemas, and the
model returns a structured, validated tool call — no fragile string parsing.
This is exactly what Module 2 (Tool Use & Function Calling) is about; you're
getting a head start.

    You  ->  give the model a `tools` schema
    Model ->  returns tool_calls (name + JSON arguments)
    You  ->  run the tool, hand back the result, loop until it stops

This file targets the OpenAI / Groq chat-completions tools API (same shape).
Set LLM_PROVIDER=openai or groq in your .env.

-------------------------------------------------------------------
YOUR TASKS  (tiered — do as many as you can)
  TODO 1 · describe the calculator as a JSON tool schema (TOOLS).
  TODO 2 · run the loop: send messages+tools; if the model returns tool_calls,
           execute each and append a tool result message; else print the answer.

  STRETCH CHALLENGES (see CHALLENGES at the bottom) — reflection, a 2nd tool,
  AST-safe execution, malformed-argument handling, and an MCP write-up.
-------------------------------------------------------------------
Run it:  python skeleton/07_advanced_agent.py
Reference: trainer/07_advanced_agent.py
"""

import sys, os, json, ast, operator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.llm_client import LLMClient

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg}

def _ev(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in _OPS: return _OPS[type(n.op)](_ev(n.left), _ev(n.right))
    if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS: return _OPS[type(n.op)](_ev(n.operand))
    raise ValueError("unsafe expression")

def calculator(expression: str):
    """AST-safe calculator (no eval)."""
    return _ev(ast.parse(expression, mode="eval").body)


# Level 1 · a second tool the model can choose
CATALOGUE = {"widget": 25, "gadget": 40, "sprocket": 12, "bolt": 3}

def price_lookup(item: str):
    """Return the catalogue price of one item."""
    item = item.strip().lower()
    if item not in CATALOGUE:
        raise ValueError(f"no price for '{item}'")
    return CATALOGUE[item]


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate an arithmetic expression using numbers, + - * / and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The expression to evaluate, e.g. '(23 * 7) + 19'.",
                    },
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "price_lookup",
            "description": "Look up the unit price of one item in the shop catalogue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {"type": "string", "description": "Item name, e.g. 'widget'."},
                },
                "required": ["item"],
            },
        },
    },
]

# Level 3 · tool registry: name -> (function, required argument)
TOOL_FUNCS = {"calculator": (calculator, "expression"), "price_lookup": (price_lookup, "item")}


def run_tool(name: str, raw_args: str):
    """Validate the model's tool call and run it; never raises, returns a string."""
    if name not in TOOL_FUNCS:
        return f"error: unknown tool '{name}'"
    try:
        args = json.loads(raw_args or "{}")
    except json.JSONDecodeError as e:
        return f"error: arguments are not valid JSON ({e})"
    func, param = TOOL_FUNCS[name]
    if not isinstance(args, dict) or not isinstance(args.get(param), str):
        return f"error: '{name}' needs a string argument '{param}'"
    try:
        return str(func(args[param]))
    except Exception as e:
        return f"error: {e}"


def reflect(sdk, model, goal, answer, evidence):
    """Level 2 · ask the model to CONFIRM or REVISE its own final answer."""
    try:
        resp = sdk.chat.completions.create(
            model=model, temperature=0.0,
            messages=[{"role": "user", "content": (
                f"Task: {goal}\nTool results so far:\n{evidence or '(none)'}\n"
                f"Proposed final answer: {answer}\n\n"
                "Using ONLY the tool results above (do not call any tools), is this answer "
                "correct and complete? Reply with EXACTLY one line:\n"
                "CONFIRM\nor\nREVISE: <one sentence on what is wrong>")}],
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"[reflect] reviewer call failed ({e}); accepting the answer.")
        return "CONFIRM"


def run_agent(goal: str):
    client = LLMClient()
    if client.provider not in ("openai", "groq"):
        print("This advanced demo targets LLM_PROVIDER=openai or groq.")
        return
    sdk = client.client                      # the raw OpenAI/Groq SDK client
    model = client._default_model()
    messages = [{"role": "user", "content": goal}]
    evidence = ""   # tool calls + results, shown to the reviewer

    for step in range(1, 9):
        resp = sdk.chat.completions.create(model=model, messages=messages,
                                           tools=TOOLS, temperature=0.0)
        msg = resp.choices[0].message

        if not getattr(msg, "tool_calls", None):
            verdict = reflect(sdk, model, goal, msg.content, evidence)
            print(f"[reflect] {verdict}")
            if verdict.upper().startswith("REVISE"):
                messages.append({"role": "assistant", "content": msg.content})
                messages.append({"role": "user", "content":
                                 f"A reviewer said: {verdict} Please fix it using the tools."})
                continue
            print("FINAL:", msg.content)
            return msg.content

        messages.append(msg)   # record the assistant's tool request
        for tc in msg.tool_calls:
            print(f"[step {step}] {tc.function.name}({tc.function.arguments})")
            result = run_tool(tc.function.name, tc.function.arguments)
            print(f"        -> {result}")
            evidence += f"{tc.function.name}({tc.function.arguments}) = {result}\n"
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    print("Stopped: step limit.")


if __name__ == "__main__":
    run_agent("What is (23 * 7) + 19? Use the calculator tool, then give the final number.")
    run_agent("What is the total price of 3 widgets and 2 gadgets? Use the tools.")


# ============================ CHALLENGES ============================
# Level 1  · Add a second tool (e.g. price_lookup) with its own schema and let
#            the model choose. (previews Module 2)                    -> DONE: price_lookup
# Level 2  · Add a REFLECT step: after the model's final answer, ask it to CONFIRM
#            or REVISE, and loop on REVISE. (previews Modules 3–4 & 7) -> DONE: reflect()
# Level 3  · Harden it: validate tool arguments, catch bad JSON, and keep the
#            AST-safe calculator — never eval() model output. (previews Module 7)
#                                                                      -> DONE: run_tool()
# Level 4  · Write 8–10 lines on how MCP (Model Context Protocol) would replace
#            these hand-written schemas with a shared tool server your agent
#            connects to. (previews Module 6: Multi-Agent + MCP)
#
# Level 4 write-up — MCP:
#   Right now every tool lives inside this file: I hand-write its JSON schema in
#   TOOLS and hand-wire it to a Python function in TOOL_FUNCS. Any other agent that
#   wants the same calculator has to copy both. With MCP, the tools move into a
#   separate MCP server that publishes them in a standard format. My agent becomes
#   an MCP client: it connects to the server, calls `tools/list` to discover each
#   tool's name, description and input schema, and passes those straight to the
#   model instead of my hand-written TOOLS list. When the model returns a tool call,
#   the agent forwards it to the server with `tools/call` and gets the result back,
#   so the dispatch code shrinks to one generic function. Tools can then be shared
#   by many agents (and apps like Claude Desktop), updated in one place, and swapped
#   without touching the agent, and the server can own the argument validation and
#   safety checks that run_tool() does by hand here.
# ===================================================================
