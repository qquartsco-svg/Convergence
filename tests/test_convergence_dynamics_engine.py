from __future__ import annotations

import sys
from pathlib import Path


SPATIAL_LAYER = Path(__file__).resolve().parents[2]
if str(SPATIAL_LAYER) not in sys.path:
    sys.path.insert(0, str(SPATIAL_LAYER))

from ConvergenceDynamics_Engine import ConvergenceDynamicsEngine
from ConvergenceDynamics_Engine.analyzer import (
    analyze,
    convergence_order,
    health_from_dynamics,
    lyapunov_exponent,
)


def test_convergence_order_detects_quadratic_behavior() -> None:
    errors = [1e-1, 1e-2, 1e-4, 1e-8]
    order = convergence_order(errors)
    assert 1.9 <= order <= 2.1


def test_lyapunov_is_negative_for_stable_decay() -> None:
    errors = [1.0, 0.5, 0.25, 0.125, 0.0625]
    lya = lyapunov_exponent(errors)
    assert lya < 0.0


def test_analyze_labels_linear_series_and_predicts_total_steps() -> None:
    errors = [1.0, 0.5, 0.25, 0.125, 0.0625]
    dynamics = analyze(errors, method_name="geometric", target_error=1e-3)
    assert dynamics.method_name == "geometric"
    assert dynamics.stability == "LINEAR"
    assert dynamics.predicted_steps_to_target is not None
    assert dynamics.predicted_steps_to_target > len(errors)


def test_health_prefers_superlinear_over_sublinear() -> None:
    superlinear = analyze([1e-1, 1e-2, 1e-4, 1e-8], method_name="newton-like")
    sublinear = analyze([1.0, 0.7, 0.55, 0.47, 0.41], method_name="slow-like")
    assert health_from_dynamics(superlinear) > health_from_dynamics(sublinear)


def test_kemet_stability_check_reports_safe_for_strong_decay() -> None:
    engine = ConvergenceDynamicsEngine(target_error=1e-9)
    verdict = engine.kemet_stability_check([1e-1, 1e-2, 1e-4, 1e-8], label="KEMET")
    assert verdict["stable"] is True
    assert verdict["stability"] == "SUPERLINEAR"
    assert verdict["verdict"] == "SAFE"
