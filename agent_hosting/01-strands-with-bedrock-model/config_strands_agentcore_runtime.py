from bedrock_agentcore_starter_toolkit import Runtime
import time
import sys

# -------------------------------
# CONFIG
# -------------------------------
REGION = "us-east-1"
AGENT_NAME = "strands_claude_east_demo"

print(f"Using region: {REGION}")

# IMPORTANT: Runtime takes no args
runtime = Runtime()

# -------------------------------
# CONFIGURE
# -------------------------------
print("\nConfiguring AgentCore runtime...")

response = runtime.configure(
    entrypoint="strands_agents.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=REGION,
    agent_name=AGENT_NAME
)

print("Configuration response:", response)

# -------------------------------
# LAUNCH
# -------------------------------
print("\nLaunching agent...")
launch_result = runtime.launch()

print("Launch response:", launch_result)

# -------------------------------
# WAIT FOR READY
# -------------------------------
print("\nWaiting for agent to be READY...\n")

END_STATES = ['READY', 'CREATE_FAILED', 'DELETE_FAILED', 'UPDATE_FAILED']

while True:
    status_response = runtime.status()
    status = status_response.endpoint['status']

    print("Status:", status)

    if status in END_STATES:
        break

    time.sleep(10)

# -------------------------------
# FINAL STATUS
# -------------------------------
if status == "READY":
    print("\n✅ Agent READY")
    print("Endpoint:", status_response.endpoint.get("endpointUrl"))
    print("Agent ARN:", launch_result.agent_arn)
else:
    print("\n❌ Deployment failed:", status)
    sys.exit(1)