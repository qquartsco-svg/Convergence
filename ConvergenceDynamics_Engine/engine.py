"""engine.py — ConvergenceDynamicsEngine 클래스

역할:
  수렴 과정(history[])을 받아 동역학 지표를 계산하고
  시스템 건강도로 연결하는 독립 엔진.

  어떤 수렴 과정도 분석 가능:
    - IrrationalApprox_Engine의 무리수 수렴 이력
    - Observer 시스템의 Ω 시계열
    - KEMET 수치 적분 오차 수열
    - AlgebraApprox_Engine의 Taylor 급수 잔차
"""
from __future__ import annotations

from typing import Dict, List, Optional, Union

from .analyzer import analyze, compare, health_from_dynamics
from .models import ConvergenceDynamicsReport, MethodDynamics


class ConvergenceDynamicsEngine:
    """수렴 과정 동역학 분석 엔진.

    Usage:
        engine = ConvergenceDynamicsEngine()

        # 1) IrrationalApprox 결과 직접 분석
        dynamics = engine.analyze(irrational_result)

        # 2) 여러 방법 비교
        report = engine.compare("√2", {"Newton": r1, "연분수": r2})

        # 3) 순수 오차 수열 분석 (Observer Ω, KEMET 등)
        omega_errors = [abs(0.9 - o) for o in omega_history]
        dynamics = engine.analyze(omega_errors, method_name="Observer-Ω")

        # 4) irrational_algebra 연동용 health 스코어
        dh = engine.health(dynamics)
    """

    def __init__(self, target_error: float = 1e-12):
        self.target_error = target_error

    def analyze(self,
                history_or_errors: Union[object, List[float]],
                method_name: str = "") -> MethodDynamics:
        """수렴 이력 하나를 분석.

        Args:
            history_or_errors: IrrationalResult 또는 List[float] 오차 수열
            method_name:       표시용 레이블
        """
        return analyze(history_or_errors, method_name, self.target_error)

    def compare(self,
                target_name: str,
                results: Dict[str, object]) -> ConvergenceDynamicsReport:
        """여러 방법을 비교한 동역학 보고서 생성."""
        return compare(target_name, results, self.target_error)

    def health(self, dynamics: MethodDynamics) -> float:
        """동역학 지표 → 건강도 스코어 (0~1).

        irrational_algebra.analyze(dynamic_health=...) 에 직접 전달 가능.
        """
        return health_from_dynamics(dynamics)

    def diagnose(self, target_name: str,
                 results: Dict[str, object]) -> None:
        """보고서를 생성하고 콘솔 출력."""
        report = self.compare(target_name, results)
        print(f"\n{'='*65}")
        print(f"  ConvergenceDynamics_Engine  —  {target_name}")
        print(f"{'='*65}")
        report.print_report()
        print()

    def kemet_stability_check(self,
                               error_series: List[float],
                               label: str = "KEMET") -> dict:
        """KEMET 수치 안정성 진단용 단일 호출 인터페이스.

        Args:
            error_series: 수치 오차 시계열 (내림차순 기대)
            label:        진단 레이블

        Returns:
            {"stable": bool, "lyapunov": float, "stability": str,
             "dynamic_health": float, "verdict": str}
        """
        d = self.analyze(error_series, method_name=label)
        dh = self.health(d)
        stable = d.stability != "DIVERGING"
        if stable and dh >= 0.7:
            verdict = "SAFE"
        elif stable and dh >= 0.4:
            verdict = "CAUTION"
        elif (not stable) and dh >= 0.2:
            verdict = "WARNING"
        else:
            verdict = "CRITICAL"
        return {
            "stable":         stable,
            "lyapunov":       d.lyapunov_exponent,
            "convergence_order": d.convergence_order,
            "stability":      d.stability,
            "dynamic_health": dh,
            "verdict":        verdict,
        }
