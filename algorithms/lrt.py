# File: algorithms/LRT.py

class LRT:
    def __init__(self):
        self.servers = []

    def update_servers(self, server_details):
        self.servers = sorted(server_details, key=lambda x: x["response_time"])  # Sort servers by response time

    def get_next_server(self):
        return self.servers[0] if self.servers else None
