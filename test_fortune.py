import unittest
import pandas as pd
from sajupy import SajuCalculator
from saju_mbti import analyze_saju_mbti
from saju_fortune_engine import calculate_daeun_info, find_yongsin_info, simulate_life_fortune

class TestSajuFortuneEngine(unittest.TestCase):
    def setUp(self):
        self.calculator = SajuCalculator()
        try:
            self.calculator.data = pd.read_csv(
                self.calculator.csv_path,
                dtype={'year': int, 'month': int, 'day': int},
                parse_dates=False,
                encoding='utf-8'
            )
        except Exception:
            pass

    def test_daeun_info_yang_male(self):
        # 1995-05-15 14:30 male
        # Year 1995 is 乙亥 (Yin Year). Male: Yin + Male -> Backward (역행)
        res = calculate_daeun_info(1995, 5, 15, 14, 30, 'male', self.calculator)
        self.assertEqual(res['direction_en'], 'backward')
        self.assertGreaterEqual(res['daeun_su'], 1)
        self.assertLessEqual(res['daeun_su'], 10)
        self.assertEqual(len(res['daeuns']), 10)
        
        # Age progression check
        d1 = res['daeuns'][0]
        self.assertEqual(d1['start_age'], res['daeun_su'])
        self.assertEqual(d1['end_age'], res['daeun_su'] + 9)

    def test_daeun_info_yang_female(self):
        # 1995-05-15 14:30 female
        # Yin Year + Female -> Forward (순행)
        res = calculate_daeun_info(1995, 5, 15, 14, 30, 'female', self.calculator)
        self.assertEqual(res['direction_en'], 'forward')

    def test_find_yongsin_info(self):
        element_scores = {'목': 1.0, '화': 4.0, '토': 2.0, '금': 0.5, '수': 2.5}
        y_info = find_yongsin_info(element_scores)
        self.assertEqual(y_info['yongsin'], '금') # lowest
        self.assertEqual(y_info['huisin'], '목')  # second lowest
        self.assertEqual(y_info['gisin'], '화')   # highest
        self.assertIn('용신', y_info['reason'])

    def test_simulate_life_fortune(self):
        daeun_info = calculate_daeun_info(1995, 5, 15, 14, 30, 'male', self.calculator)
        element_scores = {'목': 1.0, '화': 4.0, '토': 2.0, '금': 0.5, '수': 2.5}
        base_scores = {'E': 5.0, 'I': 5.0, 'S': 5.0, 'N': 5.0, 'T': 5.0, 'F': 5.0, 'J': 5.0, 'P': 5.0}
        
        sim_res = simulate_life_fortune(1995, 1995, element_scores, base_scores, daeun_info)
        scores_list = sim_res['fortune_scores']
        
        self.assertEqual(len(scores_list), 90)
        for s in scores_list:
            self.assertTrue(20.0 <= s['score'] <= 98.0)
            self.assertEqual(len(s['mbti']), 4)
            self.assertTrue(all(c in 'EISTFNJP' for c in s['mbti']))
            
        self.assertEqual(len(sim_res['decades_analysis']), 10)

    def test_analyze_saju_mbti_with_gender_and_coords(self):
        res = analyze_saju_mbti(
            year=1995, month=5, day=15, hour=14, minute=30,
            city="Seoul", real_mbti="ENFP", gender="male",
            longitude=126.9780, utc_offset=9
        )
        self.assertIn('gender', res)
        self.assertEqual(res['gender'], 'male')
        self.assertIn('solar_correction', res)
        self.assertIsNotNone(res['solar_correction'])

if __name__ == '__main__':
    unittest.main()
