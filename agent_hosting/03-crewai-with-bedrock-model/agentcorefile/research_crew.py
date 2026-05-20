import os
from research_crew.crew import ResearchCrew

# ---------- Agentcore imports --------------------
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
#------------------------------------------------


@app.entrypoint
def agent_invocation(payload, context):
    """Handler for agent invocation"""
    print(f'Payload: {payload}')
    try: 
        # Extract user message from payload with default
        user_message = payload.get("prompt", "Artificial Intelligence in Healthcare")
        print(f"Processing topic: {user_message}")
        
        # Create crew instance and run synchronously
        research_crew_instance = ResearchCrew()
        crew = research_crew_instance.crew()
        
        # Use synchronous kickoff instead of async - this avoids all event loop issues
        result = crew.kickoff(inputs={'topic': user_message})

        print("Context:\n-------\n", context)
        print("Result Raw:\n*******\n", result.raw)
        
        # Safely access json_dict if it exists
        if hasattr(result, 'json_dict'):
            print("Result JSON:\n*******\n", result.json_dict)
        
        return {"result": result.raw}
        
    except Exception as e:
        print(f'Exception occurred: {e}')
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    app.run()