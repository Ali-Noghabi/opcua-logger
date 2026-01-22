#!/bin/bash

# Certificate generation script with automatic config update

echo "🔐 Generating OPC UA Client Certificate..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Using system Python..."
fi

# Generate certificate and update config
python generate_cert.py --update-config --cn "OPCUAClient" --org "MyCompany" --days 3650

echo "✅ Certificate generation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit config.yaml to set your preferred security policy and mode"
echo "2. Available security policies: None, Basic128Rsa15, Basic256, Basic256Sha256, Aes128Sha256RsaOaep, Aes256Sha256RsaPss"
echo "3. Available security modes: None, Sign, SignAndEncrypt"
echo "4. Run the logger: ./run_logger.sh"