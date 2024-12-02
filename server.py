import tkinter as tk
from tkinter import ttk
import socket
import threading
from queue import Queue
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Global variables
packet_queue = Queue()
processing_time = 0.5
server_ip = None
buffer_size = 50
packets_received = 0
packets_lost = 0
incoming_packet_rate = 0
packet_id_time_map = {}
load = 0
avg_response_time = 0

lock = threading.Lock()
# packet_queue_lock = threading.Lock()

# Metrics for plotting
metrics = {"Packet Loss": 0, "Load": 0, "Average Response Time": 0, "Incoming Packet Rate": 0}
server_socket = None

def update_efficiency(efficiency):
    """
    Adjust the server's response time based on efficiency slider value.
    """
    global processing_time, server_ip, server_socket
    with lock:
        processing_time = (0.5 * 100) / efficiency
        # send a packet to the server to update the response time with header RTIME
        if server_socket:
            server_socket.sendall("RTIME,{},{}".format(processing_time,server_ip).encode('utf-8'))

        

        # print(processing_time)
        

def update_metrics():
    """
    Updates metrics periodically for plotting.
    """
    while True:
        # with lock:
        metrics["Packet Loss"]  = 0
        if packets_received>0:
            metrics["Packet Loss"] = (packets_lost/packets_received)*100
        metrics["Average Response Time"] = avg_response_time
        metrics["Incoming Packet Rate"] = incoming_packet_rate
        # metrics["Load"] = packet_queue.qsize() / buffer_size
        metrics["Load"] = max(100.0,incoming_packet_rate*100.0/processing_time)


        label_packet_loss.config(text="Packet Loss: {:.2f}%".format(metrics["Packet Loss"]))
        # label_load.config(text="Load: {:.2f}%".format(metrics["Load"]))
        label_avg_response_time.config(text="Average Response Time: {:.2f} seconds".format(metrics["Average Response Time"]))
        # label_incoming_packet_rate.config(text="Incoming Packet Rate: {} packets/second".format(metrics["Incoming Packet Rate"]))   
        
        # print(metrics["Packet Loss"])
        time.sleep(1)
    # root.after(500, update_metrics)

def calculate_packet_rate():
    """
    Calculates the incoming packet rate every second.
    """
    global packets_received, incoming_packet_rate
    while True:
        time.sleep(1)
        with lock:
            incoming_packet_rate = packets_received
            packets_received = 0

def plot_metrics():
    """
    Continuously updates the selected metric in a live plot.
    """
    fig, ax = plt.subplots()
    x_data, y_data = [], []

    def update_plot():
        while True:
            selected_metric = plot_selection.get()
            with lock:
                y_data.append(metrics[selected_metric])
            x_data.append(time.time())
            #keep the most recent points upto a max of 100
            if len(x_data) > 100:
                x_data.pop(0)
                y_data.pop(0)
            ax.clear()
            ax.plot(x_data, y_data, label=selected_metric)
            ax.legend()
            ax.set_title(selected_metric)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(selected_metric)
            canvas.draw()
            time.sleep(1)

    canvas = FigureCanvasTkAgg(fig, root)
    canvas.get_tk_widget().grid(row=7, column=0, columnspan=2)
    threading.Thread(target=update_plot, daemon=True).start()

def listen_for_requests(server_socket):
    global packets_received, packets_lost
    while True:
        try:
            request = server_socket.recv(1024).decode('utf-8')
            if request !="":
                # print("Received request: {}".format(request))
                packet_id, _ = request.split(",", 1)
                # with packet_queue_lock:
                packet_id_time_map[packet_id] = time.time()
                with lock:
                    packets_received += 1
                if packet_queue.qsize() < buffer_size:
                    print(request)
                    packet_queue.put(request)
                else:
                    with lock:
                        packets_lost += 1
        except Exception as e:
            print("Error receiving data: {}".format(e))
            break

def handle_requests(server_socket):
    global avg_response_time
    global processing_time
    while True:
        # with packet_queue_lock:
        if not packet_queue.empty():
            request = packet_queue.get()
            time.sleep(processing_time)
            # print(request)
            # print(processing_time)
            with lock:
                packet_id, _ = request.split(",", 1)
                observed_time = time.time() - packet_id_time_map[packet_id]
                avg_response_time = 0.1 * observed_time + 0.9 * avg_response_time
                del packet_id_time_map[packet_id]
            response = "Request processed by server {},{}".format(server_ip, request)
            # print(response)
            server_socket.sendall(response.encode('utf-8'))

