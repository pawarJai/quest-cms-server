from motor.motor_asyncio import AsyncIOMotorClient
import os
from .config import settings

server_timeout = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000"))
connect_timeout = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "5000"))
socket_timeout = int(os.getenv("MONGO_SOCKET_TIMEOUT_MS", "15000"))

client = AsyncIOMotorClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=server_timeout,
    connectTimeoutMS=connect_timeout,
    socketTimeoutMS=socket_timeout,
)
db = client[settings.DB_NAME]
