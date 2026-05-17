import sys
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

from src.graph.nodes.metrics.memory_node import memory_node
from src.graph.nodes.metrics.requests_node import requests_node
from src.graph.nodes.metrics.status_node import status_node

STATE = {
    "project": "4349a73b-c225-4f16-8628-9c7b4f52a34f",
    "service": "804a3e4b-33b2-4157-9d71-e9dd17bc0f1f",
    "environment_id": "1b11f681-da18-484c-8307-24a9f443bc3e",
}

def run(name, fn):
    print(f"\n{'='*40}")
    print(f"Testando: {name}")
    try:
        result = fn(STATE)
        print(f"OK -> {result}")
    except Exception as e:
        print(f"ERRO -> {e}")

run("memory_node", memory_node)
run("requests_node", requests_node)
run("status_node", status_node)
