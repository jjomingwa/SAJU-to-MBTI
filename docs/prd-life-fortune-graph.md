# PRD: 사주 기반 나이별 인생 운 그래프 및 상세 분석 설명 기능

사주의 음양오행 및 십성 흐름(대운)을 기반으로 연령별 인생 운의 흐름과 성향 변화를 시각적으로 보여주는 그래프 기능 및 그 결과의 도출 원리를 명리학적으로 설명하는 상세 분석 란을 제공합니다.

---

## Problem Statement

현재 SAJU-to-MBTI 서비스는 사용자의 사주 원국 분석 결과와 이를 기반으로 추정한 MBTI 유형을 제공하고 있습니다. 하지만 사용자는 타고난 사주 원판뿐만 아니라, **시간의 흐름에 따라 변화하는 인생의 운 흐름(대운/세운)**과 **각 시기별 운세의 길흉화복 분석** 및 **성향적 변화**를 알고 싶어 합니다. 
기존 텍스트 위주의 단순 정보로는 연령대별 운의 기복과 성향 변화를 한눈에 파악하기 어려우며, 특정 점수가 산출된 근거(왜 이렇게 나왔는지)에 대한 깊이 있는 명리학적 설명이 부족하여 사용자의 흥미와 신뢰도를 높이는 데 한계가 있습니다.

---

## Solution

사용자의 생년월일시와 **성별**(대운 방향 결정에 필수)을 입력받아, **나이별 인생 운세 점수(Fortune Score)** 및 **성향 변화(Dynamic MBTI Shift)**를 시각적 그래프(Line/Area Chart)로 제공합니다.
또한, 그래프 하단에 **"상세 명리학적 해석 보기 (왜 이렇게 나왔나요?)"** 버튼을 배치하여, 클릭 시 용신/희신 분석, 대운별 십성/오행의 작용 원리, 각 연령대별 구체적인 삶의 가이드를 설명하는 상세 분석 보고서 영역을 활성화합니다.

---

## User Stories

1. As a user, I want to select my biological gender on the input form, so that my Saju Daeun (대운) calculation direction (forward/backward) can be accurately determined.
2. As a user, I want to see my life fortune score (0-100) plotted as a line/area graph by age (1 to 90+), so that I can easily spot the peaks and troughs of my life's journey at a glance.
3. As a user, I want to see the dynamic shift of my MBTI strength percentages across different ages on the chart, so that I can visualize how my personality might evolve under different environmental energies (Daeun).
4. As a user, I want to hover over the graph points, so that I can see a tooltip showing the specific age, corresponding Daeun pillars (대운 간지), and a brief fortune summary of that decade.
5. As a user, I want to toggle a detailed explanation panel via a button, so that the interface remains clean by default while allowing me to dive deep into the analysis when needed.
6. As a user, I want to see my Yongsin (용신 - helper element), Huisin (희신 - favorable element), and Gisin (기신 - opposing element) clearly identified, so that I understand which elemental energies are beneficial or challenging for me.
7. As a user, I want a structured breakdown of each 10-year Daeun cycle explaining the interaction of the cycle's stems/branches with my birth chart, so that I can understand the underlying astrological reasons for my fortune scores.
8. As a developer, I want a decoupled fortune simulation engine that calculates Daeun ages, pillars, and fortune scores separately from the MBTI mapping, so that the code is easily testable and maintainable.

---

## Implementation Decisions

### 1. New/Modified Modules & Interfaces

- **Backend Logic (`saju_fortune_engine.py`) [NEW]**:
  - **Daeun Calculator**:
    - Calculates the Daeun starting age (대운수). Calculates the day difference between the birth date and the adjacent solar terms (next term for forward progression, previous term for backward progression), divided by 3, rounded to the nearest integer.
    - Determines progression direction: Forward if (Yang Year-Male or Yin Year-Female), backward if (Yang Year-Female or Yin Year-Male).
    - Generates 10-year Daeun pillars (대운 간지) starting from the Month Pillar.
  - **Yongsin/Huisin Finder**:
    - Analyzes the birth chart's element strengths to determine the overall state (strong/weak/balanced).
    - Selects the Yongsin (용신 - balancer element), Huisin (희신 - helper element), and Gisin (기신 - opposing element) based on classical Saju rules (억부법/조후법).
  - **Fortune Simulator**:
    - Generates an array of yearly or decadal fortune scores (0 to 100).
    - Score calculation formula: Base score (50) + (Daeun stem/branch element value * Yongsin/Huisin weight) - (Daeun stem/branch element value * Gisin weight).
    - Simulates dynamic MBTI shifts: Favorable or active elements in Daeun modify the baseline MBTI scores (e.g., Fire Daeun boosts Extraversion (E) and Feeling (F) scores).

- **API Layer (`app.py`) [MODIFY]**:
  - Update `/api/analyze` request schema to accept `gender` (`male` / `female`).
  - Integrate `saju_fortune_engine.py` to generate the life fortune graph data and explanation text.
  - Append the following fields to the response JSON:
    - `fortune_scores`: List of `{"age": int, "score": float, "pillar": string, "primary_element": string}`
    - `yongsin_info`: `{"yongsin": string, "huisin": string, "gisin": string, "reason": string}`
    - `daeun_analysis`: List of `{"age_range": string, "pillar": string, "score": float, "mbti_shift": string, "desc": string}`

- **Frontend User Interface (`templates/index.html`) [MODIFY]**:
  - Add "Gender (성별)" selector (남성/여성) to the input form.
  - Include Chart.js via CDN (`https://cdn.jsdelivr.net/npm/chart.js`) in the `<head>`.
  - Add a "인생 운 흐름 & 성향 변화 그래프" section in the results card.
  - Render a dual-axis or split chart showing:
    1. Life Fortune Score (Line/Area)
    2. Dynamic MBTI trait shifts (stacked or small lines for E/I, S/N, etc.)
  - Add a button: "상세 분석 설명 보기 (왜 이렇게 나왔나요?)" which toggles a modal or expands an accordion block.
  - Display the structured explanations (Yongsin/Huisin analysis, Daeun cycle interpretations) in the toggled area.

---

## Testing Decisions

### 1. External Behavior Testing
- Verify that the Daeun calculation returns correct starting ages and direction progressions for various sample dates (e.g., standard male, standard female, leap month births).
- Verify that the `/api/analyze` API validates the presence of the `gender` field and returns a 400 Bad Request error if missing or invalid.
- Ensure the simulated fortune scores remain strictly within the range $[0, 100]$.
- Ensure that the dynamic MBTI shift does not result in invalid MBTI strings (e.g. always resolves to valid E/I, S/N, T/F, J/P).

### 2. Prior Art
- Refer to `test_engine.py` for testing basic Saju-to-MBTI calculations using `unittest` or direct execution. A new test suite `test_fortune.py` will be created to validate the fortune engine.

---

## Out of Scope

- Daily or monthly fortune tracking (일진/월운) which requires continuous calendar sync and is outside the scope of life-long overview.
- Fetal/Conception-time correction (수태월 계산).
- User authentication and persistent database storage for saving past analysis charts (this remains stateless like the rest of the application).

---

## Further Notes

- **Aesthetic standard**: The graph must match the existing modern glassmorphism dark mode theme, using custom color maps for the elements (Wood: Green, Fire: Red, Earth: Yellow, Metal: Silver/White, Water: Blue) to maintain visual harmony.
