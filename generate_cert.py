#!/usr/bin/env python3
"""
Certificate Generator for OPC UA Client
Generates self-signed certificate and private key for OPC UA encrypted connections
"""

import os
import sys
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import argparse


class CertificateGenerator:
    """A class to generate OPC UA certificates without running as a script."""
    
    def __init__(self):
        pass
    
    def generate(self, common_name="OPCUAClient", country="US", organization="MyCompany", 
                valid_days=3650, key_size=2048, output_dir="certs", update_config=False):
        """
        Generate self-signed certificate and private key for OPC UA client
        
        Args:
            common_name: Common name for certificate
            country: Country code
            organization: Organization name
            valid_days: Number of days certificate is valid
            key_size: RSA key size
            output_dir: Directory to save certificates
            update_config: Whether to update config.yaml with certificate paths
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )
            
            # Create certificate subject
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, ""),
                x509.NameAttribute(NameOID.LOCALITY_NAME, ""),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])
            
            # Build certificate
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=valid_days)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(common_name),
                    x509.DNSName("localhost"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Save private key
            key_path = os.path.join(output_dir, "opcua_client_private_key.pem")
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Save certificate
            cert_path = os.path.join(output_dir, "opcua_client_certificate.pem")
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Set environment variables
            os.environ['OPCUA_CERT_PATH'] = os.path.abspath(cert_path)
            os.environ['OPCUA_KEY_PATH'] = os.path.abspath(key_path)
            
            # Update config if requested
            if update_config:
                self._update_config_with_paths(cert_path, key_path)
            
            return True
            
        except Exception as e:
            print(f"Error generating certificate: {e}")
            return False
    
    def _update_config_with_paths(self, cert_path, key_path, config_file="config.yaml"):
        """Update config file with certificate paths"""
        try:
            import yaml
            
            # Read existing config
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update certificate paths
            config['server']['certificate_path'] = os.path.abspath(cert_path)
            config['server']['private_key_path'] = os.path.abspath(key_path)
            
            # Write back to config
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
        except ImportError:
            print("PyYAML not installed. Cannot update config file automatically.")
        except Exception as e:
            print(f"Error updating config file: {e}")


def generate_certificate(common_name="OPCUAClient", country="US", organization="MyCompany", 
                       valid_days=3650, key_size=2048, output_dir="certs"):
    """
    Generate self-signed certificate and private key for OPC UA client
    
    Args:
        common_name: Common name for the certificate
        country: Country code
        organization: Organization name
        valid_days: Number of days the certificate is valid
        key_size: RSA key size
        output_dir: Directory to save certificates
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    
    # Create certificate subject
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, ""),
        x509.NameAttribute(NameOID.LOCALITY_NAME, ""),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    # Build certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=valid_days)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(common_name),
            x509.DNSName("localhost"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Save private key
    key_path = os.path.join(output_dir, "opcua_client_private_key.pem")
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save certificate
    cert_path = os.path.join(output_dir, "opcua_client_certificate.pem")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print(f"✅ Certificate generated successfully!")
    print(f"📁 Certificate: {os.path.abspath(cert_path)}")
    print(f"🔑 Private Key: {os.path.abspath(key_path)}")
    print(f"📅 Valid for: {valid_days} days")
    print(f"🔒 Key Size: {key_size} bits")
    
    # Set environment variables
    print(f"\n🌍 Setting environment variables:")
    print(f"export OPCUA_CERT_PATH={os.path.abspath(cert_path)}")
    print(f"export OPCUA_KEY_PATH={os.path.abspath(key_path)}")
    
    # Export to current session
    os.environ['OPCUA_CERT_PATH'] = os.path.abspath(cert_path)
    os.environ['OPCUA_KEY_PATH'] = os.path.abspath(key_path)
    
    return cert_path, key_path


def update_config_with_paths(cert_path, key_path, config_file="config.yaml"):
    """Update config file with certificate paths"""
    try:
        import yaml
        
        # Read existing config
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update certificate paths
        config['server']['certificate_path'] = os.path.abspath(cert_path)
        config['server']['private_key_path'] = os.path.abspath(key_path)
        
        # Write back to config
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ Updated {config_file} with certificate paths")
        
    except ImportError:
        print("⚠️  PyYAML not installed. Cannot update config file automatically.")
        print("Please manually update your config.yaml with:")
        print(f"  certificate_path: {os.path.abspath(cert_path)}")
        print(f"  private_key_path: {os.path.abspath(key_path)}")
    except Exception as e:
        print(f"⚠️  Error updating config file: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate OPC UA client certificates")
    parser.add_argument("--cn", default="OPCUAClient", help="Common name for certificate")
    parser.add_argument("--country", default="US", help="Country code")
    parser.add_argument("--org", default="MyCompany", help="Organization name")
    parser.add_argument("--days", type=int, default=3650, help="Valid days (default: 3650)")
    parser.add_argument("--key-size", type=int, default=2048, help="RSA key size (default: 2048)")
    parser.add_argument("--output-dir", default="certs", help="Output directory (default: certs)")
    parser.add_argument("--update-config", action="store_true", help="Update config.yaml with certificate paths")
    parser.add_argument("--config-file", default="config.yaml", help="Config file to update (default: config.yaml)")
    
    args = parser.parse_args()
    
    try:
        print("🔐 Generating OPC UA Client Certificate...")
        cert_path, key_path = generate_certificate(
            common_name=args.cn,
            country=args.country,
            organization=args.org,
            valid_days=args.days,
            key_size=args.key_size,
            output_dir=args.output_dir
        )
        
        if args.update_config:
            update_config_with_paths(cert_path, key_path, args.config_file)
        
        print(f"\n🎉 Certificate generation complete!")
        print(f"\n📋 Usage:")
        print(f"1. Set security_policy to something other than 'None' in config.yaml")
        print(f"2. Set message_security_mode to 'Sign' or 'SignAndEncrypt'")
        print(f"3. Run the OPC UA logger: python opcua_logger.py")
        
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()