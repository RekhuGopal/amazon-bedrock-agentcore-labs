# amazon-bedrock-agentcore-labs
# Helpful command for labs
aws bedrock list-foundation-models `
  --region us-west-2 `
  --query 'modelSummaries[?modelLifecycle.status==''ACTIVE''].modelId' `
  --output text

# List all inference profiles
aws bedrock list-inference-profiles `
  --region us-west-2 `
  --query "inferenceProfileSummaries[].inferenceProfileArn" `
  --output text

# -------------------------------
# MODEL (Inference Profile REQUIRED)
# -------------------------------
model = BedrockModel(
    model_id="arn:aws:bedrock:us-east-1:357171621133:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
)