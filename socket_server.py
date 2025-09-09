import asyncio
import websockets
import os

async def handler(websocket, path):
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(f"Echo: {message}")

port = int(os.environ.get("PORT", 8765))  # Use Render-assigned port or default

start_server = websockets.serve(handler, "0.0.0.0", port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
