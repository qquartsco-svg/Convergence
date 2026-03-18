"""ConvergenceDynamics_Engine — 수렴 과정 동역학 분석 엔진

정체성:
  IrrationalApprox_Engine가 "무리수를 계산"한다면,
  이 엔진은 "그 계산 과정의 수렴 동역학을 분석"한다.

  대상은 무리수 자체가 아니라 수렴 과정(history[])이다.

레이어: 40_SPATIAL_LAYER
역할:   독립 보조 엔진 — IrrationalApprox_Engine의 하위 유틸이 아님

3엔진 구조 내 위치:
  IrrationalApprox_Engine   → 계산기 (수렴 생성)
  ConvergenceDynamics_Engine → 판정기 (수렴 과정 동역학 분석)  ← 여기
  irrational_algebra         → 해석기 (현재 상태 구조 판독)
"""
from .engine import ConvergenceDynamicsEngine
from .models import MethodDynamics, ConvergenceDynamicsReport
from .analyzer import analyze, compare, health_from_dynamics

__all__ = [
    "ConvergenceDynamicsEngine",
    "MethodDynamics",
    "ConvergenceDynamicsReport",
    "analyze",
    "compare",
    "health_from_dynamics",
]

__version__ = "1.0.0"
