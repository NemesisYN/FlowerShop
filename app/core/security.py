from pwdlib import PasswordHash

from dotenv import load_dotenv

load_dotenv()


password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
   return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
   return password_hash.verify(password, hashed_password)