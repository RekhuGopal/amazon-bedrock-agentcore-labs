from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
import time
import sys

# =========================
# CONFIG
# =========================

AGENT_NAME = "langgraph_claude_getting_started"
ENTRYPOINT = "langgraph_bedrock.py"
REQUIREMENTS = "requirements.txt"
TIMEOUT_SECONDS = 900  # 15 mins max wait


# =========================
# SESSION / REGION
# =========================

boto_session = Session()

region = boto_session.region_name or "us-east-1"  # ✅ fallback

print(f"[INFO] Using region: {region}")


# =========================
# INIT RUNTIME
# =========================

agentcore_runtime = Runtime()


# =========================
# CONFIGURE AGENT
# =========================

try:
    print("[INFO] Configuring AgentCore runtime...")

    response = agentcore_runtime.configure(
        entrypoint=ENTRYPOINT,
        auto_create_execution_role=True,
        auto_create_ecr=True,
        requirements_file=REQUIREMENTS,
        region=region,
        agent_name=AGENT_NAME
    )

    print("[SUCCESS] Configuration complete")
    print(response)

except Exception as e:
    print(f"[ERROR] Configuration failed: {e}")
    sys.exit(1)


# =========================
# LAUNCH AGENT
# =========================

try:
    print("[INFO] Launching agent...")

    launch_result = agentcore_runtime.launch()

    print("[SUCCESS] Launch triggered")
    print(launch_result)

except Exception as e:
    print(f"[ERROR] Launch failed: {e}")
    sys.exit(1)


# =========================
# WAIT FOR STATUS
# =========================

print("[INFO] Waiting for agent to become READY...")

start_time = time.time()

end_status = ["READY", "CREATE_FAILED", "DELETE_FAILED", "UPDATE_FAILED"]

while True:
    try:
        status_response = agentcore_runtime.status()
        status = status_response.endpoint["status"]

        print(f"[STATUS] {status}")

        if status in end_status:
            break

        if time.time() - start_time > TIMEOUT_SECONDS:
            print("[ERROR] Timeout waiting for agent readiness")
            sys.exit(1)

        time.sleep(10)

    except Exception as e:
        print(f"[ERROR] Status check failed: {e}")
        sys.exit(1)


# =========================
# FINAL RESULT
# =========================

if status == "READY":
    print("\n✅ Agent is READY")

    # Optional: print endpoint details
    try:
        endpoint = status_response.endpoint
        print("\nEndpoint details:")
        print(endpoint)
    except Exception:
        pass

else:
    print(f"\n❌ Agent deployment failed with status: {status}")
    sys.exit(1)