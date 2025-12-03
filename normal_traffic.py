#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Normal Traffic Generator for Mininet
Simulates realistic network baseline traffic
"""

import xmlrpclib
import random
import time
import threading

server = xmlrpclib.ServerProxy('http://localhost:8000')

class NormalTrafficGenerator:
    def __init__(self):
        self.running = False
        self.threads = []
        self.hosts = {}
        
    def update_hosts(self):
        """Get available hosts from Mininet"""
        try:
            self.hosts = server.get_all_hosts_info()
            return True
        except Exception as e:
            print "Erro ao conectar ao servidor: %s" % e
            return False
    
    def ping_traffic(self, duration=300):
        """Generate periodic ping traffic between random hosts"""
        print "[Normal Traffic] Iniciando ping traffic..."
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration:
            if len(self.hosts) < 2:
                time.sleep(5)
                continue
            
            # Select random source and destination
            src_host = random.choice(self.hosts.keys())
            dst_ip = random.choice(self.hosts.values())
            
            # Normal ping: 1 ping per second, small count
            ping_count = random.randint(3, 10)
            interval = random.uniform(0.5, 2.0)
            
            command = "ping -c %d -i %.1f %s > /dev/null 2>&1 &" % (ping_count, interval, dst_ip)
            
            try:
                server.run_command_on_host(src_host, command)
                print "  [Ping] %s -> %s (%d pings)" % (src_host, dst_ip, ping_count)
            except Exception as e:
                print "  [Erro] Ping failed: %s" % e
            
            # Wait before next ping (realistic interval)
            time.sleep(random.uniform(5, 15))
    
    def http_traffic(self, duration=300):
        """Simulate HTTP requests using curl or wget"""
        print "[Normal Traffic] Iniciando HTTP traffic..."
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration:
            if len(self.hosts) < 2:
                time.sleep(5)
                continue
            
            src_host = random.choice(self.hosts.keys())
            dst_ip = random.choice(self.hosts.values())
            
            # Simulate HTTP request (port 80)
            # Using hping3 to simulate TCP connections
            command = "hping3 -c 5 -S -p 80 %s > /dev/null 2>&1 &" % dst_ip
            
            try:
                server.run_command_on_host(src_host, command)
                print "  [HTTP] %s -> %s:80" % (src_host, dst_ip)
            except Exception as e:
                print "  [Erro] HTTP failed: %s" % e
            
            time.sleep(random.uniform(10, 30))
    
    def dns_traffic(self, duration=300):
        """Simulate DNS queries"""
        print "[Normal Traffic] Iniciando DNS traffic..."
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration:
            if len(self.hosts) < 2:
                time.sleep(5)
                continue
            
            src_host = random.choice(self.hosts.keys())
            dst_ip = random.choice(self.hosts.values())
            
            # Simulate DNS query (UDP port 53)
            num_queries = random.randint(1, 3)
            command = "hping3 -c %d --udp -p 53 %s > /dev/null 2>&1 &" % (num_queries, dst_ip)
            
            try:
                server.run_command_on_host(src_host, command)
                print "  [DNS] %s -> %s:53 (%d queries)" % (src_host, dst_ip, num_queries)
            except Exception as e:
                print "  [Erro] DNS failed: %s" % e
            
            time.sleep(random.uniform(8, 20))
    
    def ssh_traffic(self, duration=300):
        """Simulate SSH connection attempts"""
        print "[Normal Traffic] Iniciando SSH traffic..."
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration:
            if len(self.hosts) < 2:
                time.sleep(5)
                continue
            
            src_host = random.choice(self.hosts.keys())
            dst_ip = random.choice(self.hosts.values())
            
            # Simulate SSH (TCP port 22)
            command = "hping3 -c 3 -S -p 22 %s > /dev/null 2>&1 &" % dst_ip
            
            try:
                server.run_command_on_host(src_host, command)
                print "  [SSH] %s -> %s:22" % (src_host, dst_ip)
            except Exception as e:
                print "  [Erro] SSH failed: %s" % e
            
            time.sleep(random.uniform(20, 60))
    
    def mixed_traffic(self, duration=300):
        """Generate mixed protocol traffic"""
        print "[Normal Traffic] Iniciando mixed traffic..."
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration:
            if len(self.hosts) < 2:
                time.sleep(5)
                continue
            
            src_host = random.choice(self.hosts.keys())
            dst_ip = random.choice(self.hosts.values())
            
            # Random protocol selection
            protocol_choice = random.choice(['http', 'https', 'dns', 'ssh', 'ftp'])
            
            if protocol_choice == 'http':
                port = 80
                count = random.randint(3, 8)
            elif protocol_choice == 'https':
                port = 443
                count = random.randint(3, 8)
            elif protocol_choice == 'dns':
                port = 53
                count = random.randint(1, 5)
            elif protocol_choice == 'ssh':
                port = 22
                count = random.randint(2, 5)
            else:  # ftp
                port = 21
                count = random.randint(2, 4)
            
            command = "hping3 -c %d -S -p %d %s > /dev/null 2>&1 &" % (count, port, dst_ip)
            
            try:
                server.run_command_on_host(src_host, command)
                print "  [%s] %s -> %s:%d" % (protocol_choice.upper(), src_host, dst_ip, port)
            except Exception as e:
                print "  [Erro] Traffic failed: %s" % e
            
            time.sleep(random.uniform(5, 15))
    
    def iperf_background_traffic(self, duration=60):
        """Generate background TCP traffic using iperf"""
        print "[Normal Traffic] Iniciando iperf background traffic..."
        
        if len(self.hosts) < 2:
            print "  [Erro] Necessario pelo menos 2 hosts"
            return
        
        # Select server and clients
        host_list = self.hosts.keys()
        server_host = host_list[0]
        server_ip = self.hosts[server_host]
        
        # Start iperf server
        server_cmd = "iperf -s > /dev/null 2>&1 &"
        try:
            server.run_command_on_host(server_host, server_cmd)
            print "  [iPerf Server] Started on %s (%s)" % (server_host, server_ip)
            time.sleep(2)
        except Exception as e:
            print "  [Erro] Failed to start iperf server: %s" % e
            return
        
        # Start clients from other hosts
        start_time = time.time()
        while self.running and (time.time() - start_time) < duration:
            client_host = random.choice([h for h in host_list if h != server_host])
            
            # Low bandwidth, realistic traffic
            bandwidth = random.randint(100, 500)  # Kbps
            test_duration = random.randint(5, 15)
            
            client_cmd = "iperf -c %s -b %dK -t %d > /dev/null 2>&1 &" % (
                server_ip, bandwidth, test_duration
            )
            
            try:
                server.run_command_on_host(client_host, client_cmd)
                print "  [iPerf Client] %s -> %s (%dKbps, %ds)" % (
                    client_host, server_ip, bandwidth, test_duration
                )
            except Exception as e:
                print "  [Erro] iPerf client failed: %s" % e
            
            time.sleep(random.uniform(10, 20))
    
    def start(self, duration=300, traffic_types=None):
        """Start generating normal traffic"""
        if not self.update_hosts():
            print "Falha ao obter hosts. Verifique se run_topology.py esta rodando."
            return
        
        if len(self.hosts) < 2:
            print "Necessario pelo menos 2 hosts para gerar trafego."
            return
        
        self.running = True
        
        if traffic_types is None:
            traffic_types = ['ping', 'http', 'dns', 'mixed']
        
        print "\n" + "=" * 60
        print "INICIANDO GERACAO DE TRAFEGO NORMAL"
        print "=" * 60
        print "Duracao: %d segundos" % duration
        print "Hosts disponiveis: %d" % len(self.hosts)
        print "Tipos de trafego: %s" % ', '.join(traffic_types)
        print "=" * 60 + "\n"
        
        # Start traffic generators in separate threads
        if 'ping' in traffic_types:
            t = threading.Thread(target=self.ping_traffic, args=(duration,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        if 'http' in traffic_types:
            t = threading.Thread(target=self.http_traffic, args=(duration,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        if 'dns' in traffic_types:
            t = threading.Thread(target=self.dns_traffic, args=(duration,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        if 'ssh' in traffic_types:
            t = threading.Thread(target=self.ssh_traffic, args=(duration,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        if 'mixed' in traffic_types:
            t = threading.Thread(target=self.mixed_traffic, args=(duration,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        if 'iperf' in traffic_types:
            t = threading.Thread(target=self.iperf_background_traffic, args=(duration,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        print "\nTrafego normal iniciado. Pressione Ctrl+C para parar.\n"
        
        try:
            # Wait for duration or user interrupt
            time.sleep(duration)
        except KeyboardInterrupt:
            print "\n\nParando geracao de trafego..."
        finally:
            self.stop()
    
    def stop(self):
        """Stop all traffic generation"""
        self.running = False
        for t in self.threads:
            t.join(timeout=1)
        print "Trafego normal encerrado."

def main():
    generator = NormalTrafficGenerator()
    
    print "=" * 60
    print "GERADOR DE TRAFEGO NORMAL"
    print "=" * 60
    print "1. Trafego leve (5 minutos)"
    print "2. Trafego moderado (10 minutos)"
    print "3. Trafego intenso (15 minutos)"
    print "4. Trafego continuo (30 minutos)"
    print "5. Personalizado"
    print "6. Sair"
    
    choice = raw_input("\nEscolha (1-6): ")
    
    if choice == '1':
        duration = 300
        traffic_types = ['ping', 'http', 'dns']
    elif choice == '2':
        duration = 600
        traffic_types = ['ping', 'http', 'dns', 'mixed']
    elif choice == '3':
        duration = 900
        traffic_types = ['ping', 'http', 'dns', 'ssh', 'mixed']
    elif choice == '4':
        duration = 1800
        traffic_types = ['ping', 'http', 'dns', 'ssh', 'mixed', 'iperf']
    elif choice == '5':
        try:
            duration = int(raw_input("Duracao em segundos: "))
            print "\nTipos disponiveis: ping, http, dns, ssh, mixed, iperf"
            types_input = raw_input("Digite os tipos (separados por espaco): ")
            traffic_types = types_input.split()
        except:
            print "Entrada invalida."
            return
    elif choice == '6':
        return
    else:
        print "Opcao invalida."
        return
    
    generator.start(duration=duration, traffic_types=traffic_types)

if __name__ == '__main__':
    main()
