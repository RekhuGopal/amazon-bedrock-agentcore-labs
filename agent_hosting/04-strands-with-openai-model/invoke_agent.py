import boto3
import json
from botocore.config import Config

# ==========================================
# CONFIGURATION
# ==========================================

region = "us-east-1"

agent_arn = "YOUR_AGENT_RUNTIME_ARN"

# Long-running runtime config
config = Config(
    retries={
        "max_attempts": 10,
        "mode": "adaptive"
    },
    connect_timeout=600,
    read_timeout=3000
)

# ==========================================
# CREATE AGENTCORE CLIENT
# ==========================================

agentcore_client = boto3.client(
    "bedrock-agentcore",
    region_name=region,
    config=config
)

# ==========================================
# INVOKE AGENT RUNTIME
# ==========================================

payload = {
    "prompt": "What is 2+2?"
}

runtime_session_id = None

try:
    boto3_response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        qualifier="DEFAULT",
        payload=json.dumps(payload)
    )

    # Capture runtime session ID
    runtime_session_id = boto3_response.get("runtimeSessionId")

    print(f"\n[INFO] Runtime Session ID: {runtime_session_id}")

    content_type = boto3_response.get("contentType", "")

    # ==========================================
    # STREAMING RESPONSE
    # ==========================================

    if "event-stream" in content_type or "text/event-stream" in content_type:

        print("\n========== STREAM RESPONSE ==========\n")

        stream = boto3_response.get("response")

        full_response = []

        for event in stream:
            try:
                if "chunk" in event:

                    chunk_data = (
                        event["chunk"]["bytes"]
                        .decode("utf-8")
                    )

                    print(chunk_data, end="")
                    full_response.append(chunk_data)

            except Exception as stream_error:
                print(f"\n[STREAM ERROR] {stream_error}")

        final_output = "".join(full_response)

        print("\n\n========== FINAL RESPONSE ==========\n")
        print(final_output)

    # ==========================================
    # NON-STREAM RESPONSE
    # ==========================================

    else:

        print("\n========== STANDARD RESPONSE ==========\n")

        response_body = boto3_response.get("response")

        raw_response = response_body.read().decode("utf-8")

        try:
            parsed_response = json.loads(raw_response)
            print(json.dumps(parsed_response, indent=2))

        except Exception:
            print(raw_response)

except Exception as e:
    print(f"\n[ERROR] Invocation failed:\n{e}")

# ==========================================
# STOP RUNTIME SESSION
# ==========================================

try:

    if runtime_session_id:

        agentcore_client.stop_runtime_session(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=runtime_session_id,
            qualifier="DEFAULT"
        )

        print(
            f"\n✅ Session '{runtime_session_id}' stopped successfully"
        )

    else:
        print("\n⚠️ No runtime session ID found")

except Exception as e:
    print(f"\n[ERROR] Failed to stop session:\n{e}")