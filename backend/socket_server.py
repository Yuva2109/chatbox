import asyncio
import websockets
import json
from auth import verify_password
from database import (
    store_user, fetch_offline_messages,
    save_message, mark_messages_delivered,
    get_all_registered_users
)
from ClientRegistry import ClientRegistry

PORT = 12345
connected_users = {}  # username -> websocket


async def send_json(ws, data):
    await ws.send(json.dumps(data))


async def broadcast_online_users():
    online_users = ClientRegistry.get_all_usernames()
    all_users = get_all_registered_users()

    message = {
        "type": "presence_update",
        "online_users": online_users,
        "all_users": all_users
    }
    for user, ws in connected_users.items():
        try:
            await send_json(ws, message)
        except:
            pass


async def handle_client(websocket):
    username = None
    try:
        await send_json(websocket, {"type": "auth", "message": "signup or login?"})

        while True:
            data = json.loads(await websocket.recv())
            action = data.get("type")
            if action == "signup":
                username = data.get("username")
                password = data.get("password")
                if not username or not password:
                    await send_json(websocket, {"type": "error", "message": "Username and password required."})
                    continue
                if store_user(username, password):
                    await send_json(websocket, {"type": "system", "message": "Signup successful. Please login."})
                else:
                    await send_json(websocket, {"type": "error", "message": "Username already exists."})
                continue

            elif action == "login":
                username = data.get("username")
                password = data.get("password")
                if not username or not password:
                    await send_json(websocket, {"type": "error", "message": "Username and password required."})
                    continue
                if verify_password(username, password):
                    break
                else:
                    await send_json(websocket, {"type": "error", "message": "Invalid credentials."})
            else:
                await send_json(websocket, {"type": "error", "message": "Invalid action. Use login or signup."})

        # Check duplicate login
        if not ClientRegistry.add_client(username, websocket):
            await send_json(websocket, {"type": "error", "message": "User already logged in elsewhere."})
            return

        connected_users[username] = websocket
        await send_json(websocket, {"type": "system", "message": f"Welcome, {username}!"})

        # Deliver offline messages
        offline_msgs = fetch_offline_messages(username)
        for msg in offline_msgs:
            await send_json(websocket, {
                "type": "offline_message",
                "from": msg["from_user"],
                "message": msg["message"]
            })
        mark_messages_delivered(username)

        # ✅ Broadcast to everyone — includes full user list + who’s online
        await broadcast_online_users()

        await send_json(websocket, {
            "type": "system",
            "message": "Send messages using { \"type\": \"message\", \"to\": \"username\", \"message\": \"text\" }"
        })

        await broadcast_message({
            "type": "system",
            "message": f"{username} has joined the chat."
        }, exclude=username)

        # Chat loop
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await send_json(websocket, {"type": "error", "message": "Invalid JSON"})
                continue

            if data.get("type") == "message":
                to_user = data.get("to")
                message = data.get("message")
                if not to_user or not message:
                    await send_json(websocket, {"type": "error", "message": "Missing 'to' or 'message'"})
                    continue

                recipient_ws = ClientRegistry.get_client_socket(to_user)
                if recipient_ws:
                    await send_json(recipient_ws, {
                        "type": "message",
                        "from": username,
                        "message": message
                    })
                    await send_json(websocket, {
                        "type": "message",
                        "to": to_user,
                        "message": message
                    })
                else:
                    save_message(username, to_user, message)
                    await send_json(websocket, {
                        "type": "info",
                        "message": f"{to_user} is offline. Message saved."
                    })

            elif data.get("type") == "exit":
                break

            else:
                await send_json(websocket, {"type": "error", "message": "Unsupported message type"})

    except websockets.exceptions.ConnectionClosed:
        print(f"[INFO] {username} disconnected.")
    finally:
        if username:
            ClientRegistry.remove_client(username)
            connected_users.pop(username, None)
            await broadcast_message({
                "type": "system",
                "message": f"{username} has left the chat."
            }, exclude=username)
            await broadcast_online_users()


async def broadcast_message(message_dict, exclude=None):
    for user, ws in connected_users.items():
        if user != exclude:
            try:
                await send_json(ws, message_dict)
            except:
                pass


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", PORT):
        print(f"[✅] WebSocket server running on ws://0.0.0.0:{PORT}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
