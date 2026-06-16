import os
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def get_summary():
    response = requests.get(f"{BASE_URL}/summary")
    return response.json()


def get_categories():
    response = requests.get(f"{BASE_URL}/categories")
    return response.json()


def ask_agent(question):
    response = requests.post(
        f"{BASE_URL}/agent/chat",
        json={"question": question}
    )
    return response.json()


def upload_file(file):
    file_type = getattr(file, 'type', 'application/octet-stream')
    files = {
        "file": (
            file.name,
            file,
            file_type
        )
    }
    response = requests.post(
        f"{BASE_URL}/upload/",
        files=files
    )
    return response.json()


def get_transactions():
    response = requests.get(f"{BASE_URL}/transactions")
    return response.json()


def clear_transactions():
    response = requests.delete(f"{BASE_URL}/transactions")
    return response.json()


def get_insights():
    response = requests.get(f"{BASE_URL}/insights")
    return response.json()