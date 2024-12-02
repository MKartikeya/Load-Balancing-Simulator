class LRTScheduler:
    def __init__(self):
        """
        Initializes the Least Response Time scheduler.
        """
        self.servers = []  

    def update_servers(self, server_details):
        # for server in server_details:
        #     server.setdefault("queue_length", 0)  
        self.servers = server_details

    def get_next_server(self):

        if not self.servers:
            return None

        for server in self.servers:
            server["effective_response_time"] = (
                server["queue_length"] * server["processing_time"]
            )

        self.servers.sort(key=lambda x: x["effective_response_time"])
        selected_server = self.servers[0]

        selected_server["queue_length"] += 1

        return selected_server
