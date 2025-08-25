from fastapi import APIRouter, WebSocket, Depends
from app.core.deps import get_current_user

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_current_user)):
    await websocket.accept()
    await websocket.send_text(f"Connected as user {token.email}")
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")