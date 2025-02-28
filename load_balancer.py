import socket
import time
from threading import Thread, Lock
from queue import Queue
from algorithms.rr import RoundRobinScheduler
from algorithms.random import RandomScheduler
from algorithms.lrtpp import LRTScheduler
from collections import OrderedDict
clients = {}
servers = OrderedDict()
available_client_ips = ["10.0.0.1", "10.0.0.2","10.0.0.3","10.0.0.4","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
available_server_ips = ["10.0.0.1", "10.0.0.2","10.0.0.3","10.0.0.4","10.0.0.5","10.0.0.6","10.0.0.7","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"]
client_sockets = {}
server_sockets = {}
packet_id = 0
alpha = 0.75
packet_queue = Queue()
queue_lock = Lock()
packet_id_lock = Lock()
packet_id_timestamp_lock = Lock()
scheduler = RoundRobinScheduler()
# scheduler = RandomScheduler()
# scheduler = LRTScheduler()
packet_id_timestamp = {}
server_queued_packets = {}

def handle_request(client_socket):
    try:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            return
        if data.startswith("Client"):
            handle_client(client_socket, data)
        elif data.startswith("Server"):
            handle_server(client_socket, data)
        else:
            print("Invalid connection request received: {}".format(data))
    except Exception as e:
        print("Error handling client: {}".format(str(e)))


def handle_client(client_socket, data):
    global packet_id
    global packet_id_timestamp
    global packet_queue
    client_ip = None  
    try:
        _, client_name, client_ip = data.split(",") 
        if client_ip in available_client_ips:
            available_client_ips.remove(client_ip)
            clients[client_ip] = client_name
            client_sockets[client_ip] = client_socket
            client_socket.send("1".encode('utf-8'))  # Acknowledge successful connection
            print("Client {} connected with IP: {}".format(client_name, client_ip))
        else:
            client_socket.send("0".encode('utf-8'))  # Reject connection
            print("Client connection rejected: IP {} not available.".format(client_ip))
            client_socket.close()
            return
    except Exception as e:
        print("Error handling client: {}".format(str(e)))
        client_socket.close()
        return
    try:
        while True:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            else:
                with packet_id_lock:
                    packet_id += 1
                    request = "{},{}".format(packet_id, request)
                    with queue_lock:
                        packet_queue.put({"client_ip": client_ip, "request": request})
                        # print("Request from client {} added to the queue.".format(client_ip))
    except Exception as e:
        print("Error handling client {}: {}".format(client_ip, str(e)))
    finally:
        if client_ip:
            del clients[client_ip]
            del client_sockets[client_ip]
            client_socket.close()
            available_client_ips.append(client_ip)
            available_client_ips.sort()
            print("Client {} disconnected.".format(client_ip))


def handle_server(server_socket, data):
    server_ip = None 
    try:
        _, server_ip = data.split(",",1)
        if server_ip in available_server_ips:
            message ="1"
            server_socket.send(message.encode('utf-8'))
            server_sockets[server_ip] = server_socket
            servers[server_ip] = {"server_ip": server_ip, "efficiency": 0, "response_time":0 ,"socket": server_socket,"load":0,"queue_length":0,"processing_time":0.2}
            print("Server connected with IP: {}".format(server_ip))
        else:
            server_socket.send("0".encode('utf-8'))
            print("Server connection rejected: IP {} not available.".format(server_ip))
            server_socket.close()
            return
    except Exception as e:
        print("Error handling server: {}".format(str(e)))
        server_socket.close()
        return
    # try:
    #     efficiency, response_time = server_socket.recv(1024).decode('utf-8').split(",")
    #     servers[server_ip] = {"server_ip": server_ip, "efficiency": efficiency, "response_time": response_time,"socket": server_socket}
    #     server_socket.send("1".encode('utf-8'))  # Acknowledge successful connection
    #     print("Server configuration received: Efficiency {}, Response Time {}".format(efficiency, response_time))
    # except Exception as e:
    #     print("Error handling server: {}".format(str(e)))
    #     server_socket.close()
    #     return
    try:
        while True:
            response = server_socket.recv(1024).decode('utf-8')
            if not response:
                break
            else:
                # server_queued_packets[server_ip] -= 1
                if response.startswith("RTIME"):
                    try:
                        _,processing_time,server_ip = response.split(",",2)
                        servers[server_ip]["processing_time"] = float(processing_time)
                    except Exception as e:
                        print("Error updating server  details: {}".format(str(e)))
                else:
                    update_servers(response,server_ip)
                    # print(response)
    except Exception as e:
        print("Error handling server {}: {}".format(server_ip, str(e)))
    finally:
        if server_ip:
            del servers[server_ip]
            server_socket.close()
            available_server_ips.append(server_ip)
            available_server_ips.sort()
            print("Server {} disconnected.".format(server_ip))

def update_servers(response,server_ip):
    try:
        _,packet_id_,client_ip,packet = response.split(",",3)
        observed_time = 0
        with packet_id_timestamp_lock:
            observed_time = time.time()-packet_id_timestamp[packet_id_]
            del packet_id_timestamp[packet_id_]
        servers[server_ip]["response_time"] = observed_time*alpha + (1-alpha)*float(servers[server_ip]["response_time"])
        servers[server_ip]["queue_length"] = max(0,servers[server_ip]["queue_length"]-1)
        scheduler.update_servers([details for _, details in servers.items()])
        # print(response)
        client_socket = client_sockets[client_ip]
        client_socket.sendall(response.encode("utf-8"))
    except Exception as e:
        print("Error updating server details: {}".format(str(e)))


def load_balance():
    while True:
        if not packet_queue.empty():
            with queue_lock:
                request = packet_queue.get()

            client_ip = request["client_ip"]
            client_request = request["request"]
            packet_id_, cr = client_request.split(",",1)
            scheduler.update_servers([details for _, details in servers.items()])
            selected_server = scheduler.get_next_server()
            if selected_server:
                try:
                    # server_queued_packets[selected_server["server_ip"]] += 1
                    
                    server_socket = selected_server["socket"]
                    server_socket.sendall(client_request.encode("utf-8"))
                    with packet_id_timestamp_lock:
                        packet_id_timestamp[packet_id_] = time.time()
                    # print("Forwarded request from {} to server {}".format(client_ip, selected_server["server_ip"]))
                except Exception as e:
                    print("Error forwarding request to server: {}".format(str(e)))
            else:
                print("No servers available to handle the request.")

def exit_program():
    while True:
        if input() == "exit":
            print("Exiting program...")
            break
    exit()

def start_load_balancer():
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_socket.bind(('10.0.0.3', 20001))  
    server_socket.listen(5)
    print("Load Balancer is running ...")
    Thread(target=load_balance, daemon=True).start()
    while True:
        client_socket, client_address = server_socket.accept()
        print("New connection from {}.".format(client_address))
        Thread(target=handle_request, args=(client_socket,)).start()


if __name__ == "__main__":
    Thread(target=exit_program, daemon=True).start()
    start_load_balancer()
