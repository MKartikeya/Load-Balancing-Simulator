import tkinter as tk
import socket
import threading
import time
from queue import Queue

packet_id = 0
packet_id_timestamp = {}
packet_id_timestamp_lock = threading.Lock()
avg_response_time = 0
alpha = 0.25  
pack_sent = 0
pack_rec = 0
pack_sent_lock = threading.Lock()
packet_rec_lock = threading.Lock()

def send_requests(client_socket, rps):
    global packet_id
    global packet_id_timestamp
    global avg_response_time ,pack_rec ,pack_sent
    interval = 1 / rps
    while True:
        try:
            start_time = time.time()
            packet = "{},{},{}".format(entry_client_ip.get(), entry_name.get(), packet_id)
            with packet_id_timestamp_lock:
                packet_id_timestamp[packet_id] = start_time
            with pack_sent_lock: 
                packet_id += 1
                pack_sent += 1
            client_socket.sendall(packet.encode('utf-8'))
            time.sleep(max(0, interval - (time.time() - start_time)))  
        except Exception as e:
            print("Error during request: {}".format(e))
            break


def receive_responses(client_socket):
    global packet_id_timestamp, avg_response_time, alpha, pack_rec, packet_id_timestamp_lock
    while True:
        try:
            response = client_socket.recv(1024).decode('utf-8')
            if not response:
                break
            _,load_id,client_ip, client_name, packet_id = response.split(",",4)
            # print("Received response: {}".format(response))
            # try:
            #     packet_id
            try:
                response_time = time.time() 
                with packet_id_timestamp_lock:
                    response_time = response_time - packet_id_timestamp[int(packet_id)]
                    with packet_rec_lock:
                        pack_rec += 1
                    del packet_id_timestamp[int(packet_id)]
                avg_response_time = alpha * response_time + (1 - alpha) * avg_response_time
                label_avg_response_time.config(text="Average Response Time: {:.4f} seconds".format(avg_response_time))
            except Exception as e:
                print("Error updating response time: {}".format(e)) 
                pass
        except Exception as e:
            print("Error receiving response: {}".format(e))
            break


def connect_to_load_balancer():
    client_name = entry_name.get()
    client_ip = entry_client_ip.get()
    load_balancer_ip = entry_lb_ip.get()

    if not client_name or not client_ip or not load_balancer_ip:
        label_status.config(text="All fields are required!", fg="red")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((load_balancer_ip, 20001))

        message = "Client,{},{}".format(client_name, client_ip)
        client_socket.sendall(message.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        if response != "1":
            ip_addresses = response.split(",")
            label_status.config(text=", ".join(ip_addresses), fg="green")
        else:
            label_status.config(text="Connection successful! Please enter RPS.", fg="green")

            entry_name.grid_forget()
            entry_client_ip.grid_forget()
            entry_lb_ip.grid_forget()
            label_name.grid_forget()
            label_client_ip.grid_forget()
            label_lb_ip.grid_forget()
            btn_connect.grid_forget()

            entry_rps.config(state="normal")
            btn_start_requests.config(state="normal")

            label_throughput.grid(row=1, column=0, columnspan=2, pady=10)
            root.client_socket = client_socket

    except Exception as e:
        label_status.config(text="Connection failed: {}".format(e), fg="red")

def calculate_throughput():
    global pack_sent, pack_rec
    while True:
        time.sleep(1)
        if pack_sent > 0:
            throughput_percentage = min(100.0,(pack_rec*(100.0) / pack_sent)) 
        else:
            throughput_percentage = 0.0
        label_throughput.config(text="Throughput: {:.2f}%".format(throughput_percentage))
        with pack_sent_lock:
            pack_sent = 0   
        with packet_rec_lock:
            pack_rec = 0


def exit_client():
    """
    Closes the client socket and exits the application.
    """
    while True:
        if input() == "exit":
            root.destroy()
            exit()

def start_sending_requests():
    rps = int(entry_rps.get())
    client_socket = root.client_socket

    entry_rps.grid_forget()
    label_rps.grid_forget()
    btn_start_requests.grid_forget()
    label_status.grid_forget()

    label_avg_response_time.grid(row=0, column=0, columnspan=2, pady=10)

    threading.Thread(target=send_requests, args=(client_socket, rps), daemon=True).start()
    threading.Thread(target=receive_responses, args=(client_socket,), daemon=True).start()


# GUI setup
root = tk.Tk()
root.title("Client Setup")

label_name = tk.Label(root, text="Client Name:")
label_name.grid(row=0, column=0, padx=10, pady=5)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1, padx=10, pady=5)

label_client_ip = tk.Label(root, text="Client IP Address:")
label_client_ip.grid(row=1, column=0, padx=10, pady=5)
entry_client_ip = tk.Entry(root)
entry_client_ip.grid(row=1, column=1, padx=10, pady=5)

label_lb_ip = tk.Label(root, text="Load Balancer IP Address:")
label_lb_ip.grid(row=2, column=0, padx=10, pady=5)
entry_lb_ip = tk.Entry(root)
entry_lb_ip.grid(row=2, column=1, padx=10, pady=5)

btn_connect = tk.Button(root, text="Connect", command=connect_to_load_balancer)
btn_connect.grid(row=3, column=0, columnspan=2, pady=10)

label_status = tk.Label(root, text="")
label_status.grid(row=4, column=0, columnspan=2, pady=10)

label_rps = tk.Label(root, text="Requests Per Second:")
label_rps.grid(row=5, column=0, padx=10, pady=5)
entry_rps = tk.Entry(root)
entry_rps.grid(row=5, column=1, padx=10, pady=5)
entry_rps.config(state="disabled")

btn_start_requests = tk.Button(root, text="Start Sending Requests", command=start_sending_requests)
btn_start_requests.grid(row=6, column=0, columnspan=2, pady=10)
btn_start_requests.config(state="disabled")

label_avg_response_time = tk.Label(root, text="The client hasn't received any responses yet.")
label_avg_response_time.grid_forget()  

label_throughput = tk.Label(root, text="Throughput: 0.00%")
label_throughput.grid_forget() 




threading.Thread(target=exit_client, daemon=True).start()
threading.Thread(target=calculate_throughput, daemon=True).start()
root.mainloop()