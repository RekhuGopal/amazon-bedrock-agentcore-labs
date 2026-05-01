from strands import Agent, tool
from strands_tools import calculator
import argparse
from strands.models import BedrockModel


# -------------------------------
# TOOL: Weather
# -------------------------------
@tool
def weather(city: str):
    """Get weather information."""
    print("Weather tool called with:", city)

    if city.lower() == "athens":
        return "The weather in Athens is very sunny."
    
    return f"The weather in {city} is sunny."


# -------------------------------
# MODEL (Inference Profile REQUIRED)
# -------------------------------
model = BedrockModel(
    model_id="arn:aws:bedrock:us-east-1:357171621133:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-east-1"
)

# -------------------------------
# AGENT (TRUE TOOL-CALLING AGENT)
# -------------------------------
agent = Agent(
    model=model,
    tools=[calculator, weather],
    system_prompt="""
You are a helpful AI assistant.

- You can perform math using the calculator tool
- You can fetch weather using the weather tool
- Always choose tools when appropriate
- Extract arguments correctly
"""
)


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def run_agent(prompt: str):
    print("\nUser:", prompt)

    response = agent(prompt)

    try:
        output = response.message['content'][0]['text']
    except Exception:
        output = str(response)

    print("Agent:", output)


# -------------------------------
# ENTRY POINT (CLI)
# -------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True)
    args = parser.parse_args()

    run_agent(args.prompt)