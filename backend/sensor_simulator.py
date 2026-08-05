"""
传感器数据模拟器 — 模拟真实 IoT 设备上报的传感器数据

模拟 5 种传感器：温度、湿度、大气压、电压、电流
数据具有真实的物理特征：缓慢漂移 + 随机噪声 + 日周期波动
"""

import math
import random
import time
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SensorData:
    """单帧传感器数据"""
    timestamp: str
    temperature_c: float      # 温度（摄氏度）
    humidity_pct: float       # 湿度（%RH）
    pressure_hpa: float       # 大气压（hPa）
    voltage_v: float          # 电压（V）
    current_ma: float         # 电流（mA）


class SensorSimulator:
    """
    多传感器模拟器

    模拟策略：
    - 温度：以 24h 为周期的正弦波（模拟昼夜温差）+ 一阶马尔可夫漂移 + 高斯噪声
    - 湿度：与温度呈负相关 + 独立随机波动
    - 气压：在标准大气压附近慢漂移
    - 电压：标称值附近微小的低频波动（模拟电源纹波）
    - 电流：负载波动 + 随机尖峰
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

        # ---- 内部状态（用于产生连续、平滑的数据）----
        self._phase = random.uniform(0, 2 * math.pi)       # 日周期相位
        self._temp_drift = 0.0                              # 温度慢漂移
        self._pressure_state = 1013.25                      # 气压基准（海平面）
        self._voltage_state = 3.300                          # 电压基准
        self._current_base = 120.0                           # 电流基准

        # ---- 可配置参数 ----
        self.temp_mean = 25.0        # 平均温度 ℃
        self.temp_amplitude = 6.0    # 昼夜波动幅度 ℃
        self.humidity_mean = 55.0    # 平均湿度 %RH
        self.pressure_mean = 1013.25 # 平均气压 hPa

        self._start_time = time.time()

    def _simulated_hour(self) -> float:
        """返回模拟的"一天中的小时数"（0-24），压缩时间让演示更好看"""
        elapsed = time.time() - self._start_time
        # 每 60 秒真实时间 = 24 小时模拟时间（方便演示）
        return (elapsed / 60.0 * 24.0) % 24.0

    def read_all(self) -> SensorData:
        """读取全部传感器的一帧数据"""
        hour = self._simulated_hour()

        # ---- 温度：日周期 + 慢漂移 + 噪声 ----
        diurnal = self.temp_amplitude * math.sin(2 * math.pi * hour / 24.0 + self._phase)
        self._temp_drift += random.gauss(0, 0.02)  # 慢随机游走
        self._temp_drift = max(-3.0, min(3.0, self._temp_drift))  # 限幅
        temperature = self.temp_mean + diurnal + self._temp_drift + random.gauss(0, 0.3)

        # ---- 湿度：与温度负相关 + 独立噪声 ----
        temp_deviation = temperature - self.temp_mean
        humidity = self.humidity_mean - 1.8 * temp_deviation + random.gauss(0, 1.5)
        humidity = max(20.0, min(95.0, humidity))

        # ---- 气压：慢随机游走 ----
        self._pressure_state += random.gauss(0, 0.05)
        self._pressure_state += 0.01 * math.sin(2 * math.pi * hour / 12.0)  # 半日潮
        self._pressure_state = max(980.0, min(1050.0, self._pressure_state))

        # ---- 电压：标称值附近低频波动 ----
        self._voltage_state += random.gauss(0, 0.002)
        self._voltage_state += 0.005 * math.sin(2 * math.pi * hour / 6.0)
        voltage = max(3.20, min(3.40, self._voltage_state))

        # ---- 电流：基准值 + 负载波动 + 偶发尖峰 ----
        load_factor = 0.7 + 0.3 * abs(math.sin(2 * math.pi * hour / 8.0))
        current = self._current_base * load_factor + random.gauss(0, 5.0)
        # 偶尔加入尖峰（5% 概率）
        if random.random() < 0.05:
            current += random.uniform(30, 80)
        current = max(0.0, min(500.0, current))

        return SensorData(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            temperature_c=round(temperature, 2),
            humidity_pct=round(humidity, 1),
            pressure_hpa=round(self._pressure_state, 2),
            voltage_v=round(voltage, 3),
            current_ma=round(current, 2),
        )

    def read_as_dict(self) -> dict:
        return asdict(self.read_all())
