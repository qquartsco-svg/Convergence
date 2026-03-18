# Convergence

**수렴 과정 동역학 분석 엔진**

> "수렴은 목적지가 아니라 방향이다.  
> 수열이 그 값을 향해 계속 가까워지고 있다면, 그것이 수렴이다."  
> — Feynman

---

## 정체성

이 엔진은 계산기가 아니다.

| 구분 | 설명 |
|---|---|
| **계산기** | √2, e, φ, π 값을 구한다 |
| **근사기** | 이항 근사, Taylor 급수로 함수를 전개한다 |
| **→ 이 엔진** | 근사 과정(history)의 수렴 동역학 자체를 판정한다 |

대상은 무리수가 아니라 **수렴 과정**이다.

---

## 핵심 수식

### 1. 수렴 차수 (Convergence Order) — $p$

$$p = \frac{\log\left(\dfrac{e_{n+1}}{e_n}\right)}{\log\left(\dfrac{e_n}{e_{n-1}}\right)}$$

- $e_n = |x_n - x^*|$ : $n$번째 단계의 오차
- $p = 2$ : 이차 수렴 (Newton-Raphson) — 매 단계 유효 자릿수 2배
- $p = 1$ : 선형 수렴 (연분수, 피보나치)
- $p < 1$ : 준선형 (Leibniz 급수) — 사실상 비효율

### 2. 리야푸노프 지수 (Lyapunov Exponent) — $\lambda$

$$\lambda = \lim_{n \to \infty} \frac{1}{n} \sum_{k=0}^{n-1} \log\left|\frac{e_{k+1}}{e_k}\right|$$

- $\lambda < 0$ : 안정 수렴 — 끌개(attractor)가 존재함
- $\lambda > 0$ : 발산 — 카오스, 수치 불안정
- $\lambda = 0$ : 중립 — 수렴/발산 경계

시스템이 끌개를 가지고 있다는 것의 증거가 $\lambda < 0$ 이다.

### 3. 정밀도 효율 (Efficiency) — $\eta$

$$\eta = \frac{\log_2\!\left(\dfrac{e_0}{e_n}\right)}{n} \quad \text{[bits/iteration]}$$

- 반복 1회가 몇 비트의 정밀도를 더하는가
- Newton(√2): $\eta \approx 8.08$ bits/iter
- 연분수: $\eta \approx 2.36$ bits/iter
- Leibniz(π): $\eta \approx 0.65$ bits/iter

### 4. 목표 도달 예상 총 단계 수 (Predicted Total Steps) — $\hat{n}$

마지막 두 오차로 감소율 $r = e_n / e_{n-1}$ 를 추정하면:

$$\hat{n} = n + \left\lceil \frac{\log(e^* / e_n)}{\log r} \right\rceil$$

- $e^*$ : 목표 오차 (기본값 $10^{-12}$)
- $\hat{n}$ 은 **현재까지 진행한 단계를 포함한 총 단계 수** (남은 단계 수가 아님)
- Leibniz(π): $\hat{n} \approx 9842$ (현재 500단계 진행 시 약 9342단계 더 필요)
- Newton(√2): $\hat{n} \approx 6$ (6단계 시점에서 이미 도달)

### 5. 동역학 건강도 (Dynamic Health) — $H_d$

$$H_d = \text{clip}\!\left(H_\text{base}(p,\,\lambda) + \Delta_\lambda + \Delta_\eta,\; 0,\; 1\right)$$

$$H_\text{base} = \begin{cases} 0.95 & p \geq 1.8 \;\text{(SUPERLINEAR)} \\ 0.70 & 0.9 \leq p < 1.8 \;\text{(LINEAR)} \\ 0.40 & p < 0.9 \;\text{(SUBLINEAR)} \\ 0.05 & \lambda > 0.1 \;\text{(DIVERGING)} \end{cases}$$

$$\Delta_\lambda = \text{clip}(-0.015\,\lambda,\,-0.15,\,+0.05)$$

이 $H_d$ 는 `irrational_algebra` 엔진의 `structural_health` 에 15% 가중치로 반영된다.

---

## 안정성 분류

