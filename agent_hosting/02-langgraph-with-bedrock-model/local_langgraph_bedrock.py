import argparse
import json
import math
import operator
import os

from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_aws import ChatBedrock


# =========================
# TOOLS
# =========================

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        safe_dict = {
            "__builtins__": {},
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow,
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "exp": math.exp,
            "pi": math.pi, "e": math.e,
            "ceil": math.ceil, "floor": math.floor,
            "degrees": math.degrees, "radians": math.radians,
            "add": operator.add, "sub": operator.sub,
            "mul": operator.mul, "truediv": operator.truediv,
        }

        result = eval(expression, safe_dict)
        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def weather() -> str:
    """Get current weather (dummy implementation)."""
    return "It's sunny 🌞"


# =========================
# AGENT
# =========================

def create_agent():
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    llm = ChatBedrock(
        model_id="arn:aws:bedrock:us-east-1:357171621133:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0",
        provider="anthropic",
        region_name="us-east-1",
        model_kwargs={"temperature": 0.1},
    )

    tools = [calculator, weather]
    llm_with_tools = llm.bind_tools(tools)

    system_message = SystemMessage(
        content="You are a helpful assistant. You can do math and provide weather info."
    )

    def chatbot(state: MessagesState):
        messages = state["messages"]

        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [system_message] + messages

        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools))

    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    builder.set_entry_point("chatbot")

    return builder.compile()


agent = create_agent()


# =========================
# EXECUTION
# =========================

def run_agent(prompt: str):
    result = agent.invoke({
        "messages": [HumanMessage(content=prompt)]
    })

    return result["messages"][-1].content


# =========================
# CLI ENTRY
# =========================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # ✅ Named parameter
    parser.add_argument("--prompt", type=str, help="User prompt")

    # Optional fallback for JSON payload
    parser.add_argument("--payload", type=str, help="JSON payload")

    args = parser.parse_args()

    if args.prompt:
        prompt = args.prompt

    elif args.payload:
        try:
            payload = json.loads(args.payload)
            prompt = payload.get("prompt")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in --payload")

    else:
        raise ValueError("Provide either --prompt or --payload")

    response = run_agent(prompt)

    print("\n=== RESPONSE ===")
    print(response)