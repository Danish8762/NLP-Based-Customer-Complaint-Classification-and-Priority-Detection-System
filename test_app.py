import json
from app import app

def run_tests():
    client = app.test_client()

    print("=" * 60)
    print("RUNNING AUTOMATED FLASK APPLICATION TESTS")
    print("=" * 60)

    # Test 1: GET /
    res_get = client.get('/')
    print(f"Test 1: GET / -> Status {res_get.status_code}")
    assert res_get.status_code == 200, "GET / failed"
    assert b"Customer Complaint Classification" in res_get.data

    # Test 2: POST /analyze with empty input
    res_empty = client.post('/analyze', data=json.dumps({'complaint': ''}), content_type='application/json')
    print(f"Test 2: Empty input -> Status {res_empty.status_code}, Response: {res_empty.get_json()['error']}")
    assert res_empty.status_code == 400

    # Test 3: POST /analyze with short input
    res_short = client.post('/analyze', data=json.dumps({'complaint': 'hi'}), content_type='application/json')
    print(f"Test 3: Short input -> Status {res_short.status_code}, Response: {res_short.get_json()['error']}")
    assert res_short.status_code == 400

    # Test 4: Realistic Complaints
    test_cases = [
        "My payment was deducted twice but my order was cancelled.",
        "My package has not arrived for five days.",
        "The application crashes whenever I try to login.",
        "The product I received is damaged.",
        "I cannot reset my password.",
        "I want to know how I can change my account password."
    ]

    print("\nTest 4: Real Complaint Inferences:")
    for tc in test_cases:
        res = client.post('/analyze', data=json.dumps({'complaint': tc}), content_type='application/json')
        assert res.status_code == 200, f"Failed for {tc}"
        data = res.get_json()
        print(f"\n  Input: \"{tc}\"")
        print(f"    * Category   : {data['category']} ({data['confidence']*100:.1f}%)")
        print(f"    * Priority   : {data['priority']} ({data['priority_confidence']*100:.1f}%)")
        print(f"    * Sentiment  : {data['sentiment']} (Compound: {data['compound_score']})")
        print(f"    * Clean Text : \"{data['preprocessed_text']}\"")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
