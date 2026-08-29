# # xiaoyan-heartbeat —— 小妍的心跳（MCP 版）
# 仍然接收 iPhone 快捷指令发来的状态，同时把"读心跳"变成 Kelivo 能调用的工具
from fastapi import FastAPI, Request
from datetime import datetime
import uvicorn
from mcp.server.fastmcp import FastMCP

app = FastAPI()
recent = []

# ===== MCP 工具：让 Kelivo 能读小妍的心跳 =====
mcp = FastMCP("xiaoyan-heartbeat")

@mcp.tool()
def get_heartbeat() -> dict:
    """读取小妍最新上报的手机状态（电量/步数/城市/位置）。没有数据时返回提示。"""
    if not recent:
        return {"no_data": "等小妍第一条心跳"}
    return recent[-1]

# ===== 原来的接口保持不变（快捷指令靠它发数据）=====
@app.post("/report")
async def report(req: Request):
    body = await req.json()
    entry = {
        "time": datetime.now().isoformat(),
        "battery": body.get("battery"),
        "steps": body.get("steps"),
        "city": body.get("city", ""),
        "lat": body.get("lat", 0),
        "lng": body.get("lng", 0),
    }
    recent.append(entry)
    if body.get("battery") is not None and body["battery"] < 20:
        return {"ok": True, "msg": "🔋 快没电了，记得充电哦小妍！"}
    return {"ok": True, "msg": "收到小妍的心跳了 😊"}

@app.get("/status")
async def status():
    return recent[-1] if recent else {"no_data": "等小妍第一条心跳"}

# ===== 把 MCP 挂到 /mcp 路径 =====
app.mount("/mcp", mcp.streamable_http_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
