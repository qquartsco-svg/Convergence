"""analyzer.py — 수렴 동역학 핵심 계산 함수

설계 원칙:
  순수 함수(pure functions) 집합 — 상태 없음, 부작용 없음.
  어떤 오차 수열(List[float])에도 직접 적용 가능.
  IrrationalApprox의 ConvergenceStep 외에 임의 float 수열도 받는다.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

from .models import ConvergenceDynamicsReport, MethodDynamics


# ── 저수준 계산 ──────────────────────────────────────────────────────────────

def convergence_order(errors: Sequence[float]) -> float:
    """수렴 차수 p 계산.

    |e_{n+1}| ~ C * |e_n|^p  →  p = log(e2/e1) / log(e1/e0)
    이론값: Newton=2.0, 연분수=1.0, Leibniz<1.0
    """
    orders = []
    for i in range(1, len(errors) - 1):
        e0, e1, e2 = errors[i - 1], errors[i], errors[i + 1]
        if e0 > 1e-15 and e1 > 1e-15 and e2 > 1e-15:
            try:
                p = math.log(e2 / e1) / math.log(e1 / e0)
                if 0.05 < p < 8.0:
                    orders.append(p)
            except (ValueError, ZeroDivisionError):
                pass
    return sum(orders) / len(orders) if orders else 1.0


def lyapunov_exponent(errors: Sequence[float]) -> float:
    """리야푸노프 지수 λ = 1/n * Σ log(|e_{k+1}| / |e_k|)

    λ < 0: 안정 수렴 (attractor)
    λ > 0: 발산 (chaotic / diverging)
    λ = 0: 중립
    """
    rates = []
    for i in range(len(errors) - 1):
        e_curr, e_next = errors[i], errors[i + 1]
        if e_curr > 1e-15 and e_next > 1e-15:
            try:
                rates.append(math.log(e_next / e_curr))
            except ValueError:
                pass
    return sum(rates) / len(rates) if rates else 0.0


def efficiency(errors: Sequence[float]) -> float:
    """효율 = 획득 정밀도(bits) / 반복 횟수

    Shannon 정보량 관점: 반복 1회가 몇 비트의 정보를 추가하는가?
    """
    if len(errors) < 2 or errors[-1] <= 0 or errors[0] <= 0:
        return 0.0
    bits_gained = math.log2(errors[0] / errors[-1])
    return bits_gained / len(errors)


def predict_steps(errors: Sequence[float],
                  target_error: float = 1e-12) -> Optional[int]:
    """목표 정밀도까지 남은 반복 횟수 예측.

    마지막 2개 오차로 감소율을 추정하고 등비급수 역산.
    """
    if len(errors) < 2:
        return None
    e1, e2 = errors[-2], errors[-1]
    if e2 <= target_error:
        return len(errors)
    if e1 <= 0 or e2 >= e1:
        return None
    rate = e2 / e1
    if rate <= 0 or rate >= 1.0:
        return None
    try:
        n_more = math.ceil(math.log(target_error / e2) / math.log(rate))
        return len(errors) + max(0, n_more)
    except (ValueError, ZeroDivisionError):
        return None


def stability_label(order: float, lya: float) -> str:
    if lya > 0.1:
        return "DIVERGING"
    if order >= 1.8:
        return "SUPERLINEAR"
    if order >= 0.9:
        return "LINEAR"
    return "SUBLINEAR"


# ── 공개 API ─────────────────────────────────────────────────────────────────

def analyze(history_or_errors, method_name: str = "",
            target_error: float = 1e-12) -> MethodDynamics:
    """수렴 이력 하나를 분석해 MethodDynamics 반환.

    Args:
        history_or_errors: IrrationalResult (history[] 포함) 또는
                           List[float] 오차 수열 직접 전달
        method_name:       표시용 레이블
        target_error:      예측 기준 목표 오차 (기본 1e-12)
    """
    # duck-typing: IrrationalResult면 history에서 error 추출
    if hasattr(history_or_errors, "history"):
        result = history_or_errors
        errors = [step.error for step in result.history]
        steps = len(result.history)
        final_error = result.final_error
        name = method_name or result.method.value
    else:
        errors = list(history_or_errors)
        steps = len(errors)
        final_error = errors[-1] if errors else 0.0
        name = method_name or "unknown"

    p = convergence_order(errors)
    lya = lyapunov_exponent(errors)
    eff = efficiency(errors)
    pred = predict_steps(errors, target_error)
    stab = stability_label(p, lya)

    return MethodDynamics(
        method_name=name,
        steps=steps,
        final_error=final_error,
        convergence_order=p,
        lyapunov_exponent=lya,
        efficiency_bits_per_iter=eff,
        predicted_steps_to_target=pred,
        stability=stab,
        target_error=target_error,
    )


def compare(target_name: str,
            results: Dict[str, object],
            target_error: float = 1e-12) -> ConvergenceDynamicsReport:
    """여러 방법을 비교한 동역학 보고서 생성.

    Args:
        target_name: "√2", "e", "φ", "Observer Ω" 등 표시용
        results:     {label: IrrationalResult 또는 List[float]} 딕셔너리
        target_error: 예측 기준 목표 오차
    """
    report = ConvergenceDynamicsReport(target_name=target_name)
    for label, data in results.items():
        dynamics = analyze(data, method_name=label, target_error=target_error)
        report.add_method(dynamics)
    return report


def health_from_dynamics(dynamics: MethodDynamics) -> float:
    """동역학 지표 → 건강도 스코어 (0~1).

    irrational_algebra의 structural_health에 dynamic_health로 전달.
    KEMET 수치 안정성 진단에 직접 활용 가능.
    """
    base = {
        "SUPERLINEAR": 0.95,
        "LINEAR":      0.70,
        "SUBLINEAR":   0.40,
        "DIVERGING":   0.05,
    }.get(dynamics.stability, 0.50)

    lya_bonus = min(0.05, max(-0.15, -dynamics.lyapunov_exponent * 0.015))
    eff_bonus  = min(0.05, dynamics.efficiency_bits_per_iter * 0.004)

    return max(0.0, min(1.0, base + lya_bonus + eff_bonus))
