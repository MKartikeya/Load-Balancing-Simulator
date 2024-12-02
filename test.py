# from mininet.net import Mininet
# from mininet.node import Controller
# from mininet.link import TCLink
# from mininet.cli import CLI

# def custom_topology():
#     net = Mininet(controller=Controller, link=TCLink)

#     print("* Creating nodes")
#     h1 = net.addHost('h1')
#     h2 = net.addHost('h2')
#     h3 = net.addHost('h3')
#     h4 = net.addHost('h4')
#     h5 = net.addHost('h5')
#     h6 = net.addHost('h6')
#     h7 = net.addHost('h7')
#     h8 = net.addHost('h8')
#     h9 = net.addHost('h9')
#     h10 = net.addHost('h10')
#     h11 = net.addHost('h11')
#     h12 = net.addHost('h12')
#     h13 = net.addHost('h13')
#     h14 = net.addHost('h14')
#     h15 = net.addHost('h15')
#     h16 = net.addHost('h16')
#     h17 = net.addHost('h17')

#     s1 = net.addSwitch('s1')
#     s2 = net.addSwitch('s2')
#     c0 = net.addController('c0', controller=Controller, ip="127.0.0.1", port=6633)

#     print("* Creating links")
#     hosts_s1 = [h1, h2, h3, h4, h5, h6, h7, h8]
#     for host in hosts_s1:
#         net.addLink(host, s1)

#     net.addLink(s1, h9)
#     net.addLink(h9, s2)

#     hosts_s2 = [h10, h11, h12, h13, h14, h15, h16, h17]
#     for host in hosts_s2:
#         net.addLink(host, s2)

#     print("* Starting network")
#     net.build()
#     c0.start()
#     s1.start([c0])
#     s2.start([c0])

#     print("* Network setup complete")
    
#     # Enter CLI for dynamic control and xterm support
#     CLI(net)

#     print("* Stopping network")
#     net.stop()

# if __name__ == "__main__":
#     custom_topology()
