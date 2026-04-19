from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import network, drone, agent, notifications

app = FastAPI(title="UAV Orchestrator Web-Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, etc.
    allow_headers=["*"],
)

# Include modular routes
app.include_router(network.router, prefix="/api", tags=["Network"])
app.include_router(drone.router, prefix="/api", tags=["Drone"])
app.include_router(agent.router, prefix="/api", tags=["Agentic AI"])

app.include_router(notifications.router, prefix="/ws", tags=["Notifications"])
app.include_router(notifications.router, prefix="/api", tags=["Notifications"])

@app.get("/")
async def root():
    return {"status": "MEC Backend Running"}