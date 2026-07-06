import math
from datetime import datetime, timedelta
import pandas as pd
from saju_mbti import STEMS, BRANCHES, ELEMENT_RELATIONS, get_element_and_yin_yang, get_kor_char

# Stems and Branches order for progression
STEMS_ORDER = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
BRANCHES_ORDER = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# Monthly solar terms (Jeolgi) that mark the start of each month
MONTHLY_TERMS = ['입춘', '경칩', '청명', '입하', '망종', '소서', '입추', '백로', '한로', '입동', '대설', '소한']

def calculate_daeun_info(year, month, day, hour, minute, gender, calculator):
    """
    Calculates Daeun starting age (대운수) and the 10-year Daeun pillars.
    """
    saju = calculator.calculate_saju(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute
    )
    
    y_stem = saju.get('year_stem')
    m_stem = saju.get('month_stem')
    m_branch = saju.get('month_branch')
    
    # Check if year stem is Yang
    is_yang_year = y_stem in ['甲', '丙', '戊', '庚', '壬']
    is_male = (gender == 'male')
    
    # Determine progression direction
    # Yang-Male or Yin-Female: Forward (순행)
    # Yang-Female or Yin-Male: Backward (역행)
    if (is_yang_year and is_male) or (not is_yang_year and not is_male):
        direction = 'forward'
    else:
        direction = 'backward'
        
    # Find monthly solar terms around the birth date
    df = calculator.data[calculator.data['solar_term_korean'].isin(MONTHLY_TERMS)].copy()
    
    def parse_term_time(val):
        if pd.isna(val):
            return None
        try:
            s = str(int(float(val)))
            return datetime.strptime(s, "%Y%m%d%H%M")
        except Exception:
            return None
            
    df['dt'] = df['term_time'].apply(parse_term_time)
    df = df[df['dt'].notnull()].sort_values('dt')
    
    birth_dt = datetime(year, month, day, hour, minute)
    
    term_row = None
    if direction == 'forward':
        # First monthly term after birth
        after = df[df['dt'] >= birth_dt]
        if not after.empty:
            term_row = after.iloc[0]
        else:
            term_row = df.iloc[0] # Fallback
    else:
        # Last monthly term before birth
        before = df[df['dt'] <= birth_dt]
        if not before.empty:
            term_row = before.iloc[-1]
        else:
            term_row = df.iloc[-1] # Fallback
            
    term_dt = term_row['dt']
    time_diff = abs(term_dt - birth_dt)
    days_diff = time_diff.total_seconds() / (24.0 * 3600.0)
    
    # Daeun starting age is round(days_diff / 3)
    daeun_su = round(days_diff / 3.0)
    daeun_su = max(1, min(10, daeun_su)) # clamp between 1 and 10
    
    # Generate 10-year Daeun pillars
    m_stem_idx = STEMS_ORDER.index(m_stem) if m_stem in STEMS_ORDER else 0
    m_branch_idx = BRANCHES_ORDER.index(m_branch) if m_branch in BRANCHES_ORDER else 0
    
    daeuns = []
    curr_age = daeun_su
    step = 1 if direction == 'forward' else -1
    
    for i in range(10): # Generate 10 cycles (100 years of life)
        stem_idx = (m_stem_idx + (i + 1) * step) % 10
        branch_idx = (m_branch_idx + (i + 1) * step) % 12
        d_stem = STEMS_ORDER[stem_idx]
        d_branch = BRANCHES_ORDER[branch_idx]
        d_pillar = d_stem + d_branch
        
        daeuns.append({
            'start_age': curr_age,
            'end_age': curr_age + 9,
            'stem': d_stem,
            'branch': d_branch,
            'pillar_kor': get_kor_char(d_stem) + get_kor_char(d_branch),
            'pillar_hanja': d_pillar
        })
        curr_age += 10
        
    return {
        'daeun_su': daeun_su,
        'direction': '순행' if direction == 'forward' else '역행',
        'direction_en': direction,
        'daeuns': daeuns,
        'closest_term': {
            'name': term_row['solar_term_korean'],
            'time': term_dt.strftime("%Y-%m-%d %H:%M"),
            'days_diff': round(days_diff, 2)
        }
    }

