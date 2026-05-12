import socket
import requests
import os

def check_kafka():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock.connect_ex(("localhost", 9092)) == 0

def check_api():
    try:
        res = requests.get("http://localhost:8080/health")
        return res.status_code == 200
    except:
        return False

def check_file():
    return os.path.exists("data.csv")

TOOLS = {
    "kafka": check_kafka,
    "api": check_api,
    "file": check_file
}