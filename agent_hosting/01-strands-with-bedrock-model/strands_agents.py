from strands import Agent, tool
from strands_tools import calculator
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel

app = BedrockAgentCoreApp()


# -------------------------------
# TOOL
# -------------------------------
@tool
def weather(city: str):
    print("Weather tool called with:", city)

    if city.lower() == "athens":
        return "The weather in Athens is very sunny."
    
    return f"The weather in {city} is sunny."


# -------------------------------
# MODEL (us-east-1 FIX)
# -------------------------------
model = BedrockModel(
    model_id="arn:aws:bedrock:us-east-1:357171621133:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-east-1"
)


# -------------------------------
# AGENT
# -------------------------------
agent = Agent(
    model=model,
    tools=[calculator, weather],
    system_prompt="""
You are a helpful assistant.

- Use calculator for math
- Use weather tool for weather queries
- Extract city names correctly
- Do not ask again if city is present
"""
)


# -------------------------------
# ENTRYPOINT
# -------------------------------
@app.entrypoint
def strands_agent_bedrock(payload):
    user_input = payload.get("prompt")
    print("User input:", user_input)

    response = agent(user_input)

    try:
        return response.message['content'][0]['text']
    except Exception:
        return str(response)


if __name__ == "__main__":
    app.run()