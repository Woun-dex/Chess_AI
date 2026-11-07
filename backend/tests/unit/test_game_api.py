"""Integration tests for Game API endpoints."""

from fastapi.testclient import TestClient


def test_create_game_api(client: TestClient) -> None:
    response = client.post(
        "/api/v1/games/",
        json={
            "white_player_id": "alice",
            "black_player_id": "bot",
            "opponent_type": "random",
            "bot_skill_level": 5,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "game_id" in data
    assert data["status"] == "in_progress"
    assert data["turn"] == "white"
    assert data["version"] == 1


def test_make_move_and_fetch_game_api(client: TestClient) -> None:
    # 1. Create game
    create_resp = client.post(
        "/api/v1/games/",
        json={"white_player_id": "alice", "black_player_id": "bot", "opponent_type": "random"},
    )
    game_id = create_resp.json()["game_id"]

    # 2. Make valid move e2e4
    move_resp = client.post(
        f"/api/v1/games/{game_id}/moves",
        json={"move": "e2e4", "player_id": "alice", "expected_version": 1},
    )
    assert move_resp.status_code == 200
    move_data = move_resp.json()
    # Player move + bot reply = 2 moves
    assert len(move_data["moves"]) == 2
    assert move_data["moves"][0]["uci"] == "e2e4"

    # 3. Retrieve game
    get_resp = client.get(f"/api/v1/games/{game_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["game_id"] == game_id


def test_make_move_optimistic_concurrency_conflict(client: TestClient) -> None:
    create_resp = client.post("/api/v1/games/", json={})
    game_id = create_resp.json()["game_id"]

    # Stale version 99
    response = client.post(
        f"/api/v1/games/{game_id}/moves",
        json={"move": "e2e4", "expected_version": 99},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "CONCURRENCY_CONFLICT"


def test_make_illegal_move_returns_422(client: TestClient) -> None:
    create_resp = client.post("/api/v1/games/", json={})
    game_id = create_resp.json()["game_id"]

    # Illegal move on turn 1
    response = client.post(
        f"/api/v1/games/{game_id}/moves",
        json={"move": "e2e5", "expected_version": 1},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "ILLEGAL_MOVE"


def test_resign_game_api(client: TestClient) -> None:
    create_resp = client.post(
        "/api/v1/games/",
        json={"white_player_id": "alice", "black_player_id": "bot", "opponent_type": "random"},
    )
    game_id = create_resp.json()["game_id"]

    resign_resp = client.post(
        f"/api/v1/games/{game_id}/resign",
        json={"player_id": "alice"},
    )
    assert resign_resp.status_code == 200
    data = resign_resp.json()
    assert data["status"] == "resigned"
    assert data["winner"] == "black"
