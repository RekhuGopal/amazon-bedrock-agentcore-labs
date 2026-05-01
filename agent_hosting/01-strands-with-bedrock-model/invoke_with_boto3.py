import boto3
import json

REGION = "us-east-1"
AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:357171621133:runtime/strands_claude_east_demo-3ZhaUTD7Oy"

client = boto3.client(
    "bedrock-agentcore",
    region_name=REGION
)

payload = {
    "prompt": "What is the weather in Athens?"
}

response = client.invoke_agent_runtime(
    agentRuntimeArn=AGENT_ARN,
    qualifier="DEFAULT",
    payload=json.dumps(payload)
)

print("\n=== Invocation started ===")

runtime_session_id = response.get("runtimeSessionId")
print("Session ID:", runtime_session_id)


# -------------------------------
# HANDLE STREAMING RESPONSE
# -------------------------------
if "text/event-stream" in response.get("contentType", ""):
    print("\nStreaming response:\n")

    full_output = ""

    for line in response["response"].iter_lines():
        if line:
            decoded = line.decode("utf-8")

            if decoded.startswith("data: "):
                data = decoded[6:]
                print(data)
                full_output += data + "\n"

    print("\nFinal Output:\n", full_output)


# -------------------------------
# HANDLE NON-STREAM RESPONSE
# -------------------------------
else:
    print("\nStandard response:\n")

    try:
        events = []
        for event in response.get("response", []):
            events.append(event.decode("utf-8"))

        final_output = json.loads(events[0])
        print(final_output)

    except Exception as e:
        print("Error parsing response:", str(e))


# -------------------------------
# STOP SESSION (IMPORTANT)
# -------------------------------
if runtime_session_id:
    client.stop_runtime_session(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=runtime_session_id,
        qualifier="DEFAULT"
    )
    print(f"\n✅ Session stopped: {runtime_session_id}")