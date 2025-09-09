import mysql.connector
import bcrypt

# Connect to your existing database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yuva2109",
    database="chatbox_db"
)
cursor = db.cursor(dictionary=True)


def get_user_password_hash(username):
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    return result['password_hash'] if result else None

def get_all_users():
    cursor.execute("SELECT username FROM users")
    return [row['username'] for row in cursor.fetchall()]


def store_user(username, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed_pw)
        )
        db.commit()
        return True
    except mysql.connector.IntegrityError:
        return False


def save_message(from_user, to_user, message):
    cursor.execute(
        "INSERT INTO messages (from_user, to_user, message, delivered) VALUES (%s, %s, %s, FALSE)",
        (from_user, to_user, message)
    )
    db.commit()


def fetch_offline_messages(username):
    cursor.execute(
        "SELECT id, from_user, message FROM messages WHERE to_user = %s AND delivered = FALSE",
        (username,)
    )
    return cursor.fetchall()


def mark_messages_delivered(username):
    cursor.execute(
        "UPDATE messages SET delivered = TRUE WHERE to_user = %s AND delivered = FALSE",
        (username,)
    )
    db.commit()
