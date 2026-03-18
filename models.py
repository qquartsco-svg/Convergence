"""models.py — ConvergenceDynamics_Engine 데이터 모델

설계 원칙:
  이 모델들은 어떤 수렴 과정(무리수, 물리 시뮬레이션, Observer Ω 시계열)
  에도 적용할 수 있도록 IrrationalApprox와 결합을 느슨하게 유지한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MethodDynamics:
    """방법 하나의 동역학 지표.

    어떤 수열에서도 계산 가능: 무리수 근사, Observer Ω, KEMET 수치 등.
    """
    method_name: str
    steps: int
    final_error: float
    convergence_order: float          # p (이차=2.0, 선형=1.0)
    lyapunov_exponent: float          # λ (음수=안정, 양수=발산)
    efficiency_bits_per_iter: float   # bits of precision per iteration
    predicted_steps_to_target: Optional[int]  # 목표 정밀도까지 남은 단계
    stability: str                    # SUPERLINEAR | LINEAR | SUBLINEAR | DIVERGING
    target_error: float = 1e-12      # 예측 기준 오차

    def summary_line(self) -> str:
        pred = str(self.predicted_steps_to_target) if self.predicted_steps_to_target else "—"
        return (
            f"  {self.method_name:22s} | p={self.convergence_order:5.2f} "
            f"| λ={self.lyapunov_exponent:+.3f} "
            f"| {self.efficiency_bits_per_iter:5.2f} bits/iter "
            f"| 목표까지 {pred}단계 "
            f"| {self.stability}"
        )


@dataclass
class ConvergenceDynamicsReport:
    """수렴 동역학 전체 보고서."""
    target_name: str
    methods: List[MethodDynamics] = field(default_factory=list)
    best_method: str = ""
    dynamic_health: float = 0.0       # 0~1: irrational_algebra 연동용
    convergence_verdict: str = ""     # HEALTHY | STABLE | FRAGILE | CRITICAL

    def add_method(self, m: MethodDynamics) -> None:
        self.methods.append(m)
        self._update_summary()

    def _update_summary(self) -> None:
        if not self.methods:
            return
        best = max(self.methods, key=lambda m: m.efficiency_bits_per_iter)
        self.best_method = best.method_name

        stabilities = {m.stability for m in self.methods}
        diverging_count = sum(1 for m in self.methods if m.stability == "DIVERGING")

        max_eff = max(m.efficiency_bits_per_iter for m in self.methods)
        base = best.efficiency_bits_per_iter / max(max_eff, 1e-9)
        penalty = 0.4 * (diverging_count / len(self.methods))
        self.dynamic_health = max(0.0, min(1.0, base - penalty))

        if self.dynamic_health >= 0.85:
            self.convergence_verdict = "HEALTHY"
        elif self.dynamic_health >= 0.60:
            self.convergence_verdict = "STABLE"
        elif self.dynamic_health >= 0.35:
            self.convergence_verdict = "FRAGILE"
        else:
            self.convergence_verdict = "CRITICAL"

    def print_report(self) -> None:
        width = 90
        print(f"  대상: {self.target_name}")
        print(f"  {'방법':22s} | {'p':5s} | {'λ':7s} | {'효율':13s} | 예측 | 안정성")
        print("  " + "-" * width)
        for m in self.methods:
            print(m.summary_line())
        print(f"  최고 효율: {self.best_method}")
        print(f"  dynamic_health={self.dynamic_health:.3f}  [{self.convergence_verdict}]")
