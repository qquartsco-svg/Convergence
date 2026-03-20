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
    predicted_steps_to_target: Optional[int]  # 목표 정밀도 도달 예상 총 단계 수
    stability: str                    # SUPERLINEAR | LINEAR | SUBLINEAR | DIVERGING
    target_error: float = 1e-12      # 예측 기준 오차

    def summary_line(self) -> str:
        # None이면 예측 불가 표시 — 0은 유효한 값이므로 is None으로만 구분
        pred = "—" if self.predicted_steps_to_target is None else str(self.predicted_steps_to_target)
        return (
            f"  {self.method_name:22s} | p={self.convergence_order:5.2f} "
            f"| λ={self.lyapunov_exponent:+.3f} "
            f"| {self.efficiency_bits_per_iter:5.2f} bits/iter "
            f"| 총 {pred}단계 예측 "
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
        n = len(self.methods)

        # 발산 비율 패널티
        diverging_ratio = sum(1 for m in self.methods if m.stability == "DIVERGING") / n

        # 평균 수렴 차수 점수 (p=2가 이상적 → 정규화)
        avg_order = sum(m.convergence_order for m in self.methods) / n
        order_score = min(1.0, avg_order / 2.0)

        # 평균 리야푸노프 점수 (λ=-5 이하면 1.0, 0 이상이면 0.0)
        avg_lya = sum(m.lyapunov_exponent for m in self.methods) / n
        lya_score = max(0.0, min(1.0, -avg_lya / 5.0))

        # 최고 효율 방법의 bits/iter 점수 (10 bits/iter를 기준 상한으로)
        eff_score = min(1.0, best.efficiency_bits_per_iter / 10.0)

        # 종합: 효율 40% + 수렴차수 30% + 리야푸노프 30% — 발산 패널티
        base = 0.40 * eff_score + 0.30 * order_score + 0.30 * lya_score
        self.dynamic_health = max(0.0, min(1.0, base - 0.5 * diverging_ratio))

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
