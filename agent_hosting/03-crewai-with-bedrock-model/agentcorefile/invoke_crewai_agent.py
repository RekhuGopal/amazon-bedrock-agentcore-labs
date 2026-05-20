from boto3.session import Session
from botocore.config import Config
from IPython.display import Markdown, display

import boto3
import json

# ==========================================================
# AWS Session
# ==========================================================
boto_session = Session()
region = boto_session.region_name or "us-east-1"

# ==========================================================
# Botocore Configuration
# ==========================================================
config = Config(
    retries={
        "max_attempts": 10,
        "mode": "adaptive"
    },
    connect_timeout=600,
    read_timeout=3000
)

# ==========================================================
# Agent Runtime ARN
# ==========================================================
# launch_result comes from:
# launch_result = runtime.launch()

agent_arn = "<AGENT_RUNTIME_ARN>"

print("======================================")
print("AGENT RUNTIME ARN")
print("======================================")
print(agent_arn)

# ==========================================================
# Bedrock AgentCore Client
# ==========================================================
agentcore_client = boto3.client(
    service_name="bedrock-agentcore",
    region_name=region,
    config=config
)

# ==========================================================
# Invoke Agent Runtime
# ==========================================================
try:

    boto3_response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        qualifier="DEFAULT",
        payload=json.dumps({
            "prompt": "What is 2 + 2?"
        })
    )

    print("\n======================================")
    print("AGENT INVOCATION SUCCESSFUL")
    print("======================================")

except Exception as invoke_error:

    print("\n❌ Failed to invoke agent runtime")
    print(str(invoke_error))
    raise

# ==========================================================
# Capture Runtime Session ID
# ==========================================================
runtime_session_id = boto3_response.get("runtimeSessionId")

print("\n======================================")
print("RUNTIME SESSION ID")
print("======================================")
print(runtime_session_id)

# ==========================================================
# Process Streaming Response
# ==========================================================
try:

    content_type = boto3_response.get("contentType", "")

    print("\n======================================")
    print("CONTENT TYPE")
    print("======================================")
    print(content_type)

    # ------------------------------------------------------
    # Event Stream Response
    # ------------------------------------------------------
    if "text/event-stream" in content_type:

        print("\n======================================")
        print("STREAMING RESPONSE")
        print("======================================")

        streamed_content = []

        for line in boto3_response["response"].iter_lines(chunk_size=1):

            if line:

                decoded_line = line.decode("utf-8")

                if decoded_line.startswith("data: "):

                    decoded_line = decoded_line[6:]

                    print(decoded_line)

                    streamed_content.append(decoded_line)

        final_output = "\n".join(streamed_content)

        display(Markdown(final_output))

    # ------------------------------------------------------
    # Standard Response
    # ------------------------------------------------------
    else:

        print("\n======================================")
        print("STANDARD RESPONSE")
        print("======================================")

        events = []

        try:

            for event in boto3_response.get("response", []):

                events.append(event)

        except Exception as stream_error:

            events = [f"Error reading response stream: {stream_error}"]

        if events:

            try:

                result = json.loads(events[0].decode("utf-8"))

                if isinstance(result, str):

                    display(Markdown(result))

                else:

                    display(Markdown(f"```json\n{json.dumps(result, indent=2)}\n```"))

            except Exception as parse_error:

                print(f"❌ Failed to parse response: {parse_error}")

        else:

            print("⚠️ No response returned from runtime")

except Exception as response_error:

    print("\n❌ Error processing runtime response")
    print(str(response_error))

# ==========================================================
# Stop Runtime Session
# ==========================================================
# Releases microVM resources for this session
# while keeping runtime alive for future sessions

try:

    if runtime_session_id:

        stop_response = agentcore_client.stop_runtime_session(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=runtime_session_id,
            qualifier="DEFAULT"
        )

        print("\n======================================")
        print("SESSION STOPPED SUCCESSFULLY")
        print("======================================")
        print(f"Runtime Session ID : {runtime_session_id}")
        print(f"Agent Runtime ARN  : {agent_arn}")

        print("\nStop Response:")
        print(json.dumps(stop_response, indent=2, default=str))

    else:

        print("\n⚠️ No runtime session ID available to stop")

except Exception as stop_error:

    print("\n❌ Failed to stop runtime session")
    print(str(stop_error))