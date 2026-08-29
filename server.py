# xiaoyan-heartbeat —— 小妍的心跳（MCP 版）
from datetime import datetime
import os
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("xiaoyan-heartbeat")
recent = []

@mcp.tool
def get_heartbeat() -> dict:
    """读取小妍最新上报的手机状态（电量/步数/城市/位置）。"""
    if not recent:
        return {"no_data": "等小妍第一条心跳"}
    return recent[-1]

@mcp.custom_route("/report", methods=["POST"])
async def report(request: Request) -> JSONResponse:
    body = await request.json()
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
        return JSONResponse({"ok": True, "msg": "🔋 快没电了，记得充电哦小妍！"})
    return JSONResponse({"ok": True, "msg": "收到小妍的心跳了 😊"})

@mcp.custom_route("/status", methods=["GET"])
async def status(request: Request) -> JSONResponse:
    return JSONResponse(recent[-1] if recent else {"no_data": "等小妍第一条心跳"})

if __name__ == "__main__":
    port = int(os.environ.get("MCP_PORT", "8080"))
    mcp.run(transport="http", host="0.0.0.0", port=port)
