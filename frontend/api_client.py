import os
import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:5000")


class APIError(Exception):
    def __init__(self, message, status=None, details=None):
        self.message = message
        self.status = status
        self.details = details
        super().__init__(message)


def _headers():
    token = st.session_state.get("access_token")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _handle_response(resp):
    try:
        payload = resp.json()
    except ValueError:
        raise APIError("Server se invalid response aaya", resp.status_code)

    if not resp.ok or not payload.get("success", True):
        raise APIError(
            payload.get("message", "Kuch error aaya"),
            resp.status_code,
            payload.get("details"),
        )
    return payload.get("data")


def _request(method, path, json=None, params=None, timeout=8):
    try:
        resp = requests.request(
            method, f"{API_URL}{path}", json=json, params=params,
            headers=_headers(), timeout=timeout,
        )
    except requests.ConnectionError:
        raise APIError("Backend se connect nahi ho paya. Backend chal raha hai kya?")
    except requests.Timeout:
        raise APIError("Backend response dene me bahut time le raha hai")

    return _handle_response(resp)


# ---------- Auth ----------
def register(email, password):
    return _request("POST", "/api/auth/register", json={"email": email, "password": password})


def login(email, password):
    return _request("POST", "/api/auth/login", json={"email": email, "password": password})


def get_me():
    return _request("GET", "/api/auth/me")


# ---------- Habits ----------
def list_habits(page=1, per_page=20):
    return _request("GET", "/api/habits", params={"page": page, "per_page": per_page})


def create_habit(name, category="general"):
    return _request("POST", "/api/habits", json={"name": name, "category": category})


def delete_habit(habit_id):
    return _request("DELETE", f"/api/habits/{habit_id}")


def checkin(habit_id, mood, note=None):
    return _request("POST", f"/api/habits/{habit_id}/checkin", json={"mood": mood, "note": note})


def get_checkins(habit_id):
    return _request("GET", f"/api/habits/{habit_id}/checkins")

def get_leaderboard():
    return _request("GET", "/api/habits/leaderboard")


def get_insights(habit_id):
    return _request("GET", f"/api/habits/{habit_id}/insights")