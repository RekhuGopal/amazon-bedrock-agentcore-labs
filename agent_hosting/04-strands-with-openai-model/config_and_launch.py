from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
import time

# ==========================================
# AWS SESSION
# ==========================================

boto_session = Session()

region = boto_session.region_name or "us-east-1"

print(f"\n[INFO] AWS Region: {region}")

# ==========================================
# AGENTCORE CONFIGURATION
# ==========================================

agentcore_runtime = Runtime()

agent_name = "strands_openai_getting_started"

print("\n[INFO] Configuring AgentCore Runtime...")

response = agentcore_runtime.configure(
    entrypoint="strands_agents_openai.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=region,
    agent_name=agent_name
)

print("\n========== CONFIGURE RESPONSE ==========\n")
print(response)

# ==========================================
# LAUNCH USING LOCAL DOCKER BUILD
# ==========================================

print("\n[INFO] Launching Runtime using LOCAL BUILD...\n")

launch_result = agentcore_runtime.launch(
    local_build=True
)

print("\n========== LAUNCH RESULT ==========\n")

print(f"Agent ID  : {launch_result.agent_id}")
print(f"Agent ARN : {launch_result.agent_arn}")
print(f"ECR URI   : {launch_result.ecr_uri}")

# ==========================================
# WAIT FOR READY STATUS
# ==========================================

end_status = [
    "READY",
    "CREATE_FAILED",
    "DELETE_FAILED",
    "UPDATE_FAILED"
]

status = None

while status not in end_status:

    status_response = agentcore_runtime.status()

    status = status_response.endpoint["status"]

    print(f"Current Status: {status}")

    if status in end_status:
        break

    time.sleep(10)

# ==========================================
# FINAL STATUS
# ==========================================

print("\n========== FINAL STATUS ==========\n")
print(status)

if status == "READY":

    print("\n✅ Runtime deployed successfully")

    print(f"\nAgent Runtime ARN:\n{launch_result.agent_arn}")

else:

    print("\n❌ Deployment failed")