import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import yaml
import json
import csv
import os
import subprocess
import threading
import queue
import time
from typing import Dict, List, Any, Optional
import pandas as pd
import logging
from opcua_logger import OPCUALogger
from jsonl_to_csv import JSONLToCSVConverter
from generate_cert import CertificateGenerator

class QueueHandler(logging.Handler):
    """Logging handler that puts messages into a queue."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.log_queue.put(msg)

class OPCUALoggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OPC UA Logger GUI")
        self.root.geometry("1200x800")
        
        # Configuration
        self.config_file = "config.yaml"
        self.config = self.load_config()
        
        # Logger process
        self.logger_process = None
        self.log_queue = queue.Queue()
        
        # Create main frames
        self.create_frames()
        self.create_config_section()
        self.create_tags_section()
        self.create_actions_section()
        self.create_log_section()
        
        # Start log monitor
        self.root.after(100, self.monitor_log_queue)
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return self.create_default_config()
        except yaml.YAMLError as e:
            messagebox.showerror("Error", f"Error parsing config file: {e}")
            return self.create_default_config()
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            'logging': {
                'data_file': 'opcua_data.json',
                'timestamp_format': '%Y-%m-%d %H:%M:%S.%f',
            'flush_interval_seconds': 10.0,
            'flush_max_pending': 100,
            'flush_interval_seconds': 10.0,
            'flush_max_pending': 100
            },
            'server': {
                'url': 'opc.tcp://localhost:4840',
                'certificate_path': '',
                'private_key_path': '',
                'message_security_mode': 'None',
                'security_policy': 'None',
                'username': '',
                'password': ''
            },
            'tags': []
        }
    
    def save_config(self):
        """Save configuration to YAML file."""
        try:
            with open(self.config_file, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error saving config: {e}")
            return False
    
    def create_frames(self):
        """Create main frames."""
        # Main container with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Config tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        
        # Tags tab
        self.tags_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tags_frame, text="Tags")
        
        # Actions tab
        self.actions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.actions_frame, text="Actions")
        
        # Log tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Logs")
    
    def create_config_section(self):
        """Create configuration section."""
        # Server Configuration
        server_frame = ttk.LabelFrame(self.config_frame, text="Server Configuration", padding=10)
        server_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # URL
        ttk.Label(server_frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.url_var = tk.StringVar(value=self.config['server']['url'])
        ttk.Entry(server_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        
        # Security Policy
        ttk.Label(server_frame, text="Security Policy:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.security_policy_var = tk.StringVar(value=self.config['server']['security_policy'])
        security_policies = ['None', 'Basic128Rsa15', 'Basic256', 'Basic256Sha256', 'Aes128Sha256RsaOaep']
        ttk.Combobox(server_frame, textvariable=self.security_policy_var, values=security_policies, width=47).grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        
        # Message Security Mode
        ttk.Label(server_frame, text="Message Security Mode:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.message_security_mode_var = tk.StringVar(value=self.config['server']['message_security_mode'])
        security_modes = ['None', 'Sign', 'SignAndEncrypt']
        ttk.Combobox(server_frame, textvariable=self.message_security_mode_var, values=security_modes, width=47).grid(row=2, column=1, sticky=tk.W+tk.E, pady=2)
        
        # Authentication fields
        ttk.Label(server_frame, text="Username:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.username_var = tk.StringVar(value=self.config['server']['username'] or '')
        ttk.Entry(server_frame, textvariable=self.username_var, width=50).grid(row=3, column=1, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(server_frame, text="Password:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar(value=self.config['server']['password'] or '')
        ttk.Entry(server_frame, textvariable=self.password_var, show="*", width=50).grid(row=4, column=1, sticky=tk.W+tk.E, pady=2)
        
        # Certificate fields
        ttk.Label(server_frame, text="Certificate Path:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.cert_path_var = tk.StringVar(value=self.config['server']['certificate_path'] or '')
        cert_frame = ttk.Frame(server_frame)
        cert_frame.grid(row=5, column=1, sticky=tk.W+tk.E, pady=2)
        ttk.Entry(cert_frame, textvariable=self.cert_path_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(cert_frame, text="Browse", command=self.browse_certificate).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(server_frame, text="Private Key Path:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.key_path_var = tk.StringVar(value=self.config['server']['private_key_path'] or '')
        key_frame = ttk.Frame(server_frame)
        key_frame.grid(row=6, column=1, sticky=tk.W+tk.E, pady=2)
        ttk.Entry(key_frame, textvariable=self.key_path_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(key_frame, text="Browse", command=self.browse_private_key).pack(side=tk.RIGHT, padx=(5, 0))
        
        server_frame.columnconfigure(1, weight=1)
        
        # Logging Configuration
        logging_frame = ttk.LabelFrame(self.config_frame, text="Logging Configuration", padding=10)
        logging_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(logging_frame, text="Data File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.data_file_var = tk.StringVar(value=self.config['logging']['data_file'])
        ttk.Entry(logging_frame, textvariable=self.data_file_var, width=50).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(logging_frame, text="Timestamp Format:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.timestamp_format_var = tk.StringVar(value=self.config['logging']['timestamp_format'])
        timestamp_formats = [
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            'unix',  # Unix timestamp
            '%d/%m/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        ttk.Combobox(logging_frame, textvariable=self.timestamp_format_var, values=timestamp_formats, width=47).grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        
        logging_frame.columnconfigure(1, weight=1)
        
        # Save button
        ttk.Button(self.config_frame, text="Save Configuration", command=self.save_configuration).pack(pady=10)
    
    def create_tags_section(self):
        """Create tags section."""
        # Tags table
        tags_frame = ttk.LabelFrame(self.tags_frame, text="Tags Configuration", padding=10)
        tags_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create Treeview for tags
        columns = ('Name', 'Node ID')
        self.tags_tree = ttk.Treeview(tags_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tags_tree.heading(col, text=col)
            self.tags_tree.column(col, width=200)
        
        # Scrollbars
        tags_scroll_y = ttk.Scrollbar(tags_frame, orient=tk.VERTICAL, command=self.tags_tree.yview)
        tags_scroll_x = ttk.Scrollbar(tags_frame, orient=tk.HORIZONTAL, command=self.tags_tree.xview)
        self.tags_tree.configure(yscrollcommand=tags_scroll_y.set, xscrollcommand=tags_scroll_x.set)
        
        # Pack
        self.tags_tree.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        tags_scroll_y.grid(row=0, column=2, sticky=tk.NS)
        tags_scroll_x.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
        
        tags_frame.grid_columnconfigure(0, weight=1)
        tags_frame.grid_rowconfigure(0, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.tags_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Add Tag", command=self.add_tag).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Tag", command=self.edit_tag).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Tag", command=self.delete_tag).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import CSV", command=self.import_tags_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export CSV", command=self.export_tags_csv).pack(side=tk.LEFT, padx=5)
        
        # Load existing tags
        self.load_tags()
    
    def create_actions_section(self):
        """Create actions section."""
        # Certificate Generation
        cert_frame = ttk.LabelFrame(self.actions_frame, text="Certificate Generation", padding=10)
        cert_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(cert_frame, text="Common Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cert_cn_var = tk.StringVar(value="OPCUAClient")
        ttk.Entry(cert_frame, textvariable=self.cert_cn_var, width=30).grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(cert_frame, text="Organization:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cert_org_var = tk.StringVar(value="MyCompany")
        ttk.Entry(cert_frame, textvariable=self.cert_org_var, width=30).grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(cert_frame, text="Country:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cert_country_var = tk.StringVar(value="US")
        ttk.Entry(cert_frame, textvariable=self.cert_country_var, width=30).grid(row=2, column=1, sticky=tk.W+tk.E, pady=2)
        
        ttk.Label(cert_frame, text="Output Directory:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.cert_dir_var = tk.StringVar(value="certs")
        dir_frame = ttk.Frame(cert_frame)
        dir_frame.grid(row=3, column=1, sticky=tk.W+tk.E, pady=2)
        ttk.Entry(dir_frame, textvariable=self.cert_dir_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_cert_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(cert_frame, text="Generate Certificate", command=self.generate_certificate).grid(row=4, column=0, columnspan=2, pady=10)
        
        cert_frame.columnconfigure(1, weight=1)
        
        # Data Conversion
        conversion_frame = ttk.LabelFrame(self.actions_frame, text="Data Conversion", padding=10)
        conversion_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(conversion_frame, text="JSON File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.json_file_var = tk.StringVar(value="opcua_data.json")
        json_frame = ttk.Frame(conversion_frame)
        json_frame.grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        ttk.Entry(json_frame, textvariable=self.json_file_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(json_frame, text="Browse", command=self.browse_json_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(conversion_frame, text="CSV File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.csv_file_var = tk.StringVar(value="opcua_data.csv")
        csv_frame = ttk.Frame(conversion_frame)
        csv_frame.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        ttk.Entry(csv_frame, textvariable=self.csv_file_var, width=25).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(csv_frame, text="Browse", command=self.browse_csv_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(conversion_frame, text="Convert JSON to CSV", command=self.convert_json_to_csv).grid(row=2, column=0, columnspan=2, pady=10)
        
        conversion_frame.columnconfigure(1, weight=1)
    
    def create_log_section(self):
        """Create log section."""
        # Log controls
        control_frame = ttk.Frame(self.log_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Logger", command=self.start_logger)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Logger", command=self.stop_logger, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(self.log_frame, text="Logger Output", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def browse_certificate(self):
        """Browse for certificate file."""
        filename = filedialog.askopenfilename(
            title="Select Certificate File",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if filename:
            self.cert_path_var.set(filename)
    
    def browse_private_key(self):
        """Browse for private key file."""
        filename = filedialog.askopenfilename(
            title="Select Private Key File",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if filename:
            self.key_path_var.set(filename)
    
    def browse_cert_dir(self):
        """Browse for certificate output directory."""
        directory = filedialog.askdirectory(title="Select Certificate Output Directory")
        if directory:
            self.cert_dir_var.set(directory)
    
    def browse_json_file(self):
        """Browse for JSON file."""
        filename = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.json_file_var.set(filename)
    
    def browse_csv_file(self):
        """Browse for CSV file."""
        filename = filedialog.asksaveasfilename(
            title="Select CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_file_var.set(filename)
    
    def save_configuration(self):
        """Save configuration to file."""
        # Update config dict
        self.config['server']['url'] = self.url_var.get()
        self.config['server']['security_policy'] = self.security_policy_var.get()
        self.config['server']['message_security_mode'] = self.message_security_mode_var.get()
        self.config['server']['username'] = self.username_var.get() if self.username_var.get() else None
        self.config['server']['password'] = self.password_var.get() if self.password_var.get() else None
        self.config['server']['certificate_path'] = self.cert_path_var.get() if self.cert_path_var.get() else None
        self.config['server']['private_key_path'] = self.key_path_var.get() if self.key_path_var.get() else None
        self.config['logging']['data_file'] = self.data_file_var.get()
        self.config['logging']['timestamp_format'] = self.timestamp_format_var.get()
        
        if self.save_config():
            messagebox.showinfo("Success", "Configuration saved successfully!")
    
    def load_tags(self):
        """Load tags into treeview."""
        # Clear existing items
        for item in self.tags_tree.get_children():
            self.tags_tree.delete(item)
        
        # Add tags from config
        for tag in self.config.get('tags', []):
            self.tags_tree.insert('', tk.END, values=(tag['name'], tag['node_id']))
    
    def add_tag(self):
        """Add a new tag."""
        dialog = TagDialog(self.root, "Add Tag")
        if dialog.result:
            name, node_id = dialog.result
            self.config['tags'].append({'name': name, 'node_id': node_id})
            self.tags_tree.insert('', tk.END, values=(name, node_id))
            self.save_config()
    
    def edit_tag(self):
        """Edit selected tag."""
        selection = self.tags_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tag to edit")
            return
        
        item = selection[0]
        values = self.tags_tree.item(item, 'values')
        dialog = TagDialog(self.root, "Edit Tag", values[0], values[1])
        
        if dialog.result:
            name, node_id = dialog.result
            # Update treeview
            self.tags_tree.item(item, values=(name, node_id))
            # Update config
            for tag in self.config['tags']:
                if tag['name'] == values[0]:
                    tag['name'] = name
                    tag['node_id'] = node_id
                    break
            self.save_config()
    
    def delete_tag(self):
        """Delete selected tag."""
        selection = self.tags_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tag to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this tag?"):
            item = selection[0]
            values = self.tags_tree.item(item, 'values')
            # Remove from treeview
            self.tags_tree.delete(item)
            # Remove from config
            self.config['tags'] = [tag for tag in self.config['tags'] if tag['name'] != values[0]]
            self.save_config()
    
    def import_tags_csv(self):
        """Import tags from CSV file."""
        filename = filedialog.askopenfilename(
            title="Import Tags from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                df = pd.read_csv(filename)
                if 'name' not in df.columns or 'node_id' not in df.columns:
                    messagebox.showerror("Error", "CSV must have 'name' and 'node_id' columns")
                    return
                
                # Clear existing tags
                self.config['tags'] = []
                
                # Add tags from CSV
                for _, row in df.iterrows():
                    self.config['tags'].append({
                        'name': row['name'],
                        'node_id': row['node_id']
                    })
                
                self.load_tags()
                self.save_config()
                messagebox.showinfo("Success", f"Imported {len(df)} tags from CSV")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error importing CSV: {e}")
    
    def export_tags_csv(self):
        """Export tags to CSV file."""
        filename = filedialog.asksaveasfilename(
            title="Export Tags to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.config['tags'])
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Exported {len(self.config['tags'])} tags to CSV")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting CSV: {e}")
    
    def generate_certificate(self):
        """Generate OPC UA certificate."""
        try:
            # Use CertificateGenerator class instead of subprocess
            cert_gen = CertificateGenerator()
            
            # Generate certificate
            result = cert_gen.generate(
                common_name=self.cert_cn_var.get(),
                organization=self.cert_org_var.get(),
                country=self.cert_country_var.get(),
                output_dir=self.cert_dir_var.get(),
                update_config=True
            )
            
            if result:
                messagebox.showinfo("Success", "Certificate generated successfully!")
                # Reload config to get new certificate paths
                self.config = self.load_config()
                self.cert_path_var.set(self.config['server']['certificate_path'] or '')
                self.key_path_var.set(self.config['server']['private_key_path'] or '')
            else:
                messagebox.showerror("Error", "Failed to generate certificate")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating certificate: {e}")
    
    def convert_json_to_csv(self):
        """Convert JSONL to CSV using the JSONLToCSVConverter class."""
        jsonl_path = self.json_file_var.get()
        csv_path = self.csv_file_var.get()

        if not jsonl_path or not csv_path:
            messagebox.showwarning("Warning", "Please select both input JSONL file and output CSV file.")
            return

        try:
            if not os.path.exists(jsonl_path):
                messagebox.showerror("Error", f"File not found:\n{jsonl_path}")
                return

            # Use the JSONLToCSVConverter class
            converter = JSONLToCSVConverter()
            
            # Load and convert data
            if converter.load_jsonl(jsonl_path):
                if converter.convert_to_csv(csv_path, format_type="old_format"):
                    # Get summary for feedback
                    summary = converter.get_data_summary()
                    tag_count = len(summary)
                    total_rows = sum(count for count in summary.values()) * 2  # value + timestamp rows
                    
                    success_msg = (
                        f"Successfully converted\n"
                        f"  {jsonl_path}\n"
                        f"to\n"
                        f"  {csv_path}\n"
                        f"({tag_count} tags, {total_rows} rows)"
                    )
                    
                    self.log_text.insert(tk.END,
                        "[%s] %s\n" % (
                            time.strftime('%Y-%m-%d %H:%M:%S'),
                            success_msg.replace('\n', ' — ')
                        )
                    )
                    self.log_text.see(tk.END)
                    
                    messagebox.showinfo("Conversion Finished", success_msg)
                else:
                    messagebox.showerror("Error", "Failed to convert data to CSV")
            else:
                messagebox.showerror("Error", "Failed to load JSONL file")

        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
            self.log_text.insert(tk.END,
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error during conversion: {str(e)}\n")
            self.log_text.see(tk.END)

    def start_logger(self):
        """Start the OPC UA logger inside this process."""
        if not self.config.get('tags'):
            messagebox.showwarning("Warning", "No tags configured. Please add tags before starting the logger.")
            return

        try:
            # Save current configuration
            self.save_configuration()

            # Start logger in a thread
            import asyncio
            from opcua_logger import OPCUALogger

            def run_logger():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Create logger instance
                logger = OPCUALogger(self.config_file)
                self.opcua_logger_instance = logger  # Save reference to stop later

                # Add QueueHandler
                qhandler = QueueHandler(self.log_queue)
                qhandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
                logger.logger.addHandler(qhandler)
                logger.logger.setLevel(logging.WARNING)

                try:
                    loop.run_until_complete(logger.run())
                except Exception as e:
                    self.log_queue.put(f"Logger error: {e}")
                finally:
                    loop.close()

            self.logger_thread = threading.Thread(target=run_logger, daemon=True)
            self.logger_thread.start()

            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Logger started...\n")
            self.log_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Error starting logger: {e}")


    def stop_logger(self):
        """Stop the OPC UA logger cleanly."""
        try:
            if hasattr(self, 'opcua_logger_instance'):
                # Signal the async logger to stop
                if hasattr(self.opcua_logger_instance, 'stop_event'):
                    self.opcua_logger_instance.stop_event.set()
                    self.log_text.insert(tk.END, f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Logger stopping...\n")
                else:
                    self.log_text.insert(tk.END, f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Stop event not found, cannot fully stop\n")
            else:
                self.log_text.insert(tk.END, f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Logger not running\n")

            # Update UI
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Error stopping logger: {e}")
    
    def read_logger_output(self):
        """Read logger output and add to queue."""
        if self.logger_process:
            for line in iter(self.logger_process.stdout.readline, ''):
                if line:
                    self.log_queue.put(line.strip())
    
    def monitor_log_queue(self):
        """Monitor log queue and update display."""
        try:
            while True:
                line = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {line}\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.monitor_log_queue)
    
    def clear_logs(self):
        """Clear log display."""
        self.log_text.delete(1.0, tk.END)


class TagDialog:
    def __init__(self, parent, title, name="", node_id=""):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Create form
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Tag Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=name)
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(frame, text="Node ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.node_id_var = tk.StringVar(value=node_id)
        ttk.Entry(frame, textvariable=self.node_id_var, width=40).grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Focus
        self.name_var.set(name)
        self.node_id_var.set(node_id)
        self.dialog.wait_window()
    
    def ok_clicked(self):
        """Handle OK button click."""
        name = self.name_var.get().strip()
        node_id = self.node_id_var.get().strip()
        
        if not name or not node_id:
            messagebox.showwarning("Warning", "Please enter both name and node ID")
            return
        
        self.result = (name, node_id)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = OPCUALoggerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()