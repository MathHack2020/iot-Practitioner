# Convert private.pem to base64
base64 iOTest_PrivateKey.pem > PrivateKey.pem.b64

# Convert certificate.pem to base64
base64 iOTest_Cert.pem > Cert.pem.b64

# Convert rootCA.pem to base64
base64 AmazonRootCA.pem > AmazonRootCA.pem.b64

# Create or update the AWS Secrets Manager secret
secret_name="iot/certs/prod"
region="us-east-1"

privateKey=$(cat PrivateKey.pem.b64 | jq -R .)
cert=$(cat Cert.pem.b64 | jq -R .)
rootCA=$(cat AmazonRootCA.pem.b64 | jq -R .)

secret_string=$(jq -n --arg pk "$privateKey" --arg cert "$cert" --arg ca "$rootCA" '{PrivateKey: $pk, Cert: $cert, AmazonRootCA: $ca}')

if aws secretsmanager describe-secret --secret-id "$secret_name" --region "$region" > /dev/null 2>&1; then
    # Secret exists, update it
    aws secretsmanager update-secret \
        --secret-id "$secret_name" \
        --secret-string "$secret_string" \
        --region "$region"
    echo "Secret '$secret_name' updated."
else
    # Secret does not exist, create it
    aws secretsmanager create-secret \
        --name "$secret_name" \
        --secret-string "$secret_string" \
        --region "$region"
    echo "Secret '$secret_name' created."
fi

# Clean up temporary files (optional but recommended)
rm PrivateKey.pem.b64 Cert.pem.b64 AmazonRootCA.pem.b64