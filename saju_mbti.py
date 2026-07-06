import sys
import argparse
import codecs
from sajupy import SajuCalculator

# Ensure UTF-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 1. Basic Saju constants and mappings (Keys are Chinese characters returned by sajupy)
STEMS = {
    '甲': {'element': '목', 'yin_yang': '양', 'kor': '갑'},
    '乙': {'element': '목', 'yin_yang': '음', 'kor': '을'},
    '丙': {'element': '화', 'yin_yang': '양', 'kor': '병'},
    '丁': {'element': '화', 'yin_yang': '음', 'kor': '정'},
    '戊': {'element': '토', 'yin_yang': '양', 'kor': '무'},
    '己': {'element': '토', 'yin_yang': '음', 'kor': '기'},
    '庚': {'element': '금', 'yin_yang': '양', 'kor': '경'},
    '辛': {'element': '금', 'yin_yang': '음', 'kor': '신'},
    '壬': {'element': '수', 'yin_yang': '양', 'kor': '임'},
    '癸': {'element': '수', 'yin_yang': '음', 'kor': '계'},
}

BRANCHES = {
    '子': {'element': '수', 'yin_yang': '양', 'kor': '자'},
    '丑': {'element': '토', 'yin_yang': '음', 'kor': '축'},
    '寅': {'element': '목', 'yin_yang': '양', 'kor': '인'},
    '卯': {'element': '목', 'yin_yang': '음', 'kor': '묘'},
    '辰': {'element': '토', 'yin_yang': '양', 'kor': '진'},
    '巳': {'element': '화', 'yin_yang': '음', 'kor': '사'},
    '午': {'element': '화', 'yin_yang': '양', 'kor': '오'},
    '未': {'element': '토', 'yin_yang': '음', 'kor': '미'},
    '申': {'element': '금', 'yin_yang': '양', 'kor': '신'},
    '酉': {'element': '금', 'yin_yang': '음', 'kor': '유'},
    '戌': {'element': '토', 'yin_yang': '양', 'kor': '술'},
    '亥': {'element': '수', 'yin_yang': '음', 'kor': '해'},
}

ELEMENT_RELATIONS = {
    '목': {'생': '화', '극': '토', '생함받음': '수', '극당함': '금'},
    '화': {'생': '토', '극': '금', '생함받음': '목', '극당함': '수'},
    '토': {'생': '금', '극': '수', '생함받음': '화', '극당함': '목'},
    '금': {'생': '수', '극': '목', '생함받음': '토', '극당함': '화'},
    '수': {'생': '목', '극': '화', '생함받음': '금', '극당함': '토'},
}

# Weights
POSITION_WEIGHTS = {
    '연주': 0.8,
    '월주': 1.5,
    '일주': 1.4,
    '시주': 1.1
}

TYPE_WEIGHTS = {
    '천간': 1.0,
    '지지': 1.2
}

def get_element_and_yin_yang(char):
    if char in STEMS:
        return STEMS[char]['element'], STEMS[char]['yin_yang']
    elif char in BRANCHES:
        return BRANCHES[char]['element'], BRANCHES[char]['yin_yang']
    return None, None

def get_kor_char(char):
    if char in STEMS:
        return STEMS[char]['kor']
    elif char in BRANCHES:
        return BRANCHES[char]['kor']
    return char

def get_sipsung(day_stem, target_char):
    day_elem, day_yy = get_element_and_yin_yang(day_stem)
    t_elem, t_yy = get_element_and_yin_yang(target_char)
    
    if not day_elem or not t_elem:
        return None
        
    # Same element
    if day_elem == t_elem:
        return '비견' if day_yy == t_yy else '겁재'
        
    # Day stem generates target (식상)
    if ELEMENT_RELATIONS[day_elem]['생'] == t_elem:
        return '식신' if day_yy == t_yy else '상관'
        
    # Day stem controls target (재성)
    if ELEMENT_RELATIONS[day_elem]['극'] == t_elem:
        return '편재' if day_yy == t_yy else '정재'
        
    # Target controls day stem (관성)
    if ELEMENT_RELATIONS[day_elem]['극당함'] == t_elem:
        return '편관' if day_yy == t_yy else '정관'
        
    # Target generates day stem (인성)
    if ELEMENT_RELATIONS[day_elem]['생함받음'] == t_elem:
        return '편인' if day_yy == t_yy else '정인'
        
    return None

