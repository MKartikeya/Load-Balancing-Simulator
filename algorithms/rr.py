#round robin algorithm implementation
# round_robin.py

class RoundRobinScheduler:
    def __init__(self):
        self.servers = []
        self.current_index = -1

    def update_servers(self, server_list):
        self.servers = server_list
        self.current_index = -1

    def get_next_server(self):
        if not self.servers:
            return None
        #print the number of servers
        print("Number of servers: ",len(self.servers))
        self.current_index = (self.current_index + 1) % len(self.servers)
        return self.servers[self.current_index]
