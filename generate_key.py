#!/usr/bin/env python3
"""
Generate a secure random key for APP_SECRET_KEY
"""
import secrets

if __name__ == "__main__":
    # Generate a secure 32-byte random key
    key = secrets.token_urlsafe(32)
    print("Generated APP_SECRET_KEY:")
    print(key)
    print("\nAdd this to your .env file:")
    print(f"APP_SECRET_KEY={key}")
