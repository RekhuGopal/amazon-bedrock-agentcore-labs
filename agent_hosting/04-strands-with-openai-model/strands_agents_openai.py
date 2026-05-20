from strands import Agent, tool
from strands_tools import calculator
from strands.models.litellm import LiteLLMModel

from bedrock_agentcore.runtime import BedrockAgentCoreApp

import os

# =========================================================
# BEDROCK AGENTCORE APP
# =========================================================

app = BedrockAgentCoreApp()

# =========================================================
# AZURE OPENAI / AI FOUNDRY CONFIG
# =========================================================

# IMPORTANT:
# Use Azure OpenAI endpoint
# Example:
# https://my-openai-resource.openai.azure.com/

os.environ["AZURE_API_BASE"] = "https://test-ai-foundry-gpt-demo.openai.azure.com/"

os.environ["AZURE_API_KEY"] = "<>"

os.environ["AZURE_API_VERSION"] = "2024-10-21"

# =========================================================
# CUSTOM TOOL
# =========================================================

@tool
def weather():
    """
    Get weather information
    """
    return "The weather is sunny"

# =========================================================
# MODEL CONFIGURATION
# =========================================================

# MUST match Azure deployment name exactly

deployment_name = "gpt-5.4"

model = f"azure/{deployment_name}"

litellm_model = LiteLLMModel(
    model_id=model,
    params={
        "max_tokens": 4000,
        "temperature": 0.7
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
    system_prompt="""
    You're a helpful AI assistant.

    You can:
    - perform calculations
    - answer questions
    - provide weather information
    """
)

# =========================================================
# AGENTCORE ENTRYPOINT
# =========================================================

@app.entrypoint
def strands_agent_openai(payload, context):

    try:

        print(f"Payload received: {payload}")

        user_input = payload.get(
            "prompt",
            "Hello"
        )

        response = agent(user_input)

        try:
            output_text = response.message["content"][0]["text"]

        except Exception:
            output_text = str(response)

        return {
            "result": output_text
        }

    except Exception as e:

        print(f"ERROR: {str(e)}")

        return {
            "error": str(e)
        }

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("Starting Bedrock AgentCore Runtime...")

    app.run()