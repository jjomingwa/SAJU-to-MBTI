import sys
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
    '자': {'element': '수', 'yin_yang': '양', 'kor': '자'},
    '축': {'element': '토', 'yin_yang': '음', 'kor': '축'},
    '인': {'element': '목', 'yin_yang': '양', 'kor': '인'},
    '묘': {'element': '목', 'yin_yang': '음', 'kor': '묘'},
    '진': {'element': '토', 'yin_yang': '양', 'kor': '진'},
    '사': {'element': '화', 'yin_yang': '음', 'kor': '사'},
    '오': {'element': '화', 'yin_yang': '양', 'kor': '오'},
    '미': {'element': '토', 'yin_yang': '음', 'kor': '미'},
    '신': {'element': '금', 'yin_yang': '양', 'kor': '신'},
    '유': {'element': '금', 'yin_yang': '음', 'kor': '유'},
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
        
    if day_elem == t_elem:
        return '비견' if day_yy == t_yy else '겁재'
        
    if ELEMENT_RELATIONS[day_elem]['생'] == t_elem:
        return '식신' if day_yy == t_yy else '상관'
        
    if ELEMENT_RELATIONS[day_elem]['극'] == t_elem:
        return '편재' if day_yy == t_yy else '정재'
        
    if ELEMENT_RELATIONS[day_elem]['극당함'] == t_elem:
        return '편관' if day_yy == t_yy else '정관'
        
    if ELEMENT_RELATIONS[day_elem]['생함받음'] == t_elem:
        return '편인' if day_yy == t_yy else '정인'
        
    return None

