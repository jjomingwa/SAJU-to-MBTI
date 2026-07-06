from flask import Flask, request, jsonify, render_template
from saju_mbti import analyze_saju_mbti, get_kor_char, generate_integrated_scenarios
from sajupy import SajuCalculator

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    hour = data.get('hour')
    minute = data.get('minute', 0)
    city = data.get('city', 'Seoul')
    real_mbti = data.get('real_mbti')
    calendar_type = data.get('calendar_type', 'solar') # solar / lunar_solar / lunar_leap
    
    gender = data.get('gender', 'male')
    longitude = data.get('longitude')
    utc_offset = data.get('utc_offset', 9)
    
    if not all([year, month, day, hour is not None]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Validate gender
    if gender not in ['male', 'female']:
        return jsonify({'error': '성별은 남성(male) 또는 여성(female)이어야 합니다.'}), 400
        
    # Cast longitude and utc_offset safely
    if longitude is not None:
        try:
            longitude = float(longitude)
        except ValueError:
            longitude = None
            
    try:
        utc_offset = float(utc_offset)
    except ValueError:
        utc_offset = 9.0
        
    # Validate real_mbti
    if real_mbti == '':
        real_mbti = None
    if real_mbti:
        real_mbti = real_mbti.upper().strip()
        if len(real_mbti) != 4 or not all(c in 'EISTFNJP' for c in real_mbti):
            return jsonify({'error': '실제 MBTI는 올바른 4자리 유형(예: ENFP)이어야 합니다.'}), 400
            
    try:
        original_date_str = f"{year}년 {month}월 {day}일"
        converted_log = "양력 생일 기준 계산"
        is_converted = False
        
        # Lunar to Solar conversion if required
        calculator = SajuCalculator()
        try:
            import pandas as pd
            calculator.data = pd.read_csv(
                calculator.csv_path,
                dtype={'year': int, 'month': int, 'day': int},
                parse_dates=False,
                encoding='utf-8'
            )
        except Exception:
            pass

        if calendar_type in ['lunar_solar', 'lunar_leap']:
            is_leap = (calendar_type == 'lunar_leap')
            try:
                solar_info = calculator.lunar_to_solar(
                    lunar_year=int(year),
                    lunar_month=int(month),
                    lunar_day=int(day),
                    is_leap_month=is_leap
                )
                
                # Update year, month, day to solar values for saju calculation
                year = solar_info['solar_year']
                month = solar_info['solar_month']
                day = solar_info['solar_day']
                
                converted_log = f"음력 {original_date_str} ({'윤달' if is_leap else '평달'}) -> 양력 {year}년 {month}월 {day}일 자동 변환"
                is_converted = True
            except Exception as e:
                return jsonify({'error': f"음력 변환 오류: {str(e)}"}), 400
                
        results = analyze_saju_mbti(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=int(hour),
            minute=int(minute),
            city=city,
            real_mbti=real_mbti,
            gender=gender,
            longitude=longitude,
            utc_offset=utc_offset
        )
        
        # Convert Chinese characters in pillars to Korean for easier frontend rendering
        display_pillars = {}
        for name, content in results['pillars'].items():
            display_pillars[name] = {
                'stem': get_kor_char(content['천간']),
                'branch': get_kor_char(content['지지']),
                'full': get_kor_char(content['천간']) + get_kor_char(content['지지'])
            }
            
        # Add calendar conversion log to breakdown object
        results['breakdown']['calendar_conversion'] = converted_log
        
        # Build scenario comparisons if real_mbti is provided
        scenarios_comparison = []
        if real_mbti:
            scenarios_comparison = generate_integrated_scenarios(results, real_mbti)
            
        # Call fortune simulation engine
        from saju_fortune_engine import calculate_daeun_info, simulate_life_fortune
        daeun_info = calculate_daeun_info(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=int(hour),
            minute=int(minute),
            gender=gender,
            calculator=calculator
        )
        
        fortune_res = simulate_life_fortune(
            year=int(year),
            birth_year=int(year),
            element_scores=results['element_scores'],
            base_scores=results['scores'],
            daeun_info=daeun_info
        )
        
        # Structure the payload for frontend
        payload = {
            'pillars': display_pillars,
            'element_scores': results['element_scores'],
            'sipsung_scores': results['sipsung_scores'],
            'scores': results['scores'],
            'axis_results': {
                k: {
                    'decision': v[0],
                    'strength': v[1],
                    'ratio': v[2]
                } for k, v in results['axis_results'].items()
            },
            'options': results['options'],
            'strong_elements': results['strong_elements'],
            'weak_elements': results['weak_elements'],
            'strong_sipsungs': results['strong_sipsungs'],
            'real_mbti': results['real_mbti'],
            'yang_ratio': round(results['yang_ratio'] * 100, 1),
            'yin_ratio': round((1 - results['yang_ratio']) * 100, 1),
            'breakdown': results['breakdown'],
            'calendar_info': {
                'original': original_date_str,
                'type': '양력' if calendar_type == 'solar' else ('음력 평달' if calendar_type == 'lunar_solar' else '음력 윤달'),
                'is_converted': is_converted,
                'converted_solar': f"{year}년 {month}월 {day}일" if is_converted else None,
                'log': converted_log
            },
            'scenarios_comparison': scenarios_comparison,
            'daeun_info': {
                'daeun_su': daeun_info['daeun_su'],
                'direction': daeun_info['direction'],
                'closest_term': daeun_info['closest_term']
            },
            'yongsin_info': fortune_res['yongsin_info'],
            'fortune_scores': fortune_res['fortune_scores'],
            'decades_analysis': fortune_res['decades_analysis'],
            'gender': '남성' if gender == 'male' else '여성',
            'solar_correction': results.get('solar_correction')
        }
        
        return jsonify(payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run locally on 5000 port
    app.run(debug=True, host='127.0.0.1', port=5000)
