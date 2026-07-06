import sys
import codecs
from saju_mbti import analyze_saju_mbti, print_results

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def run_test(case_num, year, month, day, hour, minute, city, real_mbti):
    print(f"=== TEST CASE {case_num} ({year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}) ===")
    try:
        results = analyze_saju_mbti(year, month, day, hour, minute, city, real_mbti)
        print_results(results)
        print("STATUS: SUCCESS\n")
    except Exception as e:
        print(f"STATUS: FAILED with error: {e}\n")

if __name__ == "__main__":
    # Test Case 1: Active wood/fire tendency expected (should lean towards extraversion/intuition/feeling)
    run_test(1, 1995, 5, 15, 14, 30, "Seoul", "ENFP")
    
    # Test Case 2: Deep metal/water/earth expected (should lean towards introversion/sensing/thinking)
    run_test(2, 1988, 12, 10, 8, 20, "Seoul", "ISTJ")
