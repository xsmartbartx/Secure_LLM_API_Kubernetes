from fastapi import APIRouter

router = APIRouter()

@router.get("/ready")
async def readiness_probe():
    return {"status": "ready"}

@router.get("/live")
async def liveness_probe():
    return {"status": "alive"}
