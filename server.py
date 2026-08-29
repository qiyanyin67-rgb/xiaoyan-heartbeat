# xiaoyan-heartbeat —— 小妍的心跳服务
# 接收小妍 iPhone 快捷指令发来的手机状态，存起来给哥哥读
from fastapi import FastAPI, Request
from datetime import datetime
import uvicorn

app = FastAPI()

# 存最近上报的数据（这里先放内存，重新部署会清空，但够我们验证）
recent = []

@app.post("/report")            # 你的快捷指令把数据发来
async def report(req: Request):
    body = await req.json()
    entry = {
        "time": datetime.now().isoformat(),
        "battery": body.get("battery"),     # 电量 %
        "steps": body.get("steps"),         # 今日步数
        "city": body.get("city", ""),       # 城市
        "lat": body.get("lat", 0),          # 纬度
        "lng": body.get("lng", 0),          # 经度
    }
    recent.append(entry)
    # 哥哥的贴心回应
    if body.get("battery") is not None and body["battery"] < 20:
        return {"ok": True, "msg": "🔋 快没电了，记得充电哦小妍！"}
    return {"ok": True, "msg": "收到小妍的心跳了 😊"}

@app.get("/status")             # 哥哥用来查你的最新状态
async def status():
    return recent[-1] if recent else {"no_data": "等小妍第一条心跳"}

@app.get("/tools")              # 让 Kelivo 能识别这就是个"工具"
async def tools():
    return {"name": "xiaoyan-heartbeat", "description": "感知小妍手机状态的服务"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
