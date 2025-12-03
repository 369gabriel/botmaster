#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xmlrpclib
import time
import random
import sys

# Configurações do Gerador
SERVER_URL = "http://localhost:8000"
DURATION = 300          # Duração total do teste em segundos
SLEEP_INTERVAL = 3      # Intervalo entre geração de novos fluxos
TRAFFIC_TYPES = ['icmp', 'http', 'voip'] 

def get_proxy():
    try:
        return xmlrpclib.ServerProxy(SERVER_URL)
    except Exception as e:
        print "Erro ao conectar com servidor RPC: %s" % e
        sys.exit(1)

def generate_icmp(proxy, hosts_list, ips):
    src = random.choice(hosts_list)
    dst = random.choice(hosts_list)
    while src == dst:
        dst = random.choice(hosts_list)
    
    dst_ip = ips[dst]
    count = random.randint(3, 10) # 3 a 10 pings
    
    cmd = "ping -c %d -i 0.5 %s &" % (count, dst_ip)
    print "[NORMAL] ICMP: %s -> %s (%d pings)" % (src, dst, count)
    proxy.run_command_on_host(src, cmd)

def generate_http(proxy, hosts_list, ips):
    # Simula tráfego Web (TCP curto)
    server = random.choice(hosts_list)
    client = random.choice(hosts_list)
    while server == client:
        client = random.choice(hosts_list)
        
    server_ip = ips[server]
    
    # Inicia servidor iperf temporário (modo one-off)
    proxy.run_command_on_host(server, "iperf -s -p 5001 -1 &")
    
    # Cliente envia dados (simulando download de arquivo)
    bytes_to_send = random.choice(['500K', '1M', '2M'])
    cmd = "iperf -c %s -p 5001 -n %s &" % (server_ip, bytes_to_send)
    
    print "[NORMAL] HTTP (Simulado): %s baixando %s de %s" % (client, bytes_to_send, server)
    proxy.run_command_on_host(client, cmd)

def generate_voip(proxy, hosts_list, ips):
    # Simula VoIP (UDP constante, baixa banda)
    server = random.choice(hosts_list)
    client = random.choice(hosts_list)
    while server == client:
        client = random.choice(hosts_list)
        
    server_ip = ips[server]
    
    # Servidor UDP
    proxy.run_command_on_host(server, "iperf -s -u -p 5002 -1 &")
    
    # Cliente envia stream de 64k (audio comum) por 5 segundos
    duration = 5
    cmd = "iperf -c %s -u -p 5002 -b 64k -t %d &" % (server_ip, duration)
    
    print "[NORMAL] VoIP: %s chamando %s (UDP 64k)" % (client, server)
    proxy.run_command_on_host(client, cmd)

def main():
    proxy = get_proxy()
    
    print "Conectando ao Mininet via XML-RPC..."
    try:
        hosts_info = proxy.get_all_hosts_info()
    except Exception:
        print "Nao foi possivel obter lista de hosts. O Mininet esta rodando?"
        sys.exit(1)
        
    hosts_list = hosts_info.keys()
    if len(hosts_list) < 2:
        print "Erro: Precisa de pelo menos 2 hosts para gerar trafego."
        sys.exit(1)

    print "Hosts encontrados: %s" % hosts_list
    print "Iniciando geracao de trafego normal por %d segundos..."

    start_time = time.time()
    
    try:
        while time.time() - start_time < DURATION:
            traffic_type = random.choice(TRAFFIC_TYPES)
            
            if traffic_type == 'icmp':
                generate_icmp(proxy, hosts_list, hosts_info)
            elif traffic_type == 'http':
                generate_http(proxy, hosts_list, hosts_info)
            elif traffic_type == 'voip':
                generate_voip(proxy, hosts_list, hosts_info)
            
            # Pausa aleatória para não sobrecarregar e parecer humano
            wait = random.uniform(1, SLEEP_INTERVAL)
            time.sleep(wait)
            
    except KeyboardInterrupt:
        print "\nParando gerador de trafego..."

    print "Fim da simulacao de trafego normal."

if __name__ == "__main__":
    main()
