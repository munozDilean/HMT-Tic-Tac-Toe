
"""
test_api.py - Tic-Tac-Toe API Test Suite
Run with: python test_api.py
Make sure the Django server is running first: python manage.py runserver
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000/api"

RESET  = "\033[0m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"

passed = 0
failed = 0


def post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test(name, status, response, checks):
    global passed, failed
    errors = []

    for description, condition in checks:
        if not condition:
            errors.append(description)

    if not errors:
        print(f"  {GREEN}✓{RESET} {name}")
        passed += 1
    else:
        print(f"  {RED}✗{RESET} {name}")
        for e in errors:
            print(f"      {YELLOW}→ Failed: {e}{RESET}")
        print(f"      Response ({status}): {json.dumps(response)}")
        failed += 1


# ---------------------------------------------------------------------------

print(f"\n{BOLD}=== Health Check ==={RESET}")

status, resp = get("/health/")
test(
    "Server is running and responding",
    status, resp,
    [
        ("Status code is 200", status == 200),
        ("Returns status ok", resp.get("status") == "ok"),
        ("Reports neural weights status", "neural_weights_loaded" in resp),
    ]
)

# ---------------------------------------------------------------------------

print(f"\n{BOLD}=== AI Move — Core Behaviour ==={RESET}")

status, resp = post("/move/", {
    "board": [None]*9,
    "player": "X"
})
test(
    "AI makes a move on an empty board",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Returns a move index", "move" in resp),
        ("Move is in range 0-8", 0 <= resp.get("move", -1) <= 8),
        ("Returns updated board", len(resp.get("board", [])) == 9),
        ("Returns encoded state (18 values)", len(resp.get("encoded_state", [])) == 18),
        ("Game not over yet", resp.get("game_over") == False),
    ]
)

status, resp = post("/move/", {
    "board": ["X", "X", None, None, None, None, None, None, None],
    "player": "X"
})
test(
    "AI plays winning move (X wins top row)",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Plays position 2 to win", resp.get("move") == 2),
        ("Reports winner as X", resp.get("winner") == "X"),
        ("Reports game over", resp.get("game_over") == True),
    ]
)

status, resp = post("/move/", {
    "board": ["O", "O", None, None, None, None, None, None, None],
    "player": "X"
})
test(
    "AI blocks opponent winning move (O top row threat)",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Blocks position 2", resp.get("move") == 2),
        ("Game not over after block", resp.get("game_over") == False),
    ]
)

status, resp = post("/move/", {
    "board": [None, None, None, "O", "O", None, None, None, None],
    "player": "X"
})
test(
    "AI blocks opponent winning move (O middle row threat)",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Blocks position 5", resp.get("move") == 5),
    ]
)

status, resp = post("/move/", {
    "board": ["O", None, None, None, "O", None, None, None, None],
    "player": "X"
})
test(
    "AI blocks diagonal threat (O top-left to bottom-right)",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Blocks position 8", resp.get("move") == 8),
    ]
)


print(f"\n{BOLD}=== AI Move — Mode Selection ==={RESET}")

status, resp = post("/move/", {
    "board": [None]*9,
    "player": "X",
    "mode": "minimax"
})
test(
    "Minimax mode works",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Reports ai_type as minimax", resp.get("ai_type") == "minimax"),
    ]
)

status, resp = post("/move/", {
    "board": [None]*9,
    "player": "X",
    "mode": "neural"
})
test(
    "Neural mode works",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Reports ai_type as neural", resp.get("ai_type") == "neural"),
    ]
)

status, resp = post("/move/", {
    "board": [None]*9,
    "player": "X",
    "mode": "auto"
})
test(
    "Auto mode works",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Reports an ai_type", resp.get("ai_type") in ("minimax", "neural")),
    ]
)


print(f"\n{BOLD}=== AI Move — O as AI Player ==={RESET}")

status, resp = post("/move/", {
    "board": [None, None, None, "O", "O", None, None, None, None],
    "player": "O"
})
test(
    "AI plays as O and wins middle row",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Plays position 5 to win", resp.get("move") == 5),
        ("Reports winner as O", resp.get("winner") == "O"),
    ]
)

print(f"\n{BOLD}=== Validate Endpoint ==={RESET}")

status, resp = post("/validate/", {
    "board": ["X", "X", "X", None, None, None, None, None, None]
})
test(
    "Detects X win on top row",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Winner is X", resp.get("winner") == "X"),
        ("Game is over", resp.get("game_over") == True),
        ("No available moves reported as list", isinstance(resp.get("available_moves"), list)),
    ]
)

status, resp = post("/validate/", {
    "board": [None, None, None, "O", "O", "O", None, None, None]
})
test(
    "Detects O win on middle row",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Winner is O", resp.get("winner") == "O"),
        ("Game is over", resp.get("game_over") == True),
    ]
)

status, resp = post("/validate/", {
    "board": ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
})
test(
    "Detects a draw",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Winner is draw", resp.get("winner") == "draw"),
        ("Game is over", resp.get("game_over") == True),
    ]
)

status, resp = post("/validate/", {
    "board": ["X", "O", None, None, None, None, None, None, None]
})
test(
    "Detects in-progress game",
    status, resp,
    [
        ("Status 200", status == 200),
        ("No winner yet", resp.get("winner") is None),
        ("Game not over", resp.get("game_over") == False),
        ("Reports 7 available moves", len(resp.get("available_moves", [])) == 7),
    ]
)

status, resp = post("/validate/", {
    "board": [None]*9
})
test(
    "Empty board is valid with 9 available moves",
    status, resp,
    [
        ("Status 200", status == 200),
        ("9 available moves", len(resp.get("available_moves", [])) == 9),
    ]
)


print(f"\n{BOLD}=== Error Handling ==={RESET}")

status, resp = post("/move/", {
    "board": ["X", "X"],
    "player": "X"
})
test(
    "Rejects board with fewer than 9 cells",
    status, resp,
    [("Status 400", status == 400)]
)

status, resp = post("/move/", {
    "board": ["X", "X", "X", "X", "X", "X", "X", "X", "X", "X"],
    "player": "X"
})
test(
    "Rejects board with more than 9 cells",
    status, resp,
    [("Status 400", status == 400)]
)

status, resp = post("/move/", {
    "board": ["X", "Z", None, None, None, None, None, None, None],
    "player": "X"
})
test(
    "Rejects invalid cell value",
    status, resp,
    [("Status 400", status == 400)]
)

status, resp = post("/move/", {
    "board": [None]*9,
    "player": "Z"
})
test(
    "Rejects invalid player value",
    status, resp,
    [("Status 400", status == 400)]
)

status, resp = post("/move/", {
    "board": ["X", "X", "X", "O", "O", None, None, None, None],
    "player": "O"
})
test(
    "Rejects move on already-won board",
    status, resp,
    [("Status 400", status == 400)]
)

status, resp = post("/move/", {
    "board": ["X", "O", "X", "X", "O", "O", "O", "X", "X"],
    "player": "X"
})
test(
    "Rejects move on a full board (draw)",
    status, resp,
    [("Status 400", status == 400)]
)

status, resp = post("/move/", {})
test(
    "Rejects empty request body",
    status, resp,
    [("Status 400", status == 400)]
)


print(f"\n{BOLD}=== Encoding ==={RESET}")

status, resp = post("/validate/", {
    "board": ["X", "O", None, None, None, None, None, None, None]
})
encoded = resp.get("encoded_state", [])
test(
    "X encodes to [1,0], O to [0,1], null to [0,0]",
    status, resp,
    [
        ("Status 200", status == 200),
        ("Encoded state has 18 values", len(encoded) == 18),
        ("X at position 0 encodes to [1,0]", encoded[:2] == [1.0, 0.0]),
        ("O at position 1 encodes to [0,1]", encoded[2:4] == [0.0, 1.0]),
        ("null at position 2 encodes to [0,0]", encoded[4:6] == [0.0, 0.0]),
    ]
)


print(f"\n{BOLD}{'='*40}{RESET}")
total = passed + failed
print(f"{BOLD}Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET} out of {total} tests")

if failed == 0:
    print(f"{GREEN}{BOLD}All tests passed!{RESET}")
else:
    print(f"{YELLOW}Some tests failed — check the output above.{RESET}")
print()