def connect_to_load_balancer():
    global server_ip, server_socket
    server_ip = entry_server_ip.get()
    load_balancer_ip = entry_lb_ip.get()

    if not server_ip or not load_balancer_ip:
        label_status.config(text="All fields are required!", fg="red")
        return

    try:
        print('Connecting to load balancer')
        print('Server IP:', server_ip)
        print('Load Balancer IP:', load_balancer_ip)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((load_balancer_ip, 20001))

        message = "Server,{}".format(server_ip)
        server_socket.sendall(message.encode('utf-8'))
        response = server_socket.recv(1024).decode('utf-8')

        if response == "1":
            label_status.config(text="Connected to Load Balancer! Adjust efficiency and monitor metrics.", fg="green")
            root.server_socket = server_socket
            entry_server_ip.grid_forget()
            entry_lb_ip.grid_forget()
            label_server_ip.grid_forget()
            label_lb_ip.grid_forget()
            btn_connect.grid_forget()
            # label_load.grid(row=8, column=0, padx=10, pady=5)
            label_avg_response_time.grid(row=9, column=0, padx=10, pady=5)
            label_packet_loss.grid(row=7, column=0, padx=10, pady=5)
            # label_incoming_packet_rate.grid(row=10, column=0, padx=10, pady=5)
            # Start listening for requests and handling them
            threading.Thread(target=listen_for_requests, args=(server_socket,), daemon=True).start()
            threading.Thread(target=handle_requests, args=(server_socket,), daemon=True).start()
        else:
            label_status.config(text="Error: {}".format(response), fg="red")
    except Exception as e:
        label_status.config(text="Error connecting to Load Balancer: {}".format(e), fg="red")

def exit_program():
    while True:
        if input() == "exit":
            print("Exiting program...")
            root.quit()
            root.destroy()
            exit()

# GUI setup
root = tk.Tk()
root.title("Server Setup and Metrics")

label_server_ip = tk.Label(root, text="Server IP Address:")
label_server_ip.grid(row=0, column=0, padx=10, pady=5)
entry_server_ip = tk.Entry(root)
entry_server_ip.grid(row=0, column=1, padx=10, pady=5)

label_lb_ip = tk.Label(root, text="Load Balancer IP Address:")
label_lb_ip.grid(row=1, column=0, padx=10, pady=5)
entry_lb_ip = tk.Entry(root)
entry_lb_ip.grid(row=1, column=1, padx=10, pady=5)

btn_connect = tk.Button(root, text="Connect", command=lambda: threading.Thread(target=connect_to_load_balancer).start())
btn_connect.grid(row=2, column=0, columnspan=2, pady=10)

label_status = tk.Label(root, text="Connect to the load balancer to start.")
label_status.grid(row=3, column=0, columnspan=2, pady=10)

label_efficiency = tk.Label(root, text="Adjust Efficiency (%):")
label_efficiency.grid(row=4, column=0, padx=10, pady=5)
efficiency_slider = tk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, command=lambda val: update_efficiency(int(val)))
efficiency_slider.grid(row=4, column=1, padx=10, pady=5)

plot_selection = ttk.Combobox(root, values=list(metrics.keys()))
plot_selection.set("Packet Loss")  # Default selection
plot_selection.grid(row=5, column=0, columnspan=2, pady=10)

btn_plot = tk.Button(root, text="Plot", command=plot_metrics)
btn_plot.grid(row=6, column=0, columnspan=2, pady=10)
efficiency_slider.set(100)

#display packet loss %, load %, average response time, incoming packet rate as labels
label_packet_loss = tk.Label(root, text="Packet Loss: 0%", anchor="center")
label_packet_loss.grid(row=7, column=0, columnspan=2, pady=5)

# label_load = tk.Label(root, text="Load: 0%", anchor="center")
# label_load.grid(row=8, column=0, columnspan=2, pady=5)

label_avg_response_time = tk.Label(root, text="Average Response Time: 0.0 seconds", anchor="center")
label_avg_response_time.grid(row=9, column=0, columnspan=2, pady=5)

# label_incoming_packet_rate = tk.Label(root, text="Incoming Packet Rate: 0 packets/second", anchor="center")
# label_incoming_packet_rate.grid(row=10, column=0, columnspan=2, pady=5)


# Threads
# threading.Thread(target=exit_program, daemon=True).start()
threading.Thread(target=calculate_packet_rate, daemon=True).start()
threading.Thread(target=update_metrics, daemon=True).start()
# root.after(500, update_metrics)
root.mainloop()