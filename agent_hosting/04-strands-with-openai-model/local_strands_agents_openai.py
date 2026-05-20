from strands import Agent, tool
from strands_tools import calculator
from strands.models.litellm import LiteLLMModel

import argparse
import os

# =========================================================
# AZURE OPENAI CONFIG
# =========================================================

os.environ["AZURE_API_BASE"] = "https://test-ai-foundry-gpt-demo.openai.azure.com/"

os.environ["AZURE_API_KEY"] = "<>"

os.environ["AZURE_API_VERSION"] = "2024-10-21"

# =========================================================
# TOOL
# =========================================================

@tool
def weather():
    """Get weather"""
    return "The weather is sunny"

# =========================================================
# IMPORTANT
# =========================================================

# THIS MUST MATCH YOUR DEPLOYMENT NAME EXACTLY

deployment_name = "gpt-5.4"

model = f"azure/{deployment_name}"

# =========================================================
# MODEL
# =========================================================

litellm_model = LiteLLMModel(
    model_id=model,
    params={
        "temperature": 0.7,
        "max_tokens": 4000
    }
)

# =========================================================
# AGENT
# =========================================================

agent = Agent(
    model=litellm_model,
    tools=[
        calculator,
        weather
    ],
    system_prompt="You're a helpful assistant."
)

# =========================================================
# INVOKE
# =========================================================

def invoke_agent(prompt: str):

    response = agent(prompt)

    try:
        return response.message["content"][0]["text"]

    except Exception:
        return str(response)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prompt",
        type=str,
        required=True
    )

    args = parser.parse_args()

    result = invoke_agent(args.prompt)

    print("\n======================")
    print("AGENT RESPONSE")
    print("======================\n")

    print(result)