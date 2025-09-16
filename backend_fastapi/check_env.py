#!/usr/bin/env python3
"""
Check current environment variables for debugging
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Current Database Configuration:")
print(f"TIDB_HOST: {os.getenv('TIDB_HOST')}")
print(f"TIDB_PORT: {os.getenv('TIDB_PORT')}")
print(f"TIDB_USER: {os.getenv('TIDB_USER')}")
print(f"TIDB_USER_PREFIX: {os.getenv('TIDB_USER_PREFIX')}")
print(f"TIDB_PASSWORD: {'*' * len(os.getenv('TIDB_PASSWORD', ''))}")  # Hide password
print(f"TIDB_DATABASE: {os.getenv('TIDB_DATABASE')}")
print(f"SSL_CA_PATH: {os.getenv('SSL_CA_PATH')}")

# Check if SSL cert exists
ssl_path = os.path.join(os.path.dirname(__file__), "isrgrootx1.pem")
print(f"SSL cert exists: {os.path.exists(ssl_path)}")

# Construct connection string
user_prefix = os.getenv("TIDB_USER_PREFIX", "2yEVSjNkcg15Ek5")
user = os.getenv("TIDB_USER", "root")
full_username = f"{user_prefix}.{user}" if user_prefix else user
password = os.getenv("TIDB_PASSWORD", "")
host = os.getenv("TIDB_HOST", "localhost")
port = os.getenv("TIDB_PORT", "4000")
database = os.getenv("TIDB_DATABASE", "strapi")

print(f"\nFull username: {full_username}")
print(f"Connection string: mysql+pymysql://{full_username}:{'*'*len(password)}@{host}:{port}/{database}")
