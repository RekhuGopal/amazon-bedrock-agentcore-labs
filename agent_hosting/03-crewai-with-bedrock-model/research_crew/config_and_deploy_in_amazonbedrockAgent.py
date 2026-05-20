from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
import time
import logging

# ---------------------------------------
# Logging Configuration
# ---------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------------------------------
# AWS Session
# ---------------------------------------
boto_session = Session()
region = boto_session.region_name or "us-east-1"

# ---------------------------------------
# Agent Configuration
# ---------------------------------------
AGENT_NAME = "research_crew_getting_started"
ENTRYPOINT = "research_crew/research_crew.py"

# ---------------------------------------
# Initialize Runtime
# ---------------------------------------
agentcore_runtime = Runtime()

try:
    logging.info("Configuring Bedrock AgentCore Runtime...")

    configure_response = agentcore_runtime.configure(
        entrypoint=ENTRYPOINT,
        auto_create_execution_role=True,
        auto_create_ecr=True,
        region=region,
        agent_name=AGENT_NAME
    )

    logging.info("Configuration completed successfully")
    print(configure_response)

except Exception as configure_error:
    logging.error(f"Configuration failed: {str(configure_error)}")
    raise


# ---------------------------------------
# Launch Runtime
# ---------------------------------------
try:
    logging.info("Launching AgentCore Runtime...")

    launch_result = agentcore_runtime.launch()

    logging.info("Launch initiated successfully")
    print(launch_result)

except Exception as launch_error:
    logging.error(f"Launch failed: {str(launch_error)}")
    raise


# ---------------------------------------
# Wait for Deployment Completion
# ---------------------------------------
FINAL_STATES = {
    "READY",
    "CREATE_FAILED",
    "DELETE_FAILED",
    "UPDATE_FAILED"
}

POLL_INTERVAL = 10  # seconds
MAX_WAIT_TIME = 1800  # 30 minutes

elapsed_time = 0

logging.info("Waiting for runtime deployment completion...")

while True:

    try:
        status_response = agentcore_runtime.status()
        current_status = status_response.endpoint["status"]

        logging.info(f"Current Status: {current_status}")

        if current_status in FINAL_STATES:
            break

        if elapsed_time >= MAX_WAIT_TIME:
            raise TimeoutError(
                f"Deployment timed out after {MAX_WAIT_TIME} seconds"
            )

        time.sleep(POLL_INTERVAL)
        elapsed_time += POLL_INTERVAL

    except Exception as status_error:
        logging.error(f"Status check failed: {str(status_error)}")
        raise


# ---------------------------------------
# Final Result
# ---------------------------------------
if current_status == "READY":
    logging.info("AgentCore Runtime deployed successfully")
else:
    logging.error(f"Deployment finished with failure state: {current_status}")

print("\n==============================")
print(f"FINAL STATUS : {current_status}")
print("==============================")