# ⚡ IoT 传感器数据模拟器 + 实时监控面板

> 纯 Python 后端 + Web 前端 | 零硬件成本 | 电子信息/嵌入式/IoT 方向简历项目

---

## 📸 效果预览

启动后在浏览器打开 `http://localhost:8080`，你将看到：

- 🌡 **5 个传感器数值卡片**（温度、湿度、气压、电压、电流）实时跳动
- 📈 **3 个实时折线图**（温湿度双轴图、电压曲线、电流曲线）
- 🔴 **连接状态指示灯** + 数据帧计数器

传感器数据具有**真实物理特征**：昼夜温度周期、湿度与温度负相关、气压半日潮、电压纹波、电流负载尖峰。

---

## 🛠 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python 3.10+ / FastAPI | REST API + SSE 实时推送 |
| 前端 | HTML5 / Chart.js | 暗色主题仪表盘，响应式布局 |
| 数据模拟 | Python 自研算法 | 日周期 + 随机游走 + 高斯噪声 |
| 实时通信 | Server-Sent Events | 每秒推送一帧，前端 EventSource 接收 |

---

## 🚀 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

### 3. 打开浏览器

访问 **http://localhost:8080**

---

## 📁 项目结构

```
sensor-dashboard/
├── backend/
│   ├── main.py              # FastAPI 服务入口
│   ├── sensor_simulator.py  # 传感器数据模拟算法
│   └── requirements.txt     # Python 依赖
├── frontend/
│   └── index.html           # 前端仪表盘（Chart.js）
└── README.md
```

---

## 🔌 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 仪表盘页面 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/sensors` | 获取一帧传感器 JSON |
| GET | `/api/stream` | SSE 实时数据流（每秒1帧） |

### 传感器数据格式

```json
{
  "timestamp": "2026-08-05 14:30:01",
  "temperature_c": 28.35,
  "humidity_pct": 48.2,
  "pressure_hpa": 1011.57,
  "voltage_v": 3.312,
  "current_ma": 98.45
}
```

---

## 🧠 数据模拟算法

`SensorSimulator` 类采用多层模型叠加，产生**逼真的连续传感器数据**：

| 物理量 | 模拟策略 |
|--------|----------|
| 温度 | 24h 正弦周期（昼夜温差）+ 一阶马尔可夫漂移 + 高斯噪声 |
| 湿度 | 与温度负相关（-1.8 %RH/°C）+ 独立随机波动 |
| 气压 | 慢随机游走 + 12h 半日潮汐分量 |
| 电压 | 3.3V 基准 + 低频纹波（模拟电源噪声） |
| 电流 | 时变负载 + 高斯噪声 + 5% 概率尖峰（模拟设备突发功耗） |

---

## 📄 License

MIT — 随意使用、修改。
