import asyncio
import boto3
import json
import sys
import base64
import time
import uuid
import httpx
from boto3.session import Session
from datetime import timedelta

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

def get_refresh_token(client_id, refresh_token, region):
    """Refresh access token using refresh token"""
    cognito_client = boto3.client('cognito-idp', region_name=region)
    auth_response = cognito_client.initiate_auth(
        ClientId=client_id,
        AuthFlow='REFRESH_TOKEN_AUTH',
        AuthParameters={'REFRESH_TOKEN': refresh_token}
    )
    return auth_response['AuthenticationResult']['AccessToken']

def get_valid_token(bearer_token, client_id, refresh_token, region):
    """Check token expiry and refresh if needed"""
    try:
        payload = bearer_token.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded = json.loads(base64.b64decode(payload))
        
        current_time = int(time.time())
        if decoded['exp'] - current_time < 300:
            print("🔄 Token expiring soon, refreshing...")
            new_token = get_refresh_token(client_id, refresh_token, region)
            print("✓ Token refreshed successfully")
            return new_token
        
        return bearer_token
    except:
        print("�� Invalid token, refreshing...")
        return get_refresh_token(client_id, refresh_token, region)

def stop_runtime_session_oauth(agent_arn, session_id, bearer_token, region):
    """Stop runtime session using OAuth bearer token via HTTP POST"""
    # Encode the ARN for URL path
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/stopruntimesession"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "runtimeSessionId": session_id,
        "agentRuntimeArn": agent_arn,
        "qualifier": "DEFAULT"
    }
    
    response = httpx.post(url, headers=headers, json=body, timeout=30.0)
    return response

async def main():
    boto_session = Session()
    region = boto_session.region_name
    
    print(f"Using AWS region: {region}")
    
    try:
        ssm_client = boto3.client('ssm', region_name=region)
        agent_arn_response = ssm_client.get_parameter(Name='/mcp_server/runtime/agent_arn')
        agent_arn = agent_arn_response['Parameter']['Value']
        print(f"Retrieved Agent ARN: {agent_arn}")

        secrets_client = boto3.client('secretsmanager', region_name=region)
        response = secrets_client.get_secret_value(SecretId='mcp_server/cognito/credentials')
        secret_value = response['SecretString']
        parsed_secret = json.loads(secret_value)
        bearer_token = parsed_secret['bearer_token']
        refresh_token = parsed_secret['refresh_token']
        client_id = parsed_secret['client_id']
        print("✓ Retrieved credentials from Secrets Manager")
        
        bearer_token = get_valid_token(bearer_token, client_id, refresh_token, region)
        
    except Exception as e:
        print(f"Error retrieving credentials: {e}")
        sys.exit(1)
    
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    # Generate custom session ID
    mcp_session_id = str(uuid.uuid4())
    print(f"\n📝 Generated custom mcpSessionId: {mcp_session_id}")
    
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Mcp-Session-Id": mcp_session_id
    }
    
    print(f"\nConnecting to: {mcp_url}")

    try:
        async with streamablehttp_client(mcp_url, headers, timeout=timedelta(seconds=120), terminate_on_close=False) as (
            read_stream, write_stream, _
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("✓ MCP session initialized")
                
                tool_result = await session.list_tools()
                print(f"\n📋 Found {len(tool_result.tools)} tools")
                
                # Test tools
                print("\n🧪 Testing tools...")
                add_result = await session.call_tool(name="add_numbers", arguments={"a": 5, "b": 3})
                print(f"   add_numbers(5, 3) = {add_result.content[0].text}")
                
                multiply_result = await session.call_tool(name="multiply_numbers", arguments={"a": 4, "b": 7})
                print(f"   multiply_numbers(4, 7) = {multiply_result.content[0].text}")
                
                greet_result = await session.call_tool(name="greet_user", arguments={"name": "CloudQuickLabs"})
                print(f"   greet_user('CloudQuickLabs') = {greet_result.content[0].text}")
                
                print("\n✅ MCP tool testing completed!")
        
        # Stop the session using OAuth bearer token
        print(f"\n🛑 Stopping session '{mcp_session_id}' (OAuth)...")
        response = stop_runtime_session_oauth(agent_arn, mcp_session_id, bearer_token, region)
        
        if response.status_code == 200:
            print(f"✅ Session stopped — microVM resources released")
            print(f"💡 Runtime remains alive for new sessions")
        else:
            print(f"⚠️  Status {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())