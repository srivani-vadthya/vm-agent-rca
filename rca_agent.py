from langgraph.graph import StateGraph, END
from typing import TypedDict
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from tools import TOOLS  # dynamic tool registry

load_dotenv()

# -----------------------
# LLM SETUP
# -----------------------
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name=os.getenv("MODEL_NAME")
)

# -----------------------
# STATE
# -----------------------
class RCAState(TypedDict):
    error: str
    analysis: str
    hypothesis: str
    selected_tool: str
    is_valid: bool
    fix: str
    attempts: int

# -----------------------
# NODES
# -----------------------

def analyze_logs(state):
    response = llm.invoke([
        HumanMessage(content=f"Analyze this error:\n{state['error']}")
    ])
    return {**state, "analysis": response.content}


def generate_hypothesis(state):
    response = llm.invoke([
        HumanMessage(content=f"""
        Based on this analysis:
        {state['analysis']}
        
        Suggest ONE root cause hypothesis.
        """)
    ])
    return {
        **state,
        "hypothesis": response.content,
        "attempts": state["attempts"] + 1
    }


# 🔥 Dynamic tool selection using LLM
def choose_tool(state):
    response = llm.invoke([
        HumanMessage(content=f"""
        Based on this hypothesis:
        {state['hypothesis']}

        Which tool should be used to verify it?

        Available tools: kafka, api, file

        Answer ONLY one word.
        """)
    ])

    tool = response.content.lower().strip()

    # Normalize output (important)
    if "kafka" in tool:
        tool = "kafka"
    elif "api" in tool:
        tool = "api"
    elif "file" in tool or "csv" in tool:
        tool = "file"
    else:
        tool = "unknown"

    return {**state, "selected_tool": tool}


# 🔧 Dynamic validation
def validate(state):
    tool_name = state.get("selected_tool", "")
    tool_func = TOOLS.get(tool_name)

    if tool_func:
        result = tool_func()
        return {**state, "is_valid": not result}

    return {**state, "is_valid": False}


def suggest_fix(state):
    response = llm.invoke([
        HumanMessage(content=f"""
        Error: {state['error']}
        Root cause: {state['hypothesis']}
        
        Suggest a practical fix.
        """)
    ])
    return {**state, "fix": response.content}


# -----------------------
# DECISION
# -----------------------

def decide(state):
    if state["is_valid"] or state["attempts"] >= 3:
        return "fix"
    return "retry"


# -----------------------
# GRAPH
# -----------------------

builder = StateGraph(RCAState)

builder.add_node("analyze", analyze_logs)
builder.add_node("hypothesis", generate_hypothesis)
builder.add_node("choose_tool", choose_tool)
builder.add_node("validate", validate)
builder.add_node("fix", suggest_fix)

builder.set_entry_point("analyze")

builder.add_edge("analyze", "hypothesis")
builder.add_edge("hypothesis", "choose_tool")
builder.add_edge("choose_tool", "validate")

builder.add_conditional_edges(
    "validate",
    decide,
    {
        "retry": "hypothesis",
        "fix": "fix"
    }
)

builder.add_edge("fix", END)

graph = builder.compile()

# -----------------------
# RUN FUNCTION
# -----------------------

def run_rca(error_text):
    return graph.invoke({
        "error": error_text,
        "analysis": "",
        "hypothesis": "",
        "selected_tool": "",
        "is_valid": False,
        "fix": "",
        "attempts": 0
    })