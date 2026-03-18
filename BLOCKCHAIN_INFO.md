# 🔗 PHAM 블록체인 서명 정보 — ConvergenceDynamics_Engine

## 📋 개요

**엔진**: ConvergenceDynamics_Engine  
**레이어**: 40_SPATIAL_LAYER  
**역할**: 수렴 과정 동역학 판정기

이 엔진은 `IrrationalApprox_Engine`이 생성한 `history[]` 또는 임의의 오차 수열을 받아
수렴 차수, Lyapunov 지수, 효율, 목표 단계 예측을 계산하는 **독립 PHAM 서명 엔진**입니다.

---

## 🏛️ 엔진 구성

```
ConvergenceDynamics_Engine/
├── __init__.py                   — 공개 API
├── analyzer.py                   — 순수 수렴 동역학 계산 함수
├── engine.py                     — ConvergenceDynamicsEngine 메인 클래스
├── models.py                     — MethodDynamics, ConvergenceDynamicsReport
├── tests/
│   └── test_convergence_dynamics_engine.py
├── README.md
├── BLOCKCHAIN_INFO.md
└── PHAM_BLOCKCHAIN_LOG.md
```

---

## 🔐 PHAM 서명 원칙

| 항목 | 내용 |
|------|------|
| **라이선스** | MIT License |
| **기여도 상한** | GNJz(Qquarts) 자발적 기여도 제한 — 블록체인 기반 최대 6% |
| **검증 방법** | 블록체인으로 기여도·출처 영구 기록 및 검증 가능 |
| **사용 제한** | 없음 (MIT) |

---

## 🔄 3엔진 구조 내 위치

| 엔진 | 역할 |
|------|------|
| `IrrationalApprox_Engine` | 수렴 생성기 |
| `ConvergenceDynamics_Engine` | 수렴 판정기 |
| `irrational_algebra` | 구조 해석기 |

이 엔진은 계산기 자체가 아니라, 계산 과정이 안정적으로 수렴하는지 판정하는 보조 엔진입니다.

---

## 🧪 검증 상태

| 항목 | 값 |
|------|----|
| 테스트 파일 | `tests/test_convergence_dynamics_engine.py` |
| 테스트 수 | 5 |
| 검증 범위 | 수렴 차수, Lyapunov 부호, 선형 수렴 판정, health 점수, KEMET 안정성 진단 |

---

**작성일**: 2026-03-18  
**버전**: 1.0.1  
**작성자**: GNJz (Qquarts)
