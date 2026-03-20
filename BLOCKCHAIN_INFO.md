# ConvergenceDynamics_Engine Blockchain Info

## Role

이 레포는 `ConvergenceDynamics_Engine`의 공식 독립 배포판입니다.
목표는 수렴 과정 동역학 판정 엔진을 단독 설치·실행 가능한 패키지로 제공하는 것입니다.

## Scope

- 포함:
  - `ConvergenceDynamics_Engine` 패키지
  - 독립 테스트
  - 독립 문서
  - 릴리스 시점 SHA-256 매니페스트
- 제외:
  - 상위 레이어 통합 로직
  - 외부 엔진의 내부 구현 코드

## PHAM

PHAM (Proof of Authorship & Merit)은
이 엔진의 provenance, 기여도, 릴리스 시점 무결성 추적을 위한 서명 계층입니다.

## Contribution Rule

- GNJz(Qquarts)의 기여도는 이 엔진에서 블록체인 검증 기준 최대 **6%**를 넘지 않는 자발적 상한을 따릅니다.
- GNJz(Qquarts)는 그 어떤 상황에서도 자신의 기여도를 **6%를 넘기지 않는다**.
- 이 6% 원칙은 GNJz(Qquarts)에게만 적용되며, 다른 기여자나 저장소 전체 소유 구조를 재정의하지 않습니다.
- 상용화, 재배포, 파생 사용 여부와 관계없이 같은 원칙을 유지합니다.

## Integrity Surface

- `__init__.py`
- `ConvergenceDynamics_Engine/__init__.py`
- `ConvergenceDynamics_Engine/analyzer.py`
- `ConvergenceDynamics_Engine/engine.py`
- `ConvergenceDynamics_Engine/models.py`
- `README.md`
- `BLOCKCHAIN_INFO.md`
- `PHAM_BLOCKCHAIN_LOG.md`
- `SIGNATURE.sha256`
- `pyproject.toml`
- `tests/test_convergence_dynamics_engine.py`

## Signature Policy

- Signature mode: SHA-256 content manifest
- Manifest file: `SIGNATURE.sha256`
- Verification command:

```bash
shasum -a 256 -c SIGNATURE.sha256
```
