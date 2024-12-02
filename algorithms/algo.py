import Queue

class my_scheduler:
    def __init__(self):
        self.servers = []   #list of servers 
        self.current_load = []  #list of current loads on the servers
        self.capacity = []  #list of capacities of the servers
        self.q = [Queue.Queue() for _ in range(self.servers.size)]   #list of last 5 response times
        self.avg_resp_time = [] 
        
        
    def update_servers(self, server_list):
        #self.servers = server_list
        #handle queue , avg response time array when server is added or removed
        return

    def get_next_server(self):
        if not self.servers:
            return None

        min_index = 0
        min_resp_time = self.avg_resp_time[0]
        for i in range(1,len(self.servers)):
            if self.avg_resp_time[i] < min_resp_time and self.current_load[i] < self.capacity[i]:
                min_resp_time = self.avg_resp_time[i]
                min_index = i
        return self.servers[min_index]
    
    def add_job(self, server_no):
        self.current_load[server_no] += 1
    
    def remove_job(self, server_no , resp_time):
        self.current_load[server_no] -= 1
        if self.q[server_no].size() < 5:
            self.q[server_no].put(resp_time)
            self.avg_resp_time[server_no] = (self.avg_resp_time[server_no]*(self.q[server_no].size()-1) + resp_time)/self.q[server_no].size()
        elif self.q[server_no].size() == 5:
            self.avg_resp_time[server_no] = (self.avg_resp_time[server_no]*(self.q[server_no].size()) + resp_time - self.q[server_no].get())/self.q[server_no].size()
            self.q[server_no].put(resp_time)
            