def find_yongsin_info(element_scores):
    """
    Determines Yongsin (용신 - balancer), Huisin (희신 - helper), and Gisin (기신 - opposing)
    based on the element scores.
    """
    sorted_elements = sorted(element_scores.items(), key=lambda x: x[1])
    
    # Lowest score is Yongsin (deficient energy that needs support)
    yongsin = sorted_elements[0][0]
    # Second lowest is Huisin
    huisin = sorted_elements[1][0]
    # Highest score is Gisin (excess energy)
    gisin = sorted_elements[-1][0]
    
    reason = (
        f"사주 분석 결과, 기운의 평형을 맞추기 위해 가장 결여된 {yongsin} 기운을 용신(用神)으로 삼고, "
        f"이를 보좌하여 생해주는 {huisin} 기운을 희신(喜神)으로 삼습니다. 반면 사주에 가장 과다하여 "
        f"치우침을 유발하는 {gisin} 기운은 흐름을 방해하는 기신(忌神)으로 판정됩니다."
    )
    
    return {
        'yongsin': yongsin,
        'huisin': huisin,
        'gisin': gisin,
        'reason': reason
    }

def simulate_life_fortune(year, birth_year, element_scores, base_scores, daeun_info):
    """
    Simulates age-by-age fortune scores and dynamic MBTI shifts.
    """
    # Find Yongsin/Huisin
    y_info = find_yongsin_info(element_scores)
    yongsin = y_info['yongsin']
    huisin = y_info['huisin']
    gisin = y_info['gisin']
    
    daeuns = daeun_info['daeuns']
    daeun_su = daeun_info['daeun_su']
    
    fortune_scores = []
    
    # Run simulation for ages 1 to 90
    for age in range(1, 91):
        # 1. Find active Daeun for this age
        active_daeun = None
        for d in daeuns:
            if d['start_age'] <= age <= d['end_age']:
                active_daeun = d
                break
        
        # If age is before first Daeun (age < daeun_su), use the month pillar as baseline
        if active_daeun is None:
            active_daeun = {
                'stem': daeuns[0]['stem'],
                'branch': daeuns[0]['branch'],
                'pillar_kor': '소운 (초년)',
                'pillar_hanja': ''
            }
            
        d_stem = active_daeun['stem']
        d_branch = active_daeun['branch']
        
        d_stem_elem, _ = get_element_and_yin_yang(d_stem)
        d_branch_elem, _ = get_element_and_yin_yang(d_branch)
        
        # Calculate Daeun fortune influence (base: 60)
        daeun_score = 60.0
        
        for elem in [d_stem_elem, d_branch_elem]:
            if elem == yongsin:
                daeun_score += 15.0
            elif elem == huisin:
                daeun_score += 8.0
            elif elem == gisin:
                daeun_score -= 12.0
                
        # 2. Find Seoun (yearly luck) for this age
        # year_at_age is Gregorian calendar year corresponding to this age
        year_at_age = birth_year + age - 1
        
        # Determine year branch index (cycle of 12)
        # Year branch is calculated by (year - 4) % 12
        seoun_branch_idx = (year_at_age - 4) % 12
        seoun_branch_hanja = BRANCHES_ORDER[seoun_branch_idx]
        seoun_branch_kor = get_kor_char(seoun_branch_hanja)
        seoun_elem, _ = get_element_and_yin_yang(seoun_branch_hanja)
        
        seoun_score = 0.0
        if seoun_elem == yongsin:
            seoun_score += 8.0
        elif seoun_elem == huisin:
            seoun_score += 4.0
        elif seoun_elem == gisin:
            seoun_score -= 6.0
            
        # Add a minor cyclical fluctuation for variety
        fluctuation = 3.0 * math.sin(age * 0.7) + 2.0 * math.cos(age * 1.3)
        
        # Total Fortune Score
        total_score = daeun_score + seoun_score + fluctuation
        # Clamp between 20 and 98
        total_score = max(20.0, min(98.0, total_score))
        
        # 3. Simulate Dynamic MBTI Shifts
        # Baseline MBTI scores
        adj_scores = base_scores.copy()
        
        # Apply elements influence from active Daeun
        # Wood (목): N/P increases
        # Fire (화): E/F increases
        # Earth (토): S/J increases
        # Metal (금): T/J increases
        # Water (수): I/N increases
        
        for elem in [d_stem_elem, d_branch_elem]:
            if elem == '목':
                adj_scores['N'] += 1.0
                adj_scores['P'] += 1.0
            elif elem == '화':
                adj_scores['E'] += 1.5
                adj_scores['F'] += 1.0
            elif elem == '토':
                adj_scores['S'] += 1.0
                adj_scores['J'] += 1.0
            elif elem == '금':
                adj_scores['T'] += 1.5
                adj_scores['J'] += 1.0
            elif elem == '수':
                adj_scores['I'] += 1.5
                adj_scores['N'] += 1.0
                
        # Resolve dynamic MBTI type
        mbti_chars = []
        mbti_chars.append('E' if adj_scores['E'] >= adj_scores['I'] else 'I')
        mbti_chars.append('S' if adj_scores['S'] >= adj_scores['N'] else 'N')
        mbti_chars.append('T' if adj_scores['T'] >= adj_scores['F'] else 'F')
        mbti_chars.append('J' if adj_scores['J'] >= adj_scores['P'] else 'P')
        dynamic_mbti = "".join(mbti_chars)
        
        fortune_scores.append({
            'age': age,
            'year': year_at_age,
            'score': round(total_score, 1),
            'daeun_pillar': active_daeun['pillar_kor'],
            'seoun_pillar': f"{seoun_branch_kor}년",
            'mbti': dynamic_mbti
        })
        
    # Generate decadal summaries for the detailed explanation
    decades_analysis = []
    # Analyze the 10 daeun cycles
    for d in daeuns:
        # Determine average score for this decade
        dec_scores = [x['score'] for x in fortune_scores if d['start_age'] <= x['age'] <= d['end_age']]
        avg_score = sum(dec_scores) / len(dec_scores) if dec_scores else 60.0
        
        d_stem_elem, _ = get_element_and_yin_yang(d['stem'])
        d_branch_elem, _ = get_element_and_yin_yang(d['branch'])
        
        # Get Sipsung of the Daeun stem (relative to Day Stem)
        # We need the day stem of the Saju birth chart
        # We can extract it from the calendar standard calculator row
        # For simplicity, let's write a descriptive text based on elements and sipsung
        # Elements description
        elem_desc = f"{d_stem_elem}·{d_branch_elem} 기운"
        
        # Qualitative description based on Yongsin/Huisin/Gisin
        is_good = (d_stem_elem == yongsin or d_branch_elem == yongsin)
        is_helper = (d_stem_elem == huisin or d_branch_elem == huisin)
        is_bad = (d_stem_elem == gisin or d_branch_elem == gisin)
        
        if is_good:
            qual_desc = "길(吉) - 귀하에게 이로운 용신 기운이 강하게 작용하여 마음에 평온이 찾아오고, 하시는 일이나 관계에 안정이 생기는 시기입니다."
        elif is_helper:
            qual_desc = "희(喜) - 희신 기운의 영향으로 삶의 든든한 조력자를 만나고, 목표를 성취하는 데 큰 탄력을 얻을 수 있습니다."
        elif is_bad:
            qual_desc = "기(忌) - 기신 기운이 지배하여 에너지가 분산되거나 현실적인 마찰 및 스트레스 관리가 요구되는 다소 신중한 시기입니다."
        else:
            qual_desc = "평(平) - 비교적 평탄하고 무난한 평운의 시기이며, 내면적 기틀을 튼튼히 가꾸어 다가올 전환기를 준비하기에 적합합니다."
            
        # Personality tendency shift summary
        mbti_shifts = []
        if '목' in [d_stem_elem, d_branch_elem]:
            mbti_shifts.append("아이디어가 풍부해지고 융통성이 생겨 인식형(P)/직관형(N) 기질이 강해집니다.")
        if '화' in [d_stem_elem, d_branch_elem]:
            mbti_shifts.append("사회적 표현력이 향상되어 외향성(E)/감정형(F) 경향이 증가합니다.")
        if '토' in [d_stem_elem, d_branch_elem]:
            mbti_shifts.append("현실 감각과 책임감이 무거워져 감각성(S)/판단형(J) 기질을 보강합니다.")
        if '금' in [d_stem_elem, d_branch_elem]:
            mbti_shifts.append("구조화된 사고와 냉정한 판단력이 서며 사고형(T)/판단형(J) 경향이 두드러집니다.")
        if '수' in [d_stem_elem, d_branch_elem]:
            mbti_shifts.append("내면 성찰과 사색의 시간이 많아져 내향성(I)/직관형(N) 기질이 활성화됩니다.")
            
        shift_text = " ".join(mbti_shifts) if mbti_shifts else "고유 기질이 균형 있게 발현됩니다."
        
        decades_analysis.append({
            'age_range': f"{d['start_age']}세 ~ {d['end_age']}세",
            'pillar': f"{d['pillar_kor']} ({d['stem']}{d['branch']}) 대운",
            'score': round(avg_score, 1),
            'qual_desc': qual_desc,
            'shift_text': shift_text,
            'desc': f"{elem_desc}이 들어오는 시기입니다. {qual_desc} {shift_text}"
        })
        
    return {
        'yongsin_info': y_info,
        'fortune_scores': fortune_scores,
        'decades_analysis': decades_analysis
    }