| 분류 | 조건 | 의미 |
|---|---|---|
| `SUPERLINEAR` | $p \geq 1.8$ | Newton급 — 매 단계 자릿수 폭발적 증가 |
| `LINEAR` | $0.9 \leq p < 1.8$ | 안정적 선형 수렴 |
| `SUBLINEAR` | $p < 0.9$ | 수렴은 하나 비효율 |
| `DIVERGING` | $\lambda > 0.1$ | 수렴 실패 — 시스템 경고 |

---

## 3엔진 구조 내 위치

```
IrrationalApprox_Engine       →  계산기  (무리수 수렴 생성, history[] 출력)
          │
          │  history[] = [e₀, e₁, e₂, ...]
          ▼
Convergence                   →  판정기  (수렴 동역학 분석)  ← 여기
          │
          │  dynamic_health ∈ [0, 1]
          ▼
irrational_algebra             →  해석기  (상태 구조 분석, structural_health)
```

---

## 활용

```python
from convergence import ConvergenceDynamicsEngine

engine = ConvergenceDynamicsEngine()
```

**입력 모드 1 — IrrationalResult 직접 전달**  
`IrrationalApprox_Engine`이 반환한 결과 객체를 그대로 넘긴다.  
내부에서 `result.history[].error` 를 자동 추출한다.

```python
# IrrationalApprox_Engine 연동
from IrrationalApprox_Engine import IrrationalApproxEngine
irr = IrrationalApproxEngine()
result = irr.sqrt(2)                              # IrrationalResult 반환

engine.diagnose("√2", {"Newton": result})
```

**입력 모드 2 — 순수 오차 수열 `List[float]`**  
무리수와 무관한 어떤 오차 시계열도 분석 가능하다.

```python
# Observer Ω 수렴 분석
omega_history = [0.50, 0.61, 0.70, 0.76, 0.80, 0.83, 0.86]
omega_errors = [abs(1.0 - o) for o in omega_history]
d = engine.analyze(omega_errors, method_name="Observer-Ω")

# KEMET 수치 안정성 진단
status = engine.kemet_stability_check(kemet_error_series)
# → {"verdict": "SAFE" | "CAUTION" | "WARNING" | "CRITICAL", ...}
```

**irrational_algebra 연동**

```python
# 실제 경로: cognitive_kernel.engines.irrational_algebra
import sys
sys.path.insert(0, "/path/to/Core/Cognitive_Kernel/src")
from cognitive_kernel.engines.irrational_algebra.irrational_algebra_engine import IrrationalAlgebraEngine

dh = engine.health(d)   # 0~1
algebra = IrrationalAlgebraEngine()
snapshot = algebra.analyze(state_vector, dynamic_health=dh)
print(snapshot.structural_health)
```

---

## 파일 구조

```
Convergence/
├── engine.py     — ConvergenceDynamicsEngine (메인 클래스)
├── analyzer.py   — convergence_order, lyapunov_exponent, efficiency, predict_steps
├── models.py     — MethodDynamics, ConvergenceDynamicsReport
└── __init__.py   — 공개 API
```

---

## 실측 결과

| 방법 | $p$ | $\lambda$ | $\eta$ (bits/iter) | 안정성 |
|---|---|---|---|---|
| Newton (√2) | 1.99 | -8.24 | 8.08 | SUPERLINEAR |
| 연분수 (√2) | 1.00 | -1.77 | 2.36 | LINEAR |
| 급수 $\sum 1/k!$ (e) | 1.09 | -2.14 | 2.59 | LINEAR |
| 극한 $(1+1/n)^n$ (e) | 1.03 | -0.69 | 0.95 | LINEAR |
| 피보나치 (φ) | 1.06 | -0.95 | 1.31 | LINEAR |
| Leibniz 급수 (π) | 0.82 | -0.47 | 0.65 | SUBLINEAR |

Newton이 8.08 bits/iter인 것에 비해 Leibniz는 0.65.  
같은 정밀도를 얻는 데 약 **12배** 더 많은 반복이 필요하다.

---

## 의존성

```
Python >= 3.10
표준 라이브러리만 사용 (math, dataclasses, typing)
외부 패키지 없음
```
