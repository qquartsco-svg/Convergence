"""Compatibility shim for the standalone Convergence repo.

Canonical package exports now live under `ConvergenceDynamics_Engine/`.
This root module remains only as a thin compatibility layer.
"""

from ConvergenceDynamics_Engine import *  # noqa: F401,F403
