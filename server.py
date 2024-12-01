import tkinter as tk
import socket
import threading
from queue import Queue
import time

packet_queue = Queue()
response_time = 0
server_ip = None

def send_server_details(server_socket):
    """
    Sends server efficiency and average response time details to the load balancer.
    """
    global response_time
    efficiency = entry_efficiency.get()
    avg_response_time = entry_response_time.get()
    #set the response time
    response_time = avg_response_time


    if not efficiency or not avg_response_time:
        label_status.config(text="All fields are required!", fg="red")
        return

    try:
        # Send server details to the load balancer
        message = "{},{}".format(efficiency, avg_response_time)
        server_socket.sendall(message.encode('utf-8'))

        # Acknowledge response from the load balancer
        response = server_socket.recv(1024).decode('utf-8')
        if response == "1":
            label_status.config(text="Details sent successfully!", fg="green")
        else:
            label_status.config(text="Error: {}".format(response), fg="red")
    except Exception as e:
        label_status.config(text="Error sending details: {}".format(e), fg="red")


def connect_to_load_balancer():
    """
    Establishes a connection to the load balancer.
    """
    global server_ip
    server_ip = entry_server_ip.get()
    load_balancer_ip = entry_lb_ip.get()

    if not server_ip or not load_balancer_ip:
        label_status.config(text="All fields are required!", fg="red")
        return

    try:
        print('Connecting to load balancer')
        print('Server IP:', server_ip)
        print('Load Balancer IP:', load_balancer_ip)
        # Connect to the load balancer
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((load_balancer_ip, 20001))

        # # Send server IP to the load balancer
        message = "Server,{}".format(server_ip)
        server_socket.sendall(message.encode('utf-8'))
        response = server_socket.recv(1024).decode('utf-8')

        if response == "1":
            label_status.config(text="Connected to Load Balancer! Please enter efficiency and response time.", fg="green")

            # Remove initial connection fields
            label_server_ip.grid_forget()
            entry_server_ip.grid_forget()
            label_lb_ip.grid_forget()
            entry_lb_ip.grid_forget()
            btn_connect.grid_forget()

            # Enable efficiency and response time input fields
            label_efficiency.grid(row=2, column=0, padx=10, pady=5)
            entry_efficiency.grid(row=2, column=1, padx=10, pady=5)
            label_response_time.grid(row=3, column=0, padx=10, pady=5)
            entry_response_time.grid(row=3, column=1, padx=10, pady=5)
            btn_send_details.grid(row=4, column=0, columnspan=2, pady=10)

            # Save the socket for later communication
            root.server_socket = server_socket

            while True:
                try:
                    request = server_socket.recv(1024).decode('utf-8')
                    if request:
                        packet_queue.put(request)
                except Exception as e:
                    print("Error receiving data: {}".format(e))
        else:
            label_status.config(text="Error: {}".format(response), fg="red")
    except Exception as e:
        label_status.config(text="Connection failed: {}".format(e), fg="red")

def handle_requests(server_socket):
    """
    Handles incoming requests from the load balancer.
    """
    while True:
        if not packet_queue.empty():
            request = packet_queue.get()
            print("Received request:", request)

            # Process the request
            # Simulate processing time
            time.sleep(response_time)

            # Send response back to the load balancer
            #append the server ip
            response = "{},{}".format(request, server_ip)
            server_socket.sendall(response.encode('utf-8'))


# GUI setup
root = tk.Tk()
root.title("Server Setup")

# Input fields for server connection
label_server_ip = tk.Label(root, text="Server IP Address:")
label_server_ip.grid(row=0, column=0, padx=10, pady=5)
entry_server_ip = tk.Entry(root)
entry_server_ip.grid(row=0, column=1, padx=10, pady=5)

label_lb_ip = tk.Label(root, text="Load Balancer IP Address:")
label_lb_ip.grid(row=1, column=0, padx=10, pady=5)
entry_lb_ip = tk.Entry(root)
entry_lb_ip.grid(row=1, column=1, padx=10, pady=5)

btn_connect = tk.Button(root, text="Connect", command=connect_to_load_balancer)
btn_connect.grid(row=2, column=0, columnspan=2, pady=10)

label_status = tk.Label(root, text="")
label_status.grid(row=3, column=0, columnspan=2, pady=10)

# Input fields for server efficiency and response time
label_efficiency = tk.Label(root, text="Server Efficiency (%):")
entry_efficiency = tk.Entry(root)
label_response_time = tk.Label(root, text="Average Response Time (ms):")
entry_response_time = tk.Entry(root)

btn_send_details = tk.Button(root, text="Send Details", command=lambda: send_server_details(root.server_socket))

# Initially hide efficiency and response time fields
label_efficiency.grid_forget()
entry_efficiency.grid_forget()
label_response_time.grid_forget()
entry_response_time.grid_forget()
btn_send_details.grid_forget()

root.mainloop()


