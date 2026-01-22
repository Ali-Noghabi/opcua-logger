#!/bin/bash

# Test runner that starts server and then tests logger

echo "🧪 Starting OPC UA Logger Test..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Using system Python..."
fi

# Start test server in background
echo "🚀 Starting test server..."
python test_server.py &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Update config to use localhost test server
echo "📝 Updating config for test server..."
cat > test_config.yaml << EOF
# OPC UA Server Configuration (Test Server)
server:
  url: "opc.tcp://localhost:4840/freeopcua/server/"
  security_policy: "None"
  message_security_mode: "None"
  username: null
  password: null
  certificate_path: null
  private_key_path: null

# Tags to subscribe to (Test Server Tags)
tags:
  - node_id: "ns=3;s=Demo.Dynamic.Scalar.Double"
    name: "Dynamic_Scalar_Double"
  - node_id: "ns=3;s=Demo.Dynamic.Scalar.Boolean"
    name: "Dynamic_Scalar_Boolean"
  - node_id: "ns=3;s=Demo.Static.Scalar.Boolean"
    name: "Static_Scalar_Boolean"

# CSV logging configuration
logging:
  csv_file: "test_opcua_data.csv"
  timestamp_format: "%Y-%m-%d %H:%M:%S.%f"
EOF

# Test the logger with test config
echo "🔍 Testing OPC UA logger..."
timeout 10s python -c "
import asyncio
import sys
sys.path.append('.')
from opcua_logger import OPCUALogger

async def test():
    logger = OPCUALogger('test_config.yaml')
    try:
        await logger.connect()
        print('✅ Connected successfully!')
        
        # Wait for some data
        await asyncio.sleep(8)
        
        # Show current data
        data = logger.get_current_data()
        print('📊 Current data:', data)
        
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        await logger.disconnect()

asyncio.run(test())
"

# Check if test data was created
if [ -f "test_opcua_data.csv" ]; then
    echo "✅ Test successful! Data written to test_opcua_data.csv"
    echo "📄 Sample data:"
    head -10 test_opcua_data.csv
else
    echo "❌ Test failed - no data file created"
fi

# Clean up
echo "🧹 Cleaning up..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null
rm -f test_config.yaml test_opcua_data.csv

echo "🏁 Test complete!"