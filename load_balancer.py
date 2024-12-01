import socket
import time
from threading import Thread

# Dictionary to store client IPs and their names
clients = {}
# Dictionary to store server details: IP, efficiency, and response time
servers = {}
# List of available client IP addresses
available_client_ips = ["10.0.1.1", "10.0.1.3"]
# List of available server IP addresses
available_server_ips = ["10.0.0.1", "10.0.0.2","10.0.0.3","10.0.1.3"]
# Mapping of sockets to IPs (clients or servers)
client_sockets = {}


def handle_request(client_socket):
    """
    Handles communication with a single client.
    """
    client_ip = None  # To track the client's assigned IP
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
    """
    Handles communication with a client.
    """
    client_ip = None  # To track the client's assigned IP
    try:
        _, client_name, client_ip = data.split(",")  # Extract client details
        # check if client IP is available
        if client_ip in available_client_ips:
            available_client_ips.remove(client_ip)
            clients[client_ip] = client_name
            client_sockets[client_ip] = client_socket
            client_socket.send("1".encode('utf-8'))  # Acknowledge successful connection
            print("Client {} connected with IP: {}".format(client_name, client_ip))
        else:
            client_socket.send("0".encode('utf-8'))  # Reject connection
            print("Client connection rejected: IP {} not available.".format(client_ip))
    except Exception as e:
        print("Error handling client: {}".format(str(e)))
    # now recieve the rps and processing time
    try:
        while True:
            # recieve the request
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            else:
                response = "1"
                client_socket.send(response.encode('utf-8'))



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
    server_ip = None  # To track the server's assigned IP
    try:
        _, server_ip = data.split(",")
        # check if server IP is available
        if server_ip in available_server_ips:
            server_socket.send("1".encode('utf-8'))
            available_server_ips.remove(server_ip)
            print("Server {} connected with IP: {}".format(server_ip))
        else:
            server_socket.send("0".encode('utf-8'))
            print("Server connection rejected: IP {} not available.".format(server_ip))
        print(data)

    except Exception as e:
        print("At connection")
        print(data)
        print("Error handling server: {}".format(str(e)))
    try:
        efficiency, response_time = server_socket.recv(1024).decode('utf-8').split(",")
        servers[server_ip] = {"server_ip": server_ip, "efficiency": efficiency, "response_time": response_time,
                              "socket": server_socket}
        server_socket.send("1".encode('utf-8'))  # Acknowledge successful connection
        print("Server configuration received: Efficiency {}, Response Time {}".format(efficiency, response_time))
    except Exception as e:
        print("Error handling server: {}".format(str(e)))
    try:
        while True:
            # recieve the request
            request = server_socket.recv(1024).decode('utf-8')
            if not request:
                break
            # send the request to the client
    except Exception as e:
        print("Over here")
        print("Error handling server {}: {}".format(server_ip, str(e)))
    finally:
        if server_ip:
            del servers[server_ip]
            server_socket.close()
            available_server_ips.append(server_ip)
            available_server_ips.sort()
            print("Server {} disconnected.".format(server_ip))


def start_load_balancer():
    """
    Starts the load balancer to accept client and server connections.
    """
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_socket.bind(('10.0.1.2', 20001))  # Listen on load balancer IP and port
    server_socket.listen(5)
    print("Load Balancer is running and accepting connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print("New connection from {}.".format(client_address))
        Thread(target=handle_request, args=(client_socket,)).start()


if __name__ == "__main__":
    start_load_balancer()