# NEW: Integrated 10 scenarios comparison logic
def generate_integrated_scenarios(res, real_mbti):
    if not real_mbti:
        return []
        
    real_mbti = real_mbti.upper()
    est_mbti = res['options'][0].upper()
    
    # Extract MBTI components
    r_e, r_s, r_t, r_j = real_mbti[0], real_mbti[1], real_mbti[2], real_mbti[3]
    e_e, e_s, e_t, e_j = est_mbti[0], est_mbti[1], est_mbti[2], est_mbti[3]
    
    # Extract Saju core qualities
    strong_elements = res['strong_elements']
    strong_sipsungs = res['strong_sipsungs']
    strong_elem = strong_elements[0] if strong_elements else '토'
    strong_ss = strong_sipsungs[0] if strong_sipsungs else '비견'
    
    scenarios = []

    # Scenario 1 (EI Axis)
    scenarios.append({
        'key': 'scenario_1',
        'title': '1. 에너지 충전과 사회적 교류',
        'real_desc': '대외 활동이나 주변인과의 왕성한 대면 소통을 거쳐 활력을 수혈받는 능동형 충전 방식을 활용합니다.' if r_e == 'E' 
                     else '소수 정예와 함께하거나 고요한 정적의 공간에서 자아 성찰을 통해 닳아버린 정신적 활력을 보급합니다.',
        'est_desc': '외향 기운(화/목 기운 혹은 식상 발달)이 지배하여 역동적인 사회 활동과 교류를 통해 에너지를 재충전하는 기질입니다.' if e_e == 'E'
                     else '내향 기운(수/금 기운 혹은 인성/비견 발달)이 강하여 조용히 혼자 있는 방랑이나 고독에서 정신 에너지를 채우는 기질입니다.',
        'is_different': r_e != e_e
    })

    # Scenario 2 (SN Axis)
    scenarios.append({
        'key': 'scenario_2',
        'title': '2. 정보 수집과 세상을 보는 눈',
        'real_desc': '눈앞에 객관적으로 증명되는 팩트와 디테일한 수치, 과거 경험 데이터를 기준으로 사태를 명확하게 수집합니다.' if r_s == 'S'
                     else '눈에 보이는 것 이상의 이면 맥락, 거시적 아이디어, 미래가 가진 비전과 은유적 직관성을 통해 파악합니다.',
        'est_desc': '토(土)/금(金) 등 조형적 실체가 강해 당장의 눈앞의 실리와 증명 가능한 현실 디테일을 확실히 보는 기질입니다.' if e_s == 'S'
                     else '목(木)/수(水) 등 상징적 성장이 발달하여 팩트 너머의 패턴과 거시적 상상력, 무형의 비전을 직관하는 기질입니다.',
        'is_different': r_s != e_s
    })

    # Scenario 3 (TF Axis)
    scenarios.append({
        'key': 'scenario_3',
        'title': '3. 의사결정과 최우선 가치 기준',
        'real_desc': '논리적 팩트 검증과 객관적인 효율성, 엄정한 규칙과 공정성을 잣대 삼아 명료하게 의사결정을 내립니다.' if r_t == 'T'
                     else '인간적인 유대와 정서적 가치, 타인의 감정에 미칠 영향과 상호 공감 및 도덕적 가치를 중심에 두고 판단합니다.',
        'est_desc': '금(金)과 관성이 발달해 차갑고 냉철한 시시비비와 시스템의 공적 효율, 이성적 최적화를 최우선 의결 기준으로 삼는 기질입니다.' if e_t == 'T'
                     else '화(火)와 식신/정인이 결합하여 따스한 감성적 연결, 관계의 평화적 조화와 타인의 마음에 공감하는 것을 최우선하는 기질입니다.',
        'is_different': r_t != e_t
    })

    # Scenario 4 (JP Axis)
    scenarios.append({
        'key': 'scenario_4',
        'title': '4. 행동 방식과 일과 시간 관리',
        'real_desc': '일정과 목표를 꼼꼼하게 정리하고, 예기치 못한 차질이 생기지 않도록 매사 매뉴얼대로 진행하는 데서 안전감을 얻습니다.' if r_j == 'J'
                     else '계획에 지배당하기보다 수시로 유연한 융통성을 발휘해 그날의 최선 흐름에 맞춰 임기응변으로 상황에 적응합니다.',
        'est_desc': '토(土)와 관성/정재의 안정 통제가 작용해 단단한 절차 수립과 정리정돈, 질서 있는 통제를 생활화하려는 성향입니다.' if e_j == 'J'
                     else '식상과 비겁의 분출성이 지배하여 정해진 규칙에 속박되지 않고 즉흥적으로 자유롭게 시도하고 발산하려는 유연 기질입니다.',
        'is_different': r_j != e_j
    })

    # Scenario 5 (Motivation - Integrated)
    # MBTI group motivation
    r_group = 'NF' if r_s + r_t in ['NF', 'SF'] and r_t == 'F' else ('NT' if r_t == 'T' and r_s == 'N' else ('SJ' if r_s == 'S' and r_j == 'J' else 'SP'))
    if r_group == 'NF':
        r_mot = "진정성 있는 삶, 인간적 조화와 깊은 자아실현을 갈망합니다."
    elif r_group == 'NT':
        r_mot = "지적인 자아 확장, 논리적 시스템 개혁, 지식의 완벽성을 추구합니다."
    elif r_group == 'SJ':
        r_mot = "가정, 사회 및 조직의 전통 질서와 안정을 성실하게 지키는 성취를 지향합니다."
    else:
        r_mot = "자유로운 신체/정신적 자기표현과 제약 없는 모험, 실용적 유희를 지향합니다."

    # Saju core motivation
    if strong_ss in ['정관', '편관', '정재', '편재'] or strong_elem in ['토', '금']:
        e_mot = f"강한 {strong_elem} 기운과 {strong_ss}의 작용으로, 세속적인 성공 기반과 실리적인 자산 지배권, 혹은 확실히 검증된 명예 권위를 안전하게 확보하려는 강한 현실 욕망을 품고 있습니다."
    elif strong_ss in ['식신', '상관'] or strong_elem in ['목', '화']:
        e_mot = f"강렬한 {strong_elem} 기운과 {strong_ss}의 영향으로, 외부적 통제에 맞서 본인의 창의적 재능과 자아 가치를 끊임없이 표현하고 성장시키며 뽐내고자 하는 욕망이 큽니다."
    elif strong_ss in ['편인', '정인'] or strong_elem == '수':
        e_mot = f"깊은 {strong_elem} 기운과 {strong_ss}이 내면화되어 세속적 지위 다툼에서 한 발 물러나 학문적 깊이, 지혜의 체득, 영적이고 철학적인 지적 사유의 발전을 추구합니다."
    else:
        e_mot = f"강한 비겁 기운의 발달로 누구의 간섭도 허용하지 않고 오롯이 나만의 주권과 주체적 고유 영역을 수호하며 독립적인 자아로 서는 것을 갈망합니다."
        
    scenarios.append({
        'key': 'scenario_5',
        'title': '5. 인생의 근본적 동기 및 욕망',
        'real_desc': f"자아인식에서는 {r_mot}",
        'est_desc': f"사주 기질상으로는 {e_mot}",
        'is_different': ('현실' in e_mot and r_group in ['NF', 'SP']) or ('표현' in e_mot and r_group in ['SJ']) or ('지혜' in e_mot and r_group in ['SP', 'SJ'])
    })

    # Scenario 6 (Stress - Integrated)
    if r_e == 'I':
        r_stress = "열등기능이 과부하되어 통제 불능 상태가 되면 극도로 위축되거나 자가망상 혹은 충동적인 현실 도피에 들어설 확률이 큽니다."
    else:
        r_stress = "에너지가 고갈되면 주위 사람들에게 히스테릭한 짜증을 방출하거나 의무와 규칙을 어기고 강박적으로 일을 벌려 주의를 분산시킵니다."

    if strong_ss in ['정관', '편관']:
        e_stress = "사주에 발달한 억압성(관성)으로 인해 스트레스가 극에 달하면 스스로를 무섭게 처벌하고 우울 속으로 몰아세우며 더욱 강박적으로 시스템을 완벽히 규율하려 듭니다."
    elif strong_ss in ['식신', '상관']:
        e_stress = "표출성(식상)이 자극되어 극도로 폭주하면 다듬어지지 않은 날카롭고 거친 말과 감정적 독설을 화끈하게 폭발시켜 주변과의 관계를 순간적으로 파괴하며 정화하려 합니다."
    elif strong_ss == '비견' or strong_ss == '겁재':
        e_stress = "비겁의 주체적 자존심이 내몰리면 한 치의 타협도 허용하지 않는 완전한 불통과 고립 장벽을 구축한 채 자기 방으로 칩잠하는 방어기제를 취합니다."
    else:
        e_stress = "인성의 수용 기운이 과부하되면 생각의 루프 속에 스스로를 가두고 멍한 무기력에 빠지며, 완전히 세상을 외면하려 함으로써 정서적 방전을 견뎌냅니다."

    scenarios.append({
        'key': 'scenario_6',
        'title': '6. 한계 상황과 스트레스 극복 기제',
        'real_desc': f"자아 보고에 따르면 {r_stress}",
        'est_desc': f"사주 기질적 무의식으로는 {e_stress}",
        'is_different': ('폭발' in e_stress and r_e == 'I') or ('칩잠' in e_stress and r_e == 'E')
    })

    # Scenario 7 (Conflict - Integrated)
    r_conf = "타인과의 평화와 조화를 갈망해 마찰이 생기면 일단 참거나 양보하여 관계 수선에 앞장섭니다." if r_t == 'F' else "팩트의 정오를 규명하고 무엇이 원리적으로 타당한지 이성적으로 논쟁하여 결판을 짓고자 합니다."
    if strong_ss in ['식신', '상관', '비견', '겁재']:
        e_conf = "비식(比食)의 독립·표출 기운이 세서 갈등 발생 시 자존심을 꺾기 힘들어하며 본인의 정당성을 강력하게 입증하거나 피하지 않고 정면 승부를 겨루려 합니다."
    elif strong_ss in ['정관', '편관', '정인', '편인']:
        e_conf = "관인(官印)의 통제 기질로 인해 면전에서의 충돌은 가급적 참아 넘기지만, 내심 강한 규칙의 선을 긋고 무례한 대상을 조용히 인생에서 차단(손절)하는 방식을 씁니다."
    else:
        e_conf = "재성적 수완을 적극 발휘해 이 갈등이 불러올 현실적 이해득실을 냉정히 주산하여 양자가 가장 실리적으로 윈윈할 수 있는 합의점을 노련하게 협상해 냅니다."

    scenarios.append({
        'key': 'scenario_7',
        'title': '7. 대인관계의 갈등 관리 스타일',
        'real_desc': f"자아 보고로는 {r_conf}",
        'est_desc': f"사주 기질로는 {e_conf}",
        'is_different': ('정면 승부' in e_conf and r_t == 'F') or ('조용히 손절' in e_conf and r_t == 'T')
    })

    # Scenario 8 (Crisis - Integrated)
    r_crisis = "구조화된 대안 절차를 세워 돌발 상황을 조속히 규칙 통제 하에 두려 조바심을 냅니다." if r_j == 'J' else "위기가 올 때 비로소 특유의 아드레날린을 느껴 순발력 있는 임기응변으로 순탄하게 파도를 타고 넘습니다."
    if strong_ss in ['비견', '겁재'] or strong_elem == '목':
        e_crisis = "강건한 주체 생명성(비겁/목)에 힘입어 위기 상황이 닥쳐도 기가 죽지 않고 본인의 고집과 저력으로 파도를 정면돌파하여 부수고 나아가는 돌파력을 뿜어냅니다."
    elif strong_ss in ['편인', '정인'] or strong_elem == '수':
        e_crisis = "수(水)의 지혜와 침잠 기질(인성)을 활용해 섣불리 움직이지 않고 일단 상황을 끝까지 관조하며 깊은 인내로 고요히 때를 기다려 지혜롭게 극복합니다."
    else:
        e_crisis = "재관의 사회 협력망을 통해 혼자 해결하기보다 주변의 제도, 공적 조직, 자산 파트너들을 가용해 영리하게 리스크를 분산하고 조율해 해결합니다."

    scenarios.append({
        'key': 'scenario_8',
        'title': '8. 인생의 전환점과 위기 대처법',
        'real_desc': f"자아 분석에서는 {r_crisis}",
        'est_desc': f"사주 오행적 대처는 {e_crisis}",
        'is_different': ('돌파' in e_crisis and r_j == 'J') or ('관조' in e_crisis and r_j == 'P')
    })

    # Scenario 9 (Leadership - Integrated)
    r_lead = "비전과 성장의 이상을 거시적 지향점으로 뿜어내며 동기부여하는 멘토형 리더십을 지향합니다." if r_s == 'N' else "명확한 규정과 분담, 실행 단계별 꼼꼼한 품질 유지를 통해 신뢰를 주는 실무형 수호자 리더십을 보입니다."
    if strong_ss in ['정관', '편관', '정인', '편인']:
        e_lead = "관인상생(官印相生)의 모범적 직무 기질로 인해 조직의 보고 체계와 절차를 칼같이 준수하고 안정적으로 계통을 수립하여 관리하는 '규격화된 관리자형' 기질입니다."
    elif strong_ss in ['식신', '상관', '편재', '정재']:
        e_lead = "식상생재(食傷生財)의 도전적 수완으로 현장 중심의 창의적 비즈니스를 주도적으로 뚫어내고 이윤을 창출하는 '개척자/프로젝트 지휘관형' 리더십입니다."
    else:
        e_lead = "비식(比食)이 발달해 상하 통제를 질색하며 독립 프리랜서형 전문가를 지향해 평등하고 독립적인 분담 하의 느슨한 시너지를 선호합니다."

    scenarios.append({
        'key': 'scenario_9',
        'title': '9. 조직 내에서의 협업 및 리더십',
        'real_desc': f"자아 보고로는 {r_lead}",
        'est_desc': f"사주 십성 기틀은 {e_lead}",
        'is_different': ('관리자' in e_lead and r_s == 'N') or ('독립 프리' in e_lead and r_s == 'S')
    })

    # Scenario 10 (Finance - Integrated)
    r_fin = "현실적 삶의 안전망을 든든하게 메우기 위해 체계적으로 저축하고 예산 통제를 하려 애씁니다." if r_s == 'S' else "무형의 학습 가치, 흥미로운 프로젝트나 독립된 자율성을 보장받는 일이라면 리스크를 안고도 베팅합니다."
    if strong_ss in ['정재', '편재'] or strong_elem == '토':
        e_fin = "재성(財星)의 영리한 실리 기질이 활성화되어 부동산, 계좌 정산 등 눈에 보이는 물적 자산을 빈틈없이 세금 수준으로 소유 및 제어해야만 진정한 안정감을 느낍니다."
    elif strong_ss in ['식신', '상관']:
        e_fin = "식상의 향유 기운에 영향을 받아 돈을 묵혀두기보다 나 자신을 뽐낼 취미, 패션, 자기계발 및 동료들과의 호탕한 대접에 소모해 정신적 유희로 전환하는 소비 성향이 높습니다."
    else:
        e_fin = "인성과 수(水) 기운의 비유물성으로 인해 세속적인 자산 다툼에 다소 초연하며 영적인 문화, 무형의 사색, 공부나 가치관 실현에 경제적 초점을 맞춥니다."

    scenarios.append({
        'key': 'scenario_10',
        'title': '10. 물질적 가치와 안정을 대하는 자세',
        'real_desc': f"자아 보고에서는 {r_fin}",
        'est_desc': f"사주 기질상 재화 관념은 {e_fin}",
        'is_different': ('소유 및 제어' in e_fin and r_s == 'N') or ('문화' in e_fin and r_s == 'S')
    })

    return scenarios

