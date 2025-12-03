#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated baseline training script
Run this before launching attacks to train the anomaly detector
Compatible with both Python 2 and 3
"""

from __future__ import print_function
import sys
import random
import time

# Python 2/3 compatibility
if sys.version_info[0] >= 3:
    import xmlrpc.client as xmlrpclib
    raw_input = input
else:
    import xmlrpclib

server = xmlrpclib.ServerProxy('http://localhost:8000')

def get_hosts():
    """Get available hosts"""
    try:
        return server.get_all_hosts_info()
    except Exception as e:
        print("Erro ao conectar: %s" % e)
        return None

def weighted_choice(choices, weights):
    """Weighted random choice compatible with Python 2 and 3"""
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in zip(choices, weights):
        if upto + weight >= r:
            return choice
        upto += weight
    return choices[-1]

def run_training_phase(duration=600, intensity='medium'):
    """
    Run automated training phase
    intensity: 'low', 'medium', 'high'
    """
    hosts = get_hosts()
    if not hosts or len(hosts) < 2:
        print("Erro: Necessario pelo menos 2 hosts")
        return False
    
    print("\n" + "=" * 70)
    print(" " * 20 + "BASELINE TRAINING PHASE")
    print("=" * 70)
    print("Duracao: %d segundos (%.1f minutos)" % (duration, duration/60.0))
    print("Intensidade: %s" % intensity.upper())
    print("Hosts disponiveis: %d" % len(hosts))
    print("=" * 70)
    print("")
    print("IMPORTANTE: Certifique-se de que o controlador Ryu esta rodando!")
    print("O modelo HalfSpaceTrees aprendera este comportamento como 'normal'.")
    print("")
    print("=" * 70 + "\n")
    
    # Set traffic parameters based on intensity
    if intensity == 'low':
        min_interval = 5
        max_interval = 15
        packets_per_flow = (3, 10)
    elif intensity == 'medium':
        min_interval = 2
        max_interval = 8
        packets_per_flow = (5, 15)
    else:  # high
        min_interval = 1
        max_interval = 5
        packets_per_flow = (10, 20)
    
    start_time = time.time()
    flows_generated = 0
    packets_sent = 0
    
    # Protocol distribution
    protocols = ['tcp', 'udp', 'icmp']
    protocol_weights = [0.4, 0.4, 0.2]  # TCP, UDP, ICMP
    
    try:
        while (time.time() - start_time) < duration:
            # Select random source and destination
            src_host = random.choice(list(hosts.keys()))
            dst_ip = random.choice(list(hosts.values()))
            
            # Random protocol with weights
            protocol = weighted_choice(protocols, protocol_weights)
            
            count = random.randint(packets_per_flow[0], packets_per_flow[1])
            
            if protocol == 'tcp':
                # Common TCP ports
                port = random.choice([22, 80, 443, 8080, 3306, 5432, 6379])
                command = "hping3 -c %d -S -p %d -i u100000 %s > /dev/null 2>&1 &" % (
                    count, port, dst_ip
                )
            elif protocol == 'udp':
                # Common UDP ports
                port = random.choice([53, 123, 161, 514, 1900])
                command = "hping3 -c %d --udp -p %d -i u100000 %s > /dev/null 2>&1 &" % (
                    count, port, dst_ip
                )
            else:  # icmp
                count = random.randint(3, 8)
                interval = random.uniform(0.5, 2.0)
                command = "ping -c %d -i %.1f %s > /dev/null 2>&1 &" % (
                    count, interval, dst_ip
                )
            
            try:
                server.run_command_on_host(src_host, command)
                flows_generated += 1
                packets_sent += count
                
                # Progress update every 10 flows
                if flows_generated % 10 == 0:
                    elapsed = time.time() - start_time
                    remaining = duration - elapsed
                    progress = (elapsed / duration) * 100
                    print("[%3.0f%%] Flows: %d | Packets: %d | Remaining: %.0fs" % (
                        progress, flows_generated, packets_sent, remaining
                    ))
            except Exception as e:
                print("Erro ao enviar trafego: %s" % e)
            
            # Wait before next flow
            time.sleep(random.uniform(min_interval, max_interval))
    
    except KeyboardInterrupt:
        print("\n\nTreinamento interrompido pelo usuario.")
    
    print("\n" + "=" * 70)
    print(" " * 20 + "TRAINING PHASE COMPLETE")
    print("=" * 70)
    print("Duracao total: %.1f minutos" % ((time.time() - start_time) / 60.0))
    print("Flows gerados: %d" % flows_generated)
    print("Pacotes enviados: %d" % packets_sent)
    if (time.time() - start_time) > 0:
        print("Taxa media: %.1f flows/min" % (flows_generated / ((time.time() - start_time) / 60.0)))
    print("=" * 70)
    print("")
    print("O modelo agora esta treinado com trafego normal.")
    print("Voce pode lancar ataques usando o botmaster.py")
    print("")
    
    return True

def main():
    print("=" * 70)
    print(" " * 15 + "TREINAMENTO DE BASELINE - CAPYMOA")
    print("=" * 70)
    
    duration = 600
    intensity = 'medium'
    
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except:
            print("Uso: python train_baseline.py [duracao_em_segundos] [intensidade]")
            return
    else:
        print("\n1. Treinamento rapido (5 minutos, low)")
        print("2. Treinamento padrao (10 minutos, medium)")
        print("3. Treinamento extenso (20 minutos, medium)")
        print("4. Treinamento completo (30 minutos, high)")
        print("5. Personalizado")
        
        choice = raw_input("\nEscolha (1-5): ")
        
        if choice == '1':
            duration = 300
            intensity = 'low'
        elif choice == '2':
            duration = 600
            intensity = 'medium'
        elif choice == '3':
            duration = 1200
            intensity = 'medium'
        elif choice == '4':
            duration = 1800
            intensity = 'high'
        elif choice == '5':
            try:
                duration = int(raw_input("Duracao (segundos): "))
                intensity = raw_input("Intensidade (low/medium/high): ").lower()
                if intensity not in ['low', 'medium', 'high']:
                    intensity = 'medium'
            except:
                print("Entrada invalida.")
                return
        else:
            print("Opcao invalida.")
            return
    
    if len(sys.argv) > 2:
        intensity = sys.argv[2].lower()
    
    run_training_phase(duration, intensity)

if __name__ == '__main__':
    main()
