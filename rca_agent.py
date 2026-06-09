from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from tools import registry  # Import the dynamic registry from your tools.py

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
    tool_kwargs: Dict[str, Any]  # NEW: Added to hold dynamic tool arguments
    is_valid: bool
    fix: str
    attempts: int

# -----------------------
# NODES
# -----------------------

def analyze_logs(state: RCAState):
    response = llm.invoke([
        HumanMessage(content=f"Analyze this error:\n{state['error']}")
    ])
    return {**state, "analysis": response.content}


def generate_hypothesis(state: RCAState):
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


# 🔥 Dynamic Tool Selection using LangChain Tool Calling
def choose_tool(state: RCAState):
    # 1. Bind the dynamic schema from your tools.py to the LLM
    llm_with_tools = llm.bind_tools(registry.get_agent_schema())
    
    # 2. Ask the LLM to verify the hypothesis using the tools
    response = llm_with_tools.invoke([
        HumanMessage(content=f"""
        Based on this hypothesis:
        {state['hypothesis']}

        Which tool should be used to verify it? Execute the most appropriate tool with the correct arguments.
        """)
    ])

    # 3. Extract the structured tool call
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        return {
            **state, 
            "selected_tool": tool_call["name"],
            "tool_kwargs": tool_call["args"] # Extracts arguments like {"host": "localhost", "port": 9092}
        }
    
    # Fallback if the LLM decides no tools are needed
    return {**state, "selected_tool": "none", "tool_kwargs": {}}


# 🔧 Dynamic Validation
def validate(state: RCAState):
    tool_name = state.get("selected_tool")
    tool_kwargs = state.get("tool_kwargs", {})

    if tool_name and tool_name != "none":
        try:
            # Execute the tool dynamically with the arguments provided by the LLM
            result = registry.execute(tool_name, **tool_kwargs)
            
            # Assuming True means healthy, and False means broken. 
            # If the tool returns False, the error hypothesis is VALIDATED.
            return {**state, "is_valid": not result}
        except Exception as e:
            print(f"Tool execution failed: {e}")
            return {**state, "is_valid": False}

    return {**state, "is_valid": False}


def suggest_fix(state: RCAState):
    response = llm.invoke([
        HumanMessage(content=f"""
        Error: {state['error']}
        Root cause verified: {state['hypothesis']}
        Failing component tool check: {state['selected_tool']} with args {state['tool_kwargs']}
        
        Suggest a practical fix.
        """)
    ])
    return {**state, "fix": response.content}


# -----------------------
# DECISION & GRAPH SETUP
# -----------------------

def decide(state: RCAState):
    if state["is_valid"] or state["attempts"] >= 3:
        return "fix"
    return "retry"

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

# Compile and export
graph = builder.compile()

def run_rca(error_message: str) -> dict:
    """Execute the RCA graph workflow on an error message."""
    initial_state = {
        "error": error_message,
        "analysis": "",
        "hypothesis": "",
        "selected_tool": "",
        "is_valid": False,
        "fix": "",
        "attempts": 0
    }
    result = graph.invoke(initial_state)
    return result

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
        "tool_kwargs": {},
        "is_valid": False,
        "fix": "",
        "attempts": 0
    })