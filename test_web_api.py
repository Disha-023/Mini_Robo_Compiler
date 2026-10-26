"""Quick integration test to verify web_api/app.py works end-to-end with the existing compiler."""
from web_api.app import app, run_robolang, RunRequest

def test_api():
    # 1. Test square program
    square_src = """START
PEN_DOWN
REPEAT 4 {
    MOVE 4
    TURN RIGHT
}
PEN_UP
POSITION
STOP"""
    
    req = RunRequest(source=square_src)
    res = run_robolang(req)
    
    assert res["success"] is True, f"Failed: {res.get('errors')}"
    assert len(res["tokens"]) > 0, "No tokens returned"
    assert res["ast"] is not None, "No AST returned"
    assert len(res["ir"]) > 0, "No IR returned"
    assert len(res["generated_code"]) > 0, "No generated code"
    assert len(res["robot_history"]) > 0, "No robot history"
    assert res["final_state"] is not None, "No final state"
    assert res["final_state"]["x"] == 0
    assert res["final_state"]["y"] == 0
    assert res["final_state"]["direction"] == "NORTH"
    print("[PASS] Square program run test passed!")
    print(f"  History events count: {len(res['robot_history'])}")
    print(f"  Final state: {res['final_state']}")

    # 2. Test invalid syntax
    invalid_src = """START
MOVE 5
INVALID_SYNTAX_WITHOUT_STOP"""
    req_bad = RunRequest(source=invalid_src)
    res_bad = run_robolang(req_bad)
    assert res_bad["success"] is False
    assert len(res_bad["errors"]) > 0
    print(f"[PASS] Error handling test passed: {res_bad['errors'][0]}")

    # 3. Test basic movement
    move_src = """START
PEN_DOWN
MOVE 5
TURN RIGHT
MOVE 3
PEN_UP
MOVE 2
POSITION
STOP"""
    req_move = RunRequest(source=move_src)
    res_move = run_robolang(req_move)
    assert res_move["success"] is True
    assert res_move["final_state"]["x"] == 5
    assert res_move["final_state"]["y"] == 5
    assert res_move["final_state"]["direction"] == "EAST"
    print("[PASS] Basic movement test passed!")
    print(f"  Final state: {res_move['final_state']}")

    print("\nALL WEB API INTEGRATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_api()
