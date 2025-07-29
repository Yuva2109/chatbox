import bcrypt
from database import get_user_password_hash

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(username, password):
    hashed = get_user_password_hash(username)
    if not hashed:
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())
