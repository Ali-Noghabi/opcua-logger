import asyncio
import json
import logging
import yaml
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from asyncua import Client, ua
import os
import base64

class OPCUALogger:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.client: Optional[Client] = None
        self.subscriptions: Dict[str, Any] = {}
        self.tag_data: Dict[str, List[Dict[str, Any]]] = {}
        
        # Setup logging
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)

        self.packet_count = 0
        self.last_counter_reset = datetime.now()

        # Initialize data structures for each tag
        for tag in self.config['tags']:
            self.tag_data[tag['name']] = []


    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {config_path} not found")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {e}")

    async def _setup_security(self) -> None:
        """Setup security for the OPC UA client."""
        security_policy = self.config['server']['security_policy']
        message_security_mode = self.config['server']['message_security_mode']
        
        # All possible combinations of security policy and message mode
        security_combinations = {
            # No Security
            ("None", "None"): (ua.SecurityPolicyType.NoSecurity, None),
            
            # Basic128Rsa15
            ("Basic128Rsa15", "Sign"): (ua.SecurityPolicyType.Basic128Rsa15_Sign, None),
            ("Basic128Rsa15", "SignAndEncrypt"): (ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt, None),
            
            # Basic256
            ("Basic256", "Sign"): (ua.SecurityPolicyType.Basic256_Sign, None),
            ("Basic256", "SignAndEncrypt"): (ua.SecurityPolicyType.Basic256_SignAndEncrypt, None),
            
            # Basic256Sha256
            ("Basic256Sha256", "Sign"): (ua.SecurityPolicyType.Basic256Sha256_Sign, None),
            ("Basic256Sha256", "SignAndEncrypt"): (ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt, None),
            
            # Aes128Sha256RsaOaep
            ("Aes128Sha256RsaOaep", "Sign"): (ua.SecurityPolicyType.Aes128Sha256RsaOaep_Sign, None),
            ("Aes128Sha256RsaOaep", "SignAndEncrypt"): (ua.SecurityPolicyType.Aes128Sha256RsaOaep_SignAndEncrypt, None),
        }
        
        combination_key = (security_policy, message_security_mode)
        
        try:
            if combination_key not in security_combinations:
                self.logger.warning(f"Unknown security combination: {security_policy} + {message_security_mode}, using None/None")
                combination_key = ("None", "None")
            
            policy, _ = security_combinations[combination_key]
            
            if policy == ua.SecurityPolicyType.NoSecurity:
                # No security - simple setup
                self.logger.info(f"Security policy: {security_policy}, Mode: {message_security_mode}")
                return
            else:
                # For encrypted connections, we need certificates
                cert_path = self.config['server']['certificate_path']
                key_path = self.config['server']['private_key_path']
                
                if not cert_path or not key_path:
                    raise ValueError(f"Certificate and private key paths required for security policy: {security_policy}")
                
                if not os.path.exists(cert_path) or not os.path.exists(key_path):
                    raise FileNotFoundError(f"Certificate file {cert_path} or private key {key_path} not found")
                
                # Set security with certificates
                self.client.set_security(policy, cert_path, key_path)
                self.logger.info(f"Security policy: {security_policy}, Mode: {message_security_mode}")
                self.logger.info(f"Using certificate: {cert_path}")
                
        except Exception as e:
            self.logger.error(f"Error setting up security: {e}")
            # Fallback to no security
            self.logger.info("Fallback to no security")

    async def _setup_authentication(self) -> None:
        """Setup authentication for the OPC UA client."""
        username = self.config['server']['username']
        password = self.config['server']['password']
        
        if username and password:
            self.client.set_user(username)
            self.client.set_password(password)
            self.logger.info(f"Using username/password authentication for user: {username}")

    def _write_to_json(self) -> None:
        """Write current data to JSON file."""
        try:
            json_path = self.config['logging']['data_file']
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(json_path) if os.path.dirname(json_path) else '.', exist_ok=True)
            
            # Write data to JSON file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.tag_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error writing to JSON: {e}")


    def _json_safe(self, v: Any) -> Any:
        """Convert values to JSON-serializable types."""
        if isinstance(v, (str, int, float, bool)) or v is None:
            return v

        # OPC UA ByteString -> bytes
        if isinstance(v, (bytes, bytearray, memoryview)):
            b = bytes(v)
            return {
                "__type__": "bytes",
                "encoding": "base64",
                "value": base64.b64encode(b).decode("ascii"),
            }

        # datetime/date -> ISO string
        if isinstance(v, (datetime, date)):
            return v.isoformat()

        # lists/tuples -> recursively convert
        if isinstance(v, (list, tuple)):
            return [self._json_safe(x) for x in v]

        # dict -> recursively convert
        if isinstance(v, dict):
            return {str(k): self._json_safe(val) for k, val in v.items()}

        # Fallback: string representation (covers ua.Variant-like oddities)
        return str(v)

    def datachange_notification(self, node, val, data) -> None:
        try:
            tag_name = None
            for tag in self.config['tags']:
                if node.nodeid.to_string() == tag['node_id']:
                    tag_name = tag['name']
                    break

            if not tag_name:
                self.logger.warning(f"Received data change for unknown node: {node.nodeid.to_string()}")
                return

            timestamp = datetime.now().strftime(self.config['logging']['timestamp_format'])

            data_point = {
                "timestamp": timestamp,
                "value": self._json_safe(val),   # <-- key change
            }
            self.tag_data[tag_name].append(data_point)

            self.logger.info(f"Data change for {tag_name}: {val} at {timestamp}")
            self._write_to_json()
            self.packet_count += 1

        except Exception as e:
            self.logger.error(f"Error handling data change: {e}")

    async def _setup_subscriptions(self) -> None:
        """Setup subscriptions for all configured tags."""
        try:
            # Create subscription
            subscription = await self.client.create_subscription(500, self)  # 500ms publishing interval
            
            for tag in self.config['tags']:
                try:
                    # Get the node
                    node = self.client.get_node(tag['node_id'])
                    
                    # Subscribe to data changes using the subscription
                    handle = await subscription.subscribe_data_change([node])
                    
                    self.subscriptions[tag['name']] = {
                        'node': node,
                        'handle': handle,
                        'subscription': subscription
                    }
                    
                    self.logger.info(f"Subscribed to tag: {tag['name']} ({tag['node_id']})")
                    
                except Exception as e:
                    self.logger.error(f"Error subscribing to tag {tag['name']}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error setting up subscriptions: {e}")
            raise

    async def connect(self) -> None:
        """Connect to OPC UA server and setup subscriptions."""
        try:
            server_url = self.config['server']['url']
            self.logger.info(f"Connecting to OPC UA server: {server_url}")
            
            self.client = Client(url=server_url)
            
            # Setup security and authentication
            await self._setup_security()
            await self._setup_authentication()
            
            # Connect to server
            await self.client.connect()
            self.logger.info("Connected to OPC UA server")
            
            # No initialization needed for JSON
            # Setup subscriptions
            await self._setup_subscriptions()
            
        except Exception as e:
            self.logger.error(f"Error connecting to OPC UA server: {e}")
            raise

    async def _packet_counter_task(self):
        while True:
            await asyncio.sleep(1)

            count = self.packet_count
            self.packet_count = 0

            self.logger.warning(f"Packets/sec: {count}")

    async def run(self) -> None:
        """Main run loop - keep the connection alive."""
        try:
            await self.connect()
            asyncio.create_task(self._packet_counter_task())
            self.logger.info("OPC UA Logger is running. Press Ctrl+C to stop.")
            
            # Keep the script running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            await self.disconnect()

    async def disconnect(self) -> None:
        """Disconnect from OPC UA server and cleanup."""
        try:
            if self.client:
                await self.client.disconnect()
                self.logger.info("Disconnected from OPC UA server")
                
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")

    def get_current_data(self) -> Dict[str, Any]:
        """Get current data for all tags."""
        current_data = {}
        for tag in self.config['tags']:
            tag_name = tag['name']
            if self.tag_data[tag_name]:
                current_data[tag_name] = self.tag_data[tag_name][-1]
            else:
                current_data[tag_name] = None
        return current_data


async def main():
    """Main entry point."""
    logger = OPCUALogger()
    await logger.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Program error: {e}")