def analyze_saju_mbti(year, month, day, hour, minute, city="Seoul", real_mbti=None, gender="male", longitude=None, utc_offset=9):
    calculator = SajuCalculator()
    
    try:
        import pandas as pd
        calculator.data = pd.read_csv(
            calculator.csv_path,
            dtype={'year': int, 'month': int, 'day': int},
            parse_dates=False,
            encoding='utf-8'
        )
    except Exception as e:
        print("Warning: Failed to apply UTF-8 encoding patch to sajupy database:", e)

    saju = calculator.calculate_saju(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        city=city,
        longitude=longitude,
        utc_offset=utc_offset,
        use_solar_time=True
    )


    
    # Extract pillars (stems and branches)
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
    
    breakdown = {
        'element_calculation': [],
        'season_adjustment': '',
        'sipsung_calculation': [],
        'yinyang_adjustment': '',
        'mbti_formulas': {}
    }
    
    # 1. 오행 점수 계산
    element_scores = {'목': 0.0, '화': 0.0, '토': 0.0, '금': 0.0, '수': 0.0}
    for pillar_name, content in pillars.items():
        p_weight = POSITION_WEIGHTS[pillar_name]
        for type_name, char in content.items():
            t_weight = TYPE_WEIGHTS[type_name]
            elem, _ = get_element_and_yin_yang(char)
            if elem:
                score = p_weight * t_weight
                element_scores[elem] += score
                breakdown['element_calculation'].append(
                    f"{pillar_name} {type_name}: {get_kor_char(char)}({elem}) -> "
                    f"{p_weight}(위치) x {t_weight}(형태) = +{score:.2f}점"
                )
                
    # 2. 계절 보정
    season_element = None
    if m_branch in ['寅', '卯', '辰']:
        season_element = '목'
    elif m_branch in ['巳', '午', '未'] or m_branch in ['사', '오', '미']:
        season_element = '화'
    elif m_branch in ['申', '酉', '戌']:
        season_element = '금'
    elif m_branch in ['亥', '子', '丑'] or m_branch in ['해', '자', '축']:
        season_element = '수'
        
    if season_element:
        prev_score = element_scores[season_element]
        element_scores[season_element] *= 1.2
        new_score = element_scores[season_element]
        breakdown['season_adjustment'] = (
            f"월지 기둥 지지 {get_kor_char(m_branch)} 기준 계절 보정: {season_element} 기운 1.2배 강화 적용 "
            f"(기존 {prev_score:.2f}점 -> {new_score:.2f}점)"
        )
    else:
        breakdown['season_adjustment'] = "월지 기준 특정 오행 계절 보정 조건 없음 (환절기/토 등)"
        
    # 3. 십성 점수 계산 (일간 기준)
    sipsung_scores = {
        '비견': 0.0, '겁재': 0.0, '식신': 0.0, '상관': 0.0, '편재': 0.0,
        '정재': 0.0, '편관': 0.0, '정관': 0.0, '편인': 0.0, '정인': 0.0
    }
    
    sipsung_map = {}
    for pillar_name, content in pillars.items():
        p_weight = POSITION_WEIGHTS[pillar_name]
        sipsung_map[pillar_name] = {}
        for type_name, char in content.items():
            t_weight = TYPE_WEIGHTS[type_name]
            if pillar_name == '일주' and type_name == '천간':
                breakdown['sipsung_calculation'].append(
                    f"일주 천간: {get_kor_char(char)} -> 자기 자신(일간), 십성 판정 기준점으로 점수 가산 제외"
                )
                continue
            ss = get_sipsung(d_stem, char)
            if ss:
                score = p_weight * t_weight
                sipsung_scores[ss] += score
                sipsung_map[pillar_name][type_name] = ss
                breakdown['sipsung_calculation'].append(
                    f"{pillar_name} {type_name}: {get_kor_char(char)} -> {ss} 매핑 -> "
                    f"{p_weight}(위치) x {t_weight}(형태) = +{score:.2f}점"
                )

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
        breakdown['yinyang_adjustment'] = (
            f"음양 구성: 양 {yang_ratio*100:.1f}% | 음 {yin_ratio*100:.1f}% -> "
            f"양 기운이 60% 이상이므로 외향성 E +1, 유연성 P +1 가산 보정 적용"
        )
    elif yin_ratio >= 0.60:
        yy_adjustment['I'] += 1
        yy_adjustment['J'] += 1
        breakdown['yinyang_adjustment'] = (
            f"음양 구성: 양 {yang_ratio*100:.1f}% | 음 {yin_ratio*100:.1f}% -> "
            f"음 기운이 60% 이상이므로 내향성 I +1, 구조성 J +1 가산 보정 적용"
        )
    else:
        breakdown['yinyang_adjustment'] = (
            f"음양 구성: 양 {yang_ratio*100:.1f}% | 음 {yin_ratio*100:.1f}% -> "
            f"음양 기운이 균형을 이루므로 추가 보정 가산 없음"
        )

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
    expressive_positions = [
        sipsung_map.get('월주', {}).get('천간'),
        sipsung_map.get('월주', {}).get('지지'),
        sipsung_map.get('시주', {}).get('천간'),
        sipsung_map.get('시주', {}).get('지지')
    ]
    expressive_bonus = any(ss in ['상관', '식신', '편재', '겁재'] for ss in expressive_positions)
    if expressive_bonus:
        E_base += 1
    
    breakdown['mbti_formulas']['E'] = (
        f"E = 화({element_scores['화']:.2f}) x 2 + 목({element_scores['목']:.2f}) x 1 + "
        f"겁재({sipsung_scores['겁재']:.2f}) x 2 + 식신({sipsung_scores['식신']:.2f}) x 1 + "
        f"상관({sipsung_scores['상관']:.2f}) x 1 + 편재({sipsung_scores['편재']:.2f}) x 2 + "
        f"음양보정({yy_adjustment['E']}) + 월주/시간표현성보정({1 if expressive_bonus else 0}) = {E_base:.2f}점"
    )

    I_base = (
        element_scores['수'] * 2 +
        element_scores['금'] * 1 +
        sipsung_scores['비견'] * 1 +
        sipsung_scores['정관'] * 1 +
        sipsung_scores['편인'] * 2 +
        sipsung_scores['정인'] * 1 +
        yy_adjustment['I']
    )
    reflective_positions = [
        sipsung_map.get('일주', {}).get('지지'),
        sipsung_map.get('시주', {}).get('천간'),
        sipsung_map.get('시주', {}).get('지지')
    ]
    reflective_bonus = any(ss in ['편인', '정인', '비견', '정관'] for ss in reflective_positions)
    if reflective_bonus:
        I_base += 1
        
    breakdown['mbti_formulas']['I'] = (
        f"I = 수({element_scores['수']:.2f}) x 2 + 금({element_scores['금']:.2f}) x 1 + "
        f"비견({sipsung_scores['비견']:.2f}) x 1 + 정관({sipsung_scores['정관']:.2f}) x 1 + "
        f"편인({sipsung_scores['편인']:.2f}) x 2 + 정인({sipsung_scores['정인']:.2f}) x 1 + "
        f"음양보정({yy_adjustment['I']}) + 일주/시간내면성보정({1 if reflective_bonus else 0}) = {I_base:.2f}점"
    )

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
    reality_monthly = [
        sipsung_map.get('월주', {}).get('천간'),
        sipsung_map.get('월주', {}).get('지지')
    ]
    reality_bonus = any(ss in ['정재', '편재', '정관', '편관'] for ss in reality_monthly)
    if reality_bonus:
        S_base += 1
        
    breakdown['mbti_formulas']['S'] = (
        f"S = 토({element_scores['토']:.2f}) x 2 + 금({element_scores['금']:.2f}) x 1 + "
        f"식신({sipsung_scores['식신']:.2f}) x 1 + 편재({sipsung_scores['편재']:.2f}) x 1 + "
        f"정재({sipsung_scores['정재']:.2f}) x 2 + 정관({sipsung_scores['정관']:.2f}) x 1 + "
        f"편관({sipsung_scores['편관']:.2f}) x 1 + 월주현실적십성보정({1 if reality_bonus else 0}) = {S_base:.2f}점"
    )

    N_base = (
        element_scores['목'] * 2 +
        element_scores['수'] * 2 +
        element_scores['화'] * 1 +
        sipsung_scores['상관'] * 2 +
        sipsung_scores['편인'] * 2 +
        sipsung_scores['정인'] * 1
    )
    abstract_positions = [
        sipsung_map.get('월주', {}).get('천간'),
        sipsung_map.get('월주', {}).get('지지'),
        sipsung_map.get('일주', {}).get('지지')
    ]
    abstract_bonus = any(ss in ['편인', '상관'] for ss in abstract_positions) or (element_scores['목'] + element_scores['수'] > 5.0)
    if abstract_bonus:
        N_base += 1
        
    breakdown['mbti_formulas']['N'] = (
        f"N = 목({element_scores['목']:.2f}) x 2 + 수({element_scores['수']:.2f}) x 2 + "
        f"화({element_scores['화']:.2f}) x 1 + 상관({sipsung_scores['상관']:.2f}) x 2 + "
        f"편인({sipsung_scores['편인']:.2f}) x 2 + 정인({sipsung_scores['정인']:.2f}) x 1 + "
        f"미래추상성조합보정({1 if abstract_bonus else 0}) = {N_base:.2f}점"
    )

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
    logic_bonus = (element_scores['금'] + element_scores['수'] > 5.0) or (sipsung_scores['편관'] + sipsung_scores['정관'] > 3.0)
    if logic_bonus:
        T_base += 1
        
    breakdown['mbti_formulas']['T'] = (
        f"T = 금({element_scores['금']:.2f}) x 2 + 수({element_scores['수']:.2f}) x 1 + "
        f"비견({sipsung_scores['비견']:.2f}) x 1 + 겁재({sipsung_scores['겁재']:.2f}) x 1 + "
        f"상관({sipsung_scores['상관']:.2f}) x 1 + 편재({sipsung_scores['편재']:.2f}) x 1 + "
        f"정재({sipsung_scores['정재']:.2f}) x 1 + 편관({sipsung_scores['편관']:.2f}) x 2 + "
        f"정관({sipsung_scores['정관']:.2f}) x 1 + 금/수/관성보정({1 if logic_bonus else 0}) = {T_base:.2f}점"
    )

    F_base = (
        element_scores['화'] * 2 +
        element_scores['목'] * 1 +
        element_scores['토'] * 1 +
        sipsung_scores['식신'] * 2 +
        sipsung_scores['정인'] * 1
    )
    harmony_bonus = (element_scores['목'] + element_scores['화'] > 5.0) or (sipsung_scores['식신'] + sipsung_scores['상관'] > 3.0)
    if harmony_bonus:
        F_base += 1
        
    breakdown['mbti_formulas']['F'] = (
        f"F = 화({element_scores['화']:.2f}) x 2 + 목({element_scores['목']:.2f}) x 1 + "
        f"토({element_scores['토']:.2f}) x 1 + 식신({sipsung_scores['식신']:.2f}) x 2 + "
        f"정인({sipsung_scores['정인']:.2f}) x 1 + 목/화/식상관계성보정({1 if harmony_bonus else 0}) = {F_base:.2f}점"
    )

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
    structure_bonus = any(ss in ['정관', '편관', '정재', '편재'] for ss in reality_monthly)
    if structure_bonus:
        J_base += 1
        
    breakdown['mbti_formulas']['J'] = (
        f"J = 토({element_scores['토']:.2f}) x 2 + 금({element_scores['금']:.2f}) x 2 + "
        f"정재({sipsung_scores['정재']:.2f}) x 2 + 정관({sipsung_scores['정관']:.2f}) x 2 + "
        f"편관({sipsung_scores['편관']:.2f}) x 2 + 정인({sipsung_scores['정인']:.2f}) x 1 + "
        f"음양보정({yy_adjustment['J']}) + 월주관성재성보정({1 if structure_bonus else 0}) = {J_base:.2f}점"
    )

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
    flexibility_bonus = (sipsung_scores['식신'] + sipsung_scores['상관'] + sipsung_scores['비견'] + sipsung_scores['겁재'] + sipsung_scores['편인'] > 5.0)
    if flexibility_bonus:
        P_base += 1
        
    breakdown['mbti_formulas']['P'] = (
        f"P = 목({element_scores['목']:.2f}) x 1 + 화({element_scores['화']:.2f}) x 1 + "
        f"수({element_scores['수']:.2f}) x 1 + 겁재({sipsung_scores['겁재']:.2f}) x 2 + "
        f"식신({sipsung_scores['식신']:.2f}) x 1 + 상관({sipsung_scores['상관']:.2f}) x 2 + "
        f"편재({sipsung_scores['편재']:.2f}) x 1 + 편인({sipsung_scores['편인']:.2f}) x 1 + "
        f"음양보정({yy_adjustment['P']}) + 식상비겁편인보정({1 if flexibility_bonus else 0}) = {P_base:.2f}점"
    )

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
    flexible_axes = []
    for axis, (dec, strength, ratio) in axis_results.items():
        if strength in ["거의 동률", "약한 선호"]:
            flexible_axes.append(axis)

    def replace_char(mbti, axis_index, new_char):
        lst = list(mbti)
        lst[axis_index] = new_char
        return "".join(lst)

    mbti_options = [primary_mbti]
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
        'yy_adjustment': yy_adjustment,
        'breakdown': breakdown,
        'gender': gender,
        'solar_correction': saju.get('solar_correction')
    }


def print_results(res):
    print("## 1. 사주 핵심 요약\n")
    print(f"* 강한 오행: {', '.join(res['strong_elements'])}")
    print(f"* 약한 오행: {', '.join(res['weak_elements'])}")
    print(f"* 강한 십성: {', '.join(res['strong_sipsungs'])}")
    
    display_pillars = {}
    for name, content in res['pillars'].items():
        display_pillars[name] = f"{get_kor_char(content['천간'])}{get_kor_char(content['지지'])}"
        
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
