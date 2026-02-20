"""
Generate a valid 2FA encryption key for use in .env file
"""
from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    key_string = key.decode()
    
    print("=" * 60)
    print("2FA Encryption Key Generator")
    print("=" * 60)
    print()
    print("Generated key (add this to your .env file):")
    print()
    print(f"2FA_ENCRYPTION_KEY={key_string}")
    print()
    print("=" * 60)
    print("Instructions:")
    print("1. Copy the key above")
    print("2. Open your .env file")
    print("3. Add or update the line: 2FA_ENCRYPTION_KEY=<paste_key_here>")
    print("4. Save the file and restart your backend server")
    print("=" * 60)
