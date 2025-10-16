import llmgraphbuilder
import socket
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import threading  # For UDP listener thread
import time


def get_local_ip():
    """Find the local network IP of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


app = Flask(__name__)
CORS(app)  # Enable if needed for cross-origin


@app.route("/run", methods=["POST"])
def run():
    data = request.json
    start_time = time.time()  # Start the clock
    result = llmgraphbuilder.prompt(data)
    end_time = time.time()  # End the clock
    latency = end_time - start_time  # Calculate latency in seconds
    return jsonify({"result": result, "latency": latency})


def udp_discovery_listener():
    """UDP listener for discovery broadcasts."""
    DISCOVERY_PORT = 5001
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', DISCOVERY_PORT))

    local_ip = get_local_ip()
    local_port = 5000  # HTTP port

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        if message == "FLASK_DISCOVERY":
            response = f"FLASK_SERVER:{local_ip}:{local_port}"
            sock.sendto(response.encode('utf-8'), addr)


if __name__ == "__main__":
    # Start UDP discovery in a background thread
    llmgraphbuilder.delete_memory()
    threading.Thread(target=udp_discovery_listener, daemon=True).start()
    local_ip = get_local_ip()
    print(f"Server running at: http://{local_ip}:5000/run")
    app.run(host="0.0.0.0", port=5000)