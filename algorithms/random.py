import random

class RandomScheduler:
    def __init__(self):
        self.servers = []

    def update_servers(self, server_list):
        self.servers = server_list

    def add_server(self, server_ip):
        if server_ip not in self.servers:
            self.servers.append(server_ip)

    def remove_server(self, server_ip):
        if server_ip in self.servers:
            self.servers.remove(server_ip)

    def get_next_server(self):
        if not self.servers:
            raise Exception("No available servers.")
        return random.choice(self.servers)