def analyze_saju_mbti(year, month, day, hour, minute, city="Seoul", real_mbti=None):
    calculator = SajuCalculator()
    saju = calculator.calculate_saju(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city
    )
    
    # Extract pillars (stems and branches)
    # clean char function to extract only the valid Chinese Saju character
    def clean_char(raw_str, char_set):
        if not raw_str:
            return ""
        raw_str = raw_str.strip()
        for char in raw_str:
            if char in char_set:
                return char
        return raw_str[0] if raw_str else ""

    y_stem = clean_char(saju.get('year_stem', ''), STEMS)
    y_branch = clean_char(saju.get('year_branch', ''), BRANCHES)
    m_stem = clean_char(saju.get('month_stem', ''), STEMS)
    m_branch = clean_char(saju.get('month_branch', ''), BRANCHES)
    d_stem = clean_char(saju.get('day_stem', ''), STEMS)
    d_branch = clean_char(saju.get('day_branch', ''), BRANCHES)
    h_stem = clean_char(saju.get('hour_stem', ''), STEMS)
    h_branch = clean_char(saju.get('hour_branch', ''), BRANCHES)
    
    pillars = {
        '연주': {'천간': y_stem, '지지': y_branch},
        '월주': {'천간': m_stem, '지지': m_branch},
        '일주': {'천간': d_stem, '지지': d_branch},
        '시주': {'천간': h_stem, '지지': h_branch}
    }
    
    # 1. 오행 점수 계산
    element_scores = {'목': 0.0, '화': 0.0, '토': 0.0, '금': 0.0, '수': 0.0}
    for pillar_name, content in pillars.items():
        p_weight = POSITION_WEIGHTS[pillar_name]
        for type_name, char in content.items():
            t_weight = TYPE_WEIGHTS[type_name]
            elem, _ = get_element_and_yin_yang(char)
            if elem:
                element_scores[elem] += p_weight * t_weight
                
    # 2. 계절 보정
    # 월지 기준으로 특정 오행 강화
    season_element = None
    if m_branch in ['寅', '卯', '辰']:
        season_element = '목'
    elif m_branch in ['巳', '午', '未']:
        season_element = '화'
    elif m_branch in ['申', '酉', '戌']:
        season_element = '금'
    elif m_branch in ['亥', '子', '丑']:
        season_element = '수'
        
    if season_element:
        element_scores[season_element] *= 1.2
        
    # 3. 십성 점수 계산 (일간 기준)
    sipsung_scores = {
        '비견': 0.0, '겁재': 0.0, '식신': 0.0, '상관': 0.0, '편재': 0.0,
        '정재': 0.0, '편관': 0.0, '정관': 0.0, '편인': 0.0, '정인': 0.0
    }
    
    # Store sipsung for each position
    sipsung_map = {}
    for pillar_name, content in pillars.items():
        p_weight = POSITION_WEIGHTS[pillar_name]
        sipsung_map[pillar_name] = {}
        for type_name, char in content.items():
            t_weight = TYPE_WEIGHTS[type_name]
            # 일간 자체는 십성 계산에서 제외
            if pillar_name == '일주' and type_name == '천간':
                continue
            ss = get_sipsung(d_stem, char)
            if ss:
                sipsung_scores[ss] += p_weight * t_weight
                sipsung_map[pillar_name][type_name] = ss

    # 4. 음양 보정 계산
    yin_yang_counts = {'양': 0, '음': 0}
    for pillar_name, content in pillars.items():
        for type_name, char in content.items():
            _, yy = get_element_and_yin_yang(char)
            if yy in yin_yang_counts:
                yin_yang_counts[yy] += 1
                
    total_yy = yin_yang_counts['양'] + yin_yang_counts['음']
    yang_ratio = yin_yang_counts['양'] / total_yy if total_yy > 0 else 0
    yin_ratio = yin_yang_counts['음'] / total_yy if total_yy > 0 else 0
    
    yy_adjustment = {'E': 0, 'I': 0, 'P': 0, 'J': 0}
    if yang_ratio >= 0.60:
        yy_adjustment['E'] += 1
        yy_adjustment['P'] += 1
    elif yin_ratio >= 0.60:
        yy_adjustment['I'] += 1
        yy_adjustment['J'] += 1

    # 5. MBTI 네 축 점수 계산
    # E / I
    E_base = (
        element_scores['화'] * 2 +
        element_scores['목'] * 1 +
        sipsung_scores['겁재'] * 2 +
        sipsung_scores['식신'] * 1 +
        sipsung_scores['상관'] * 1 +
        sipsung_scores['편재'] * 2 +
        yy_adjustment['E']
    )
    # E 추가 보정: 월주/시간에 표현성 강한 글자가 있을 경우 보정 (+1)
    # 표현성 강한 글자: 상관, 식신, 편재, 겁재
    expressive_positions = [
        sipsung_map.get('월주', {}).get('천간'),
        sipsung_map.get('월주', {}).get('지지'),
        sipsung_map.get('시주', {}).get('천간'),
        sipsung_map.get('시주', {}).get('지지')
    ]
    if any(ss in ['상관', '식신', '편재', '겁재'] for ss in expressive_positions):
        E_base += 1
        
    I_base = (
        element_scores['수'] * 2 +
        element_scores['금'] * 1 +
        sipsung_scores['비견'] * 1 +
        sipsung_scores['정관'] * 1 +
        sipsung_scores['편인'] * 2 +
        sipsung_scores['정인'] * 1 +
        yy_adjustment['I']
    )
    # I 추가 보정: 일주/시주에 내면성 강한 글자가 있을 경우 보정 (+1)
    # 내면성 강한 글자: 편인, 정인, 비견, 정관
    reflective_positions = [
        sipsung_map.get('일주', {}).get('지지'),
        sipsung_map.get('시주', {}).get('천간'),
        sipsung_map.get('시주', {}).get('지지')
    ]
    if any(ss in ['편인', '정인', '비견', '정관'] for ss in reflective_positions):
        I_base += 1

    # S / N
    S_base = (
        element_scores['토'] * 2 +
        element_scores['금'] * 1 +
        sipsung_scores['식신'] * 1 +
        sipsung_scores['편재'] * 1 +
        sipsung_scores['정재'] * 2 +
        sipsung_scores['정관'] * 1 +
        sipsung_scores['편관'] * 1
    )
    # S 추가 보정: 현실적 십성이 월주에 강할 경우 보정 (+1)
    # 현실적 십성: 정재, 편재, 정관, 편관
    reality_monthly = [
        sipsung_map.get('월주', {}).get('천간'),
        sipsung_map.get('월주', {}).get('지지')
    ]
    if any(ss in ['정재', '편재', '정관', '편관'] for ss in reality_monthly):
        S_base += 1

    N_base = (
        element_scores['목'] * 2 +
        element_scores['수'] * 2 +
        element_scores['화'] * 1 +
        sipsung_scores['상관'] * 2 +
        sipsung_scores['편인'] * 2 +
        sipsung_scores['정인'] * 1
    )
    # N 추가 보정: 미래지향적/추상적 조합이 강할 경우 보정 (+1)
    # 조합 예: 월주/일주에 편인/상관이 있거나 수/목 점수가 높을 때
    abstract_positions = [
        sipsung_map.get('월주', {}).get('천간'),
        sipsung_map.get('월주', {}).get('지지'),
        sipsung_map.get('일주', {}).get('지지')
    ]
    if any(ss in ['편인', '상관'] for ss in abstract_positions) or (element_scores['목'] + element_scores['수'] > 5.0):
        N_base += 1

    # T / F
    T_base = (
        element_scores['금'] * 2 +
        element_scores['수'] * 1 +
        sipsung_scores['비견'] * 1 +
        sipsung_scores['겁재'] * 1 +
        sipsung_scores['상관'] * 1 +
        sipsung_scores['편재'] * 1 +
        sipsung_scores['정재'] * 1 +
        sipsung_scores['편관'] * 2 +
        sipsung_scores['정관'] * 1
    )
    # T 추가 보정: 금/수/관성이 강할 경우 보정 (+1)
    if (element_scores['금'] + element_scores['수'] > 5.0) or (sipsung_scores['편관'] + sipsung_scores['정관'] > 3.0):
        T_base += 1

    F_base = (
        element_scores['화'] * 2 +
        element_scores['목'] * 1 +
        element_scores['토'] * 1 +
        sipsung_scores['식신'] * 2 +
        sipsung_scores['정인'] * 1
    )
    # F 추가 보정: 목/화/식상이 강할 경우 또는 관계성 조화성 구조일 때 보정 (+1)
    if (element_scores['목'] + element_scores['화'] > 5.0) or (sipsung_scores['식신'] + sipsung_scores['상관'] > 3.0):
        F_base += 1

    # J / P
    J_base = (
        element_scores['토'] * 2 +
        element_scores['금'] * 2 +
        sipsung_scores['정재'] * 2 +
        sipsung_scores['정관'] * 2 +
        sipsung_scores['편관'] * 2 +
        sipsung_scores['정인'] * 1 +
        yy_adjustment['J']
    )
    # J 추가 보정: 월주에 관성/재성이 강할 경우 보정 (+1)
    if any(ss in ['정관', '편관', '정재', '편재'] for ss in reality_monthly):
        J_base += 1

    P_base = (
        element_scores['목'] * 1 +
        element_scores['화'] * 1 +
        element_scores['수'] * 1 +
        sipsung_scores['겁재'] * 2 +
        sipsung_scores['식신'] * 1 +
        sipsung_scores['상관'] * 2 +
        sipsung_scores['편재'] * 1 +
        sipsung_scores['편인'] * 1 +
        yy_adjustment['P']
    )
    # P 추가 보정: 식상/비겁/편인이 강할 경우 보정 (+1)
    if (sipsung_scores['식신'] + sipsung_scores['상관'] + sipsung_scores['비견'] + sipsung_scores['겁재'] + sipsung_scores['편인'] > 5.0):
        P_base += 1

    # Round scores
    scores = {
        'E': round(E_base, 2), 'I': round(I_base, 2),
        'S': round(S_base, 2), 'N': round(N_base, 2),
        'T': round(T_base, 2), 'F': round(F_base, 2),
        'J': round(J_base, 2), 'P': round(P_base, 2),
    }

    # Helper for Strength & Axis Determination
    def evaluate_axis(a_val, b_val, a_name, b_name):
        total = a_val + b_val
        if total == 0:
            return a_name, "동률", 0.0
            
        diff_ratio = abs(a_val - b_val) / total
        
        if diff_ratio <= 0.05:
            strength = "거의 동률"
        elif diff_ratio <= 0.10:
            strength = "약한 선호"
        elif diff_ratio <= 0.20:
            strength = "중간 선호"
        else:
            strength = "강한 선호"
            
        decision = a_name if a_val > b_val else (b_name if b_val > a_val else "X")
        return decision, strength, round(diff_ratio * 100, 1)

    axis_results = {}
    axis_results['E/I'] = evaluate_axis(scores['E'], scores['I'], 'E', 'I')
    axis_results['S/N'] = evaluate_axis(scores['S'], scores['N'], 'S', 'N')
    axis_results['T/F'] = evaluate_axis(scores['T'], scores['F'], 'T', 'F')
    axis_results['J/P'] = evaluate_axis(scores['J'], scores['P'], 'J', 'P')

    # Primary MBTI
    primary_mbti = (
        axis_results['E/I'][0] +
        axis_results['S/N'][0] +
        axis_results['T/F'][0] +
        axis_results['J/P'][0]
    )

    # Alternate possibilities for "거의 동률" or "약한 선호" axes
    alternatives = []
    # Identify flexible axes (diff <= 10%)
    flexible_axes = []
    for axis, (dec, strength, ratio) in axis_results.items():
        if strength in ["거의 동률", "약한 선호"]:
            flexible_axes.append(axis)

    def replace_char(mbti, axis_index, new_char):
        lst = list(mbti)
        lst[axis_index] = new_char
        return "".join(lst)

    mbti_options = [primary_mbti]
    
    # 2nd and 3rd choices construction
    axis_indices = {'E/I': 0, 'S/N': 1, 'T/F': 2, 'J/P': 3}
    
    # Sort flexible axes by smallest ratio
    flexible_axes_sorted = sorted(flexible_axes, key=lambda x: axis_results[x][2])
    
    for axis in flexible_axes_sorted:
        idx = axis_indices[axis]
        current_dec = primary_mbti[idx]
        opp_dec = axis[2] if current_dec == axis[0] else axis[0]
        alt_mbti = replace_char(primary_mbti, idx, opp_dec)
        if alt_mbti not in mbti_options:
            mbti_options.append(alt_mbti)
            
    # Fallback to make sure we have 3 options
    all_16_mbtis = [
        "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]
    
    while len(mbti_options) < 3:
        # Generate another variation from the next closest axis
        all_axes_sorted = sorted(axis_indices.keys(), key=lambda x: axis_results[x][2])
        added = False
        for axis in all_axes_sorted:
            idx = axis_indices[axis]
            current_dec = primary_mbti[idx]
            opp_dec = axis[2] if current_dec == axis[0] else axis[0]
            alt_mbti = replace_char(primary_mbti, idx, opp_dec)
            if alt_mbti not in mbti_options:
                mbti_options.append(alt_mbti)
                added = True
                break
        if not added:
            # Absolute fallback
            for m in all_16_mbtis:
                if m not in mbti_options:
                    mbti_options.append(m)
                    break

    # Determine strong / weak aspects
    strong_elements = [k for k, v in sorted(element_scores.items(), key=lambda x: x[1], reverse=True)[:2] if v > 0]
    weak_elements = [k for k, v in sorted(element_scores.items(), key=lambda x: x[1])[:2]]
    strong_sipsungs = [k for k, v in sorted(sipsung_scores.items(), key=lambda x: x[1], reverse=True)[:2] if v > 0]
    
    return {
        'pillars': pillars,
        'element_scores': element_scores,
        'sipsung_scores': sipsung_scores,
        'yin_yang_counts': yin_yang_counts,
        'yang_ratio': yang_ratio,
        'scores': scores,
        'axis_results': axis_results,
        'options': mbti_options[:3],
        'strong_elements': strong_elements,
        'weak_elements': weak_elements,
        'strong_sipsungs': strong_sipsungs,
        'real_mbti': real_mbti,
        'yy_adjustment': yy_adjustment
    }

def print_results(res):
    print("## 1. 사주 핵심 요약\n")
    print(f"* 강한 오행: {', '.join(res['strong_elements'])}")
    print(f"* 약한 오행: {', '.join(res['weak_elements'])}")
    print(f"* 강한 십성: {', '.join(res['strong_sipsungs'])}")
    
    # Pillar Korean Conversion for Display
    display_pillars = {}
    for name, content in res['pillars'].items():
        stem_kor = get_kor_char(content['천간'])
        branch_kor = get_kor_char(content['지지'])
        display_pillars[name] = f"{stem_kor}{branch_kor}"
        
    print(f"* 사주팔자 기둥: 연주({display_pillars['연주']}), 월주({display_pillars['월주']}), 일주({display_pillars['일주']}), 시주({display_pillars['시주']})")
    
    strong_elem = res['strong_elements'][0] if res['strong_elements'] else ""
    strong_ss = res['strong_sipsungs'][0] if res['strong_sipsungs'] else ""
    
    atmosphere = f"이 사주는 {strong_elem} 기운을 중심으로 강한 {strong_ss} 성향이 조화를 이루고 있어, "
    if strong_elem in ['목', '화']:
        atmosphere += "외향적 에너지의 발산과 유연하고 창의적인 관계 중심의 기질이 지배적인 성향을 보여줍니다."
    else:
        atmosphere += "내향적인 사고 성향과 논리적이고 구조화된 현실 지향적 기질이 강하게 드러나는 성향을 보여줍니다."
        
    print(f"* 사주의 전체 분위기: {atmosphere}")
    
    features = ""
    if '식신' in res['strong_sipsungs'] or '상관' in res['strong_sipsungs']:
        features = "창의적인 자기표현과 감각적인 즐거움, 자유로움을 선호하며 아이디어가 풍부한 기질"
    elif '정재' in res['strong_sipsungs'] or '정관' in res['strong_sipsungs']:
        features = "체계적이고 성실하며, 규칙과 책임감을 바탕으로 안정성을 고수하는 현실 지향적 기질"
    elif '편인' in res['strong_sipsungs'] or '정인' in res['strong_sipsungs']:
        features = "깊은 내면의 사색과 상상력, 보편적 가치보다 독창적 사유와 학구열을 추구하는 기질"
    elif '비견' in res['strong_sipsungs'] or '겁재' in res['strong_sipsungs']:
        features = "자기 주관이 매우 뚜렷하고 타인과의 비교 속에서도 자아 독립성을 수호하려는 기질"
    else:
        features = "외부 상황에 대단히 유연하고 기회를 날카롭게 잘 포착하는 실용적 기질"
        
    print(f"* 성격적으로 가장 두드러지는 특징: {features}\n")
    
    print("## 2. MBTI 축별 점수\n")
    print("| 축   | A 점수 | B 점수 | 판정     | 강도       |")
    print("| --- | ---: | ---: | ------ | -------- |")
    for axis in ['E/I', 'S/N', 'T/F', 'J/P']:
        dec, strength, ratio = res['axis_results'][axis]
        a_char, b_char = axis.split('/')
        a_score = res['scores'][a_char]
        b_score = res['scores'][b_char]
        print(f"| {axis} | {a_score} | {b_score} | {dec} | {strength} |")
    print()
    
    print("## 3. 최종 추정 MBTI\n")
    print(f"* 1순위: {res['options'][0]}")
    print(f"* 2순위: {res['options'][1]}")
    print(f"* 3순위: {res['options'][2]}")
    print()
    
    print("## 4. 왜 이 유형으로 판정했는가\n")
    print("오행, 십성, 위치, 음양 배치를 근거로 볼 때:")
    print(f"- **에너지 방향 (E/I)**: 수/금(내면) 대비 화/목(발산)의 총합과 십성의 표현성 글자 배치에 근거합니다.")
    print(f"- **정보 인식 (S/N)**: 토의 현실감 점수({res['element_scores']['토']:.2f}) 대비 목/수의 상상력 점수({res['element_scores']['목'] + res['element_scores']['수']:.2f})의 비중과 현실/미래지향 십성에 따릅니다.")
    print(f"- **판단 방식 (T/F)**: 금/수의 논리적 기질 점수와 관성의 규칙성 점수 대비 화/목의 조화와 식상의 감정적 공감 성향의 대조에 기인합니다.")
    print(f"- **생활 양식 (J/P)**: 토/금의 구조화 점수와 정관/정재의 안정성 지표 대비 식상/비겁/편인의 즉흥적 유연성 기질 총합에 근거합니다.")
    print(f"- **음양 비중**: 양 기운 비율 {res['yang_ratio']*100:.1f}% 대 음 기운 비율 {(1 - res['yang_ratio'])*100:.1f}%의 영향이 반영되었습니다.")
    print()
    
    if res['real_mbti']:
        real = res['real_mbti'].upper()
        est = res['options'][0]
        matching = []
        mismatching = []
        for i, char in enumerate(real):
            if char == est[i]:
                matching.append(char)
            else:
                mismatching.append(f"{real[i]}/{est[i]}")
                
        print("## 5. 실제 MBTI와 비교\n")
        print(f"* 실제 MBTI: {real}")
        print(f"* 사주 기반 추정 MBTI: {est}")
        print(f"* 일치한 축: {', '.join(matching) if matching else '없음'}")
        print(f"* 불일치한 축: {', '.join(mismatching) if mismatching else '없음'}")
        print(f"* 해석: 사주상의 고유 성향({est})과 스스로를 인식하는 자아 지도({real})의 비교를 통해, 환경과 후천적 학습이 성격 형성에 미친 영향을 유추해 볼 수 있습니다.")
        print(f"* 이 모델상 보완할 점: 환경적 영향력 및 직업적 보정 변수를 지장간 비율과 결합하여 세분화할 여지가 있습니다.\n")
        
    print("## 6. 주의점\n")
    print("“이 결과는 사주와 MBTI를 연결해보는 가설적 매핑 모델에 따른 추정이며, 과학적으로 확정된 성격 진단은 아니다. 다만 반복적인 데이터 검증을 통해 실제 MBTI와의 일치율을 확인하면 연구용 모델로 발전시킬 수 있다.”\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Saju to MBTI hypothetical mapping engine")
    parser.add_argument("--year", type=int, help="Birth year (solar)")
    parser.add_argument("--month", type=int, help="Birth month (solar)")
    parser.add_argument("--day", type=int, help="Birth day (solar)")
    parser.add_argument("--hour", type=int, help="Birth hour (24h format)")
    parser.add_argument("--minute", type=int, default=0, help="Birth minute")
    parser.add_argument("--city", type=str, default="Seoul", help="Birth city for solar time offset")
    parser.add_argument("--real-mbti", type=str, default=None, help="User's actual MBTI for comparison")
    
    args = parser.parse_args()
    
    # Interactive input if arguments are missing
    if not (args.year and args.month and args.day and args.hour is not None):
        print("사주-MBTI 변환 엔진 대화형 분석기")
        try:
            year = int(input("출생 연도(양력, 예: 1995): ").strip())
            month = int(input("출생 월(양력): ").strip())
            day = int(input("출생 일(양력): ").strip())
            hour = int(input("출생 시간(0~23): ").strip())
            minute = int(input("출생 분(0~59): ").strip())
            city = input("출생 도시 (기본값: Seoul): ").strip() or "Seoul"
            real_mbti = input("알고 있는 실제 MBTI (선택): ").strip() or None
        except ValueError:
            print("올바른 정수 값을 입력하세요.")
            sys.exit(1)
    else:
        year = args.year
        month = args.month
        day = args.day
        hour = args.hour
        minute = args.minute
        city = args.city
        real_mbti = args.real_mbti
        
    try:
        results = analyze_saju_mbti(year, month, day, hour, minute, city, real_mbti)
        print_results(results)
    except Exception as e:
        print("분석 중 에러가 발생했습니다:", e)
