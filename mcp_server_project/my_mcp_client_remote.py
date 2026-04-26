import asyncio
import boto3
import json
import sys
import base64
import time
from boto3.session import Session
from datetime import timedelta
import traceback

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
    except Exception as e:
        print("🔄 Invalid token, refreshing...", e)
        traceback.print_exc()
        return get_refresh_token(client_id, refresh_token, region)

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
        
        # Validate and refresh token if needed
        bearer_token = get_valid_token(bearer_token, client_id, refresh_token, region)
        
    except Exception as e:
        print(f"Error retrieving credentials: {e}")
        sys.exit(1)
    
    if not agent_arn or not bearer_token:
        print("Error: AGENT_ARN or BEARER_TOKEN not retrieved properly")
        sys.exit(1)
    
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    headers = {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nConnecting to: {mcp_url}")
    print("Headers configured ✓")

    try:
        async with streamablehttp_client(mcp_url, headers, timeout=timedelta(seconds=120), terminate_on_close=False) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                print("\n🔄 Initializing MCP session...")
                await session.initialize()
                print("✓ MCP session initialized")
                
                print("\n🔄 Listing available tools...")
                tool_result = await session.list_tools()
                
                print("\n📋 Available MCP Tools:")
                print("=" * 50)
                for tool in tool_result.tools:
                    print(f"🔧 {tool.name}")
                    print(f"   Description: {tool.description}")
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        properties = tool.inputSchema.get('properties', {})
                        if properties:
                            print(f"   Parameters: {list(properties.keys())}")
                    print()
                
                print(f"✅ Successfully connected to MCP server!")
                print(f"Found {len(tool_result.tools)} tools available.")
                
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())