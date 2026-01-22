#!/usr/bin/env python3
"""
Simple OPC UA Test Server for testing the logger
"""

import asyncio
import logging
from datetime import datetime
from asyncua import Server, ua

async def create_test_server():
    """Create a simple OPC UA test server with demo tags"""
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("OPC UA Test Server")
    
    # Setup our own namespace
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)
    
    # Add objects
    objects = server.get_objects_node()
    
    # Add demo objects with correct node IDs
    demo_obj = await objects.add_object(idx, "Demo")
    
    # Add dynamic variables with string node IDs
    temp_var = await demo_obj.add_variable(idx, "Dynamic.Scalar.Double", 0.0)
    pressure_var = await demo_obj.add_variable(idx, "Dynamic.Scalar.Boolean", False)
    flow_var = await demo_obj.add_variable(idx, "Static.Scalar.Boolean", True)
    
    # Make variables writable
    await temp_var.set_writable()
    await pressure_var.set_writable()
    await flow_var.set_writable()
    
    # Start server
    async with server:
        print(f"🚀 OPC UA Test Server started at opc.tcp://0.0.0.0:4840/freeopcua/server/")
        print("📋 Available Tags:")
        print(f"   ns=3;s=Demo.Dynamic.Scalar.Double (ID: {temp_var.nodeid})")
        print(f"   ns=3;s=Demo.Dynamic.Scalar.Boolean (ID: {pressure_var.nodeid})")
        print(f"   ns=3;s=Demo.Static.Scalar.Boolean (ID: {flow_var.nodeid})")
        print("⏰ Updating values every 2 seconds...")
        
        counter = 0
        while True:
            # Update dynamic values
            temp_value = 20.0 + (counter % 10) + 0.5
            pressure_value = bool(counter % 2)
            
            await temp_var.write_value(temp_value)
            await pressure_var.write_value(pressure_value)
            
            print(f"📊 Update {counter}: Temp={temp_value:.1f}, Pressure={pressure_value}")
            
            counter += 1
            await asyncio.sleep(2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(create_test_server())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")