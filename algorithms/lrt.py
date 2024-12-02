# File: algorithms/LRT.py

class LRT:
    def __init__(self):
        """
        Initializes the Least Response Time scheduler.
        """
        self.servers = []

    def update_servers(self, server_details):
        """
        Updates the list of servers with their latest response times.
        Args:
            server_details (list): A list of dictionaries containing server information, including response times.
        """
        self.servers = sorted(server_details, key=lambda x: x["response_time"])  # Sort servers by response time

    def get_next_server(self):
        """
        Selects the server with the least response time.
        Returns:
            dict: The server with the lowest response time or None if no servers are available.
        """
        return self.servers[0] if self.servers else None
