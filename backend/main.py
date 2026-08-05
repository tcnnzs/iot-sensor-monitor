"""
IoT 传感器数据模拟器 — Web 后端服务

基于 FastAPI，通过 Server-Sent Events (SSE) 实时推送传感器数据到前端。
"""

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from sensor_simulator import SensorSimulator

# ---- 初始化 ----
app = FastAPI(
    title="IoT Sensor Dashboard API",
    description="实时传感器数据模拟器 — 适用于嵌入式/IoT 项目演示",
    version="1.0.0",
)

# 允许跨域（方便前端开发调试）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = SensorSimulator()

# ---- 挂载前端静态文件 ----
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """返回仪表盘首页"""
    html_path = frontend_dir / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "IoT Sensor Simulator"}


@app.get("/api/sensors")
async def get_sensors():
    """获取一帧传感器数据（用于轮询）"""
    return simulator.read_as_dict()


@app.get("/api/stream")
async def stream(request: Request):
    """
    SSE 实时数据流

    每秒推送一帧完整传感器数据，前端用 EventSource 接收。
    """
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            data = simulator.read_as_dict()
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---- 启动入口 ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
