# --- Cleanup Resources ---
import boto3

region = boto3.Session().region_name
ssm_client = boto3.client('ssm', region_name=region)
secrets_client = boto3.client('secretsmanager', region_name=region)


agentcore_control_client = boto3.client('bedrock-agentcore-control', region_name=region)
ecr_client = boto3.client('ecr', region_name=region)

# Step 1: Delete Secrets Manager secret first to minimize credential exposure window
try:
    secrets_client.delete_secret(
        SecretId='mcp_server/cognito/credentials',
        ForceDeleteWithoutRecovery=True
    )
    print("✅ Secrets Manager secret deleted")
except secrets_client.exceptions.ResourceNotFoundException:
    print("ℹ️  Secrets Manager secret not found")

# Step 2: Delete Parameter Store parameter
try:
    ssm_client.delete_parameter(Name='/mcp_server/runtime/agent_arn')
    print("✅ Parameter Store parameter deleted")
except ssm_client.exceptions.ParameterNotFound:
    print("ℹ️  Parameter Store parameter not found")

# Step 3: Delete the agent runtime to stop incurring costs
# AgentCore Runtime costs are based on vCPU and Memory
try:
    agentcore_control_client.delete_agent_runtime(
        agentRuntimeId=launch_result.agent_id,
    )
    print(f"✅ Agent runtime '{launch_result.agent_id}' deleted")
except Exception as e:
    print(f"⚠️ Failed to delete agent runtime: {e}")

# Step 4: Delete the ECR repository
try:
    ecr_client.delete_repository(
        repositoryName=launch_result.ecr_uri.split('/')[1],
        force=True
    )
    print(f"✅ ECR repository '{launch_result.ecr_uri.split('/')[1]}' deleted")
except Exception as e:
    print(f"⚠️ Failed to delete ECR repository: {e}")

print("\n✅ Cleanup completed successfully!")