import tkinter as tk
import socket
import threading
import time
from queue import Queue

def send_requests(client_socket, rps):
    """
    Sends packets at the specified rate (requests per second) and measures response time.
    """
    interval = 1 / rps
    while True:
        try:
            start_time = time.time()
            # the packet should contain the following fields: client ip address, client name, timestamp, processing time, request type
            packet = "{},{},{},{},{}".format(entry_client_ip.get(), entry_name.get(), time.time(),
                                             entry_proc_time.get(), "PING")
            # send the packet to the load balancer
            client_socket.sendall(packet.encode('utf-8'))
            response = client_socket.recv(1024)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print("Response received in {:.2f} ms".format(response_time))
            time.sleep(max(0, interval - (time.time() - start_time)))  # Maintain the rate
        except Exception as e:
            print("Error during request: {}".format(e))
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

        # Send client details
        message = "Client,{},{}".format(client_name, client_ip)
        client_socket.sendall(message.encode('utf-8'))

        # Receive response
        response = client_socket.recv(1024).decode('utf-8')
        if response != "1":
            ip_addresses = response.split(",")
            label_status.config(text=", ".join(ip_addresses), fg="green")
        else:
            label_status.config(text="Connection successful! Please enter RPS and processing time.", fg="green")

            # Remove previous fields
            entry_name.grid_forget()
            entry_client_ip.grid_forget()
            entry_lb_ip.grid_forget()
            label_name.grid_forget()
            label_client_ip.grid_forget()
            label_lb_ip.grid_forget()
            btn_connect.grid_forget()

            # Enable the RPS and processing time fields after successful connection
            entry_rps.config(state="normal")
            entry_proc_time.config(state="normal")
            btn_start_requests.config(state="normal")

            # Save the socket for later use in the RPS thread
            root.client_socket = client_socket

    except Exception as e:
        label_status.config(text="Connection failed: {}".format(e), fg="red")


def start_sending_requests():
    rps = int(entry_rps.get())
    client_socket = root.client_socket
    processing_time = int(entry_proc_time.get())

    # Start sending requests at the specified rate
    threading.Thread(target=send_requests, args=(client_socket, rps), daemon=True).start()

    label_status.config(
        text="Started sending requests at {} RPS with {} ms processing time.".format(rps, processing_time), fg="green")


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

# Entry fields for RPS and processing time
label_rps = tk.Label(root, text="Requests Per Second:")
label_rps.grid(row=5, column=0, padx=10, pady=5)
entry_rps = tk.Entry(root)
entry_rps.grid(row=5, column=1, padx=10, pady=5)
entry_rps.config(state="disabled")  # Disabled initially

label_proc_time = tk.Label(root, text="Processing Time (ms):")
label_proc_time.grid(row=6, column=0, padx=10, pady=5)
entry_proc_time = tk.Entry(root)
entry_proc_time.grid(row=6, column=1, padx=10, pady=5)
entry_proc_time.config(state="disabled")  # Disabled initially

btn_start_requests = tk.Button(root, text="Start Sending Requests", command=start_sending_requests)
btn_start_requests.grid(row=7, column=0, columnspan=2, pady=10)
btn_start_requests.config(state="disabled")  # Disabled initially

root.mainloop()