"""
Simple test script to verify basic functionality
"""
import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import init_db, async_session_maker
from app.models import AppConfig
from app.utils.encryption import encryption
from app.utils.config import ConfigManager
from sqlalchemy import select


async def test_database():
    """Test database initialization"""
    print("🧪 Testing database initialization...")
    await init_db()
    print("✅ Database initialized successfully")


async def test_encryption():
    """Test encryption/decryption"""
    print("\n🧪 Testing encryption...")
    test_data = "secret-api-key-12345"
    
    encrypted = encryption.encrypt(test_data)
    print(f"  Encrypted: {encrypted[:20]}...")
    
    decrypted = encryption.decrypt(encrypted)
    assert decrypted == test_data, "Decryption failed!"
    print("✅ Encryption working correctly")


async def test_config():
    """Test config management"""
    print("\n🧪 Testing config management...")
    
    async with async_session_maker() as db:
        # Get or create config
        config = await ConfigManager.get_config(db)
        print(f"  Config ID: {config.id}")
        
        # Update Immich config
        await ConfigManager.update_immich_config(
            db,
            "https://immich.example.com",
            "test-api-key"
        )
        
        # Verify
        config = await ConfigManager.get_config(db)
        assert config.immich_url == "https://immich.example.com"
        
        api_key = ConfigManager.get_immich_api_key(config)
        assert api_key == "test-api-key"
        
        print("✅ Config management working correctly")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("  Immich → Google Photos Sync - Basic Tests")
    print("=" * 60)
    
    try:
        await test_database()
        await test_encryption()
        await test_config()
        
        print("\n" + "=" * 60)
        print("  ✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"  ❌ Test failed: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    # Set test database path
    os.environ["DATABASE_PATH"] = "./data/test.db"
    os.environ["APP_SECRET_KEY"] = "test-key-for-testing-purposes-only"
    
    asyncio.run(main())
