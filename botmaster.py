#!/usr/bin/python2
# -*- coding: utf-8 -*-
import xmlrpclib
import random
import re
import os
import sys
from attack_logger import AttackLogger

server = xmlrpclib.ServerProxy('http://localhost:8000')


attack_logger = AttackLogger()

controlled_hosts = set()
available_hosts = {}

def clean_environment():
    print "\n--- Limpeza de Ambiente ---"
    
    files_to_remove = [
        '../controller/attack_flows.csv', 
        '../controller/controller_preds.csv'    
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print "Arquivo removido: %s" % file_path
            except OSError as e:
                print "Erro ao remover %s: %s" % (file_path, e)
        else:
            print "Arquivo limpo (nao existia): %s" % file_path
            
    print "Logs anteriores apagados com sucesso."
    
    global attack_logger
    attack_logger = AttackLogger()
    print "AttackLogger reinicializado.\n"

def update_available_hosts():
    global available_hosts
    try:
        host_info = server.get_all_hosts_info()
        available_hosts = host_info
        return True
    except Exception as e:
        print "erro ao conectar ao servidor Mininet. Verifique se run_topology.py esta em execucao."
        print "erro: %s" % e
        return False

def host_management_menu():
    global controlled_hosts
    while True:
        print "\n--- gerenciamento de hosts ---"
        print "1. listar hosts"
        print "2. adicionar hosts (manual)"
        print "3. adicionar N hosts aleatorios"
        print "4. adicionar TODOS os hosts disponiveis"
        print "5. listar hosts controlados ('infectados')"
        print "6. voltar ao menu principal"
        choice = raw_input("Escolha (1-6): ")

        if choice == '1':
            if update_available_hosts():
                if not available_hosts:
                    print "nenhum host encontrado."
                    continue
                print "hosts diponiveis"
                for host_name, ip in sorted(available_hosts.items()):
                    status = "(controlado)" if host_name in controlled_hosts else "(nao controlado)"
                    print "  - %s ip: %s %s" % (host_name, ip, status)

        elif choice == '2':
            if not update_available_hosts(): continue
            infectable_hosts = [h for h in available_hosts.keys() if h not in controlled_hosts]
            if not infectable_hosts:
                print "nenhum host disponivel para infeccao."
                continue
            print "hosts disponiveis para infeccao:"
            for h in sorted(infectable_hosts):
                print "  - %s (IP: %s)" % (h, available_hosts[h])
            hosts_to_infect_input = raw_input("digite os hosts para adicionar (separados por espaco, ex: h1 h2): ")
            hosts_list = hosts_to_infect_input.replace(',', ' ').split()
            added_count = 0
            for host_name in hosts_list:
                host_name = host_name.strip()
                if not host_name: continue
                if host_name in infectable_hosts:
                    controlled_hosts.add(host_name)
                    print "  - host %s adicionado aos hosts controlados." % host_name
                    added_count += 1
                elif host_name in controlled_hosts:
                    print "  - host %s ja esta sob controle." % host_name
                else:
                    print "  - host '%s' nao e um alvo valido." % host_name
            if added_count > 0:
                print "%d host(s) adicionado(s) com sucesso." % added_count

        elif choice == '3':
            if not update_available_hosts(): continue
            infectable_hosts = [h for h in available_hosts.keys() if h not in controlled_hosts]
            if not infectable_hosts:
                print "nenhum host disponivel para infeccao."
                continue
            try:
                num_to_add_str = raw_input("quantos hosts aleatorios adicionar? ")
                num_to_add = int(num_to_add_str)
            except ValueError:
                print "numero invalido."
                continue
            if num_to_add <= 0:
                print "o numero deve ser positivo."
                continue
            if num_to_add > len(infectable_hosts):
                print "voce so pode adicionar no maximo %d hosts. Adicionando todos os disponiveis." % len(infectable_hosts)
                num_to_add = len(infectable_hosts)
            hosts_to_add = random.sample(infectable_hosts, num_to_add)
            for host_name in hosts_to_add:
                controlled_hosts.add(host_name)
            print "%d hosts aleatorios adicionados ao controle." % num_to_add

        elif choice == '4':
            if not update_available_hosts(): continue
            infectable_hosts = [h for h in available_hosts.keys() if h not in controlled_hosts]
            if not infectable_hosts:
                print "todos os hosts ja estao sob seu controle."
                continue
            count = 0
            for host_name in infectable_hosts:
                controlled_hosts.add(host_name)
                count += 1
            print "%d hosts disponiveis foram adicionados ao controle." % count

        elif choice == '5':
            if not controlled_hosts:
                print "nenhum host controlado"
            else:
                print "hosts controlados (%d): %s" % (len(controlled_hosts), ', '.join(sorted(list(controlled_hosts))))

        elif choice == '6':
            print "voltando ao menu principal..."
            break
        else:
            print "escolha invalida."

def select_attackers():
    attackers = []
    if not controlled_hosts:
        print "nenhum host controlado."
        return []
    while True:
        print "\n--- selecionar atacantes (de %d controlados) ---" % len(controlled_hosts)
        print "1. um host especifico"
        print "2. n hosts aleatorios"
        print "3. todos os hosts controlados"
        choice = raw_input("Escolha (1-3): ")
        hosts_controlados_lista = sorted(list(controlled_hosts))
        if choice == '1':
            print "hosts controlados:"
            for i, host_name in enumerate(hosts_controlados_lista):
                print "  %d: %s (IP: %s)" % (i + 1, host_name, available_hosts.get(host_name, "N/A"))
            try:
                host_choice = raw_input("digite o nome do host (ex: h1): ")
                if host_choice in controlled_hosts:
                    attackers = [host_choice]
                    break
                else:
                    print "host invalido ou nao controlado."
            except (IndexError, ValueError):
                print "selecao invalida."
        elif choice == '2':
            try:
                num_str = raw_input("quantos hosts aleatorios? ")
                num = int(num_str)
                if num <= 0:
                    print "numero deve ser positivo."
                elif num > len(hosts_controlados_lista):
                    print "numero maior que os hosts controlados (%d). Usando todos." % len(hosts_controlados_lista)
                    attackers = hosts_controlados_lista
                    break
                else:
                    attackers = random.sample(hosts_controlados_lista, num)
                    break
            except ValueError:
                print "numero invalido."
        elif choice == '3':
            attackers = hosts_controlados_lista
            break
        else:
            print "opcao invalida."
    print "atacantes selecionados: %s" % ', '.join(attackers)
    return attackers

def launch_test_menu():
    if not controlled_hosts:
        print "nenhum host controlado. infecte hosts primeiro usando o Menu 1."
        return
    if not update_available_hosts():
        return
    print "\n--- lancar teste de trafego ---"
    print "alvos disponiveis :"
    available_targets = {}
    for host_name, ip in available_hosts.items():
        if host_name not in controlled_hosts:
            available_targets[host_name] = ip
    if not available_targets:
        print "nenhum alvo disponivel. todos os hosts estao sob seu controle."
        return
    for host_name, ip in sorted(available_targets.items()):
        print "  - %s (IP: %s)" % (host_name, ip)
    target_ip = raw_input("Digite o IP do alvo (ex: 10.0.0.4): ")
    if not any(ip == target_ip for ip in available_targets.values()):
        print "aviso: O IP '%s' nao e um alvo valido ou pertence a um host controlado." % target_ip
        if raw_input("deseja continuar mesmo assim? (s/n): ").lower() != 's':
            print "teste cancelado."
            return
    print "\n--- Tipo de Trafego ---"
    print "1. ping (ICMP Flood)"
    print "2. hping3 (TCP SYN Flood)"
    print "3. hping3 (UDP Flood)"
    print "4. iperf (TCP/UDP Flood)"
    test_type = raw_input("Escolha (1-4): ")
    command_template = ""
    attack_type_name = ""
    port = None
    duration = None
    if test_type == '1':
        duration = raw_input("duracao do ping em segundos (ex: 10): ")
        command_template = "timeout %s ping -f %s &" % (duration, target_ip)
        attack_type_name = "ping"
    elif test_type == '2':
        duration = raw_input("duracao do ataque em segundos (ex: 10): ")
        port = raw_input("porta alvo (ex: 80): ")
        command_template = "timeout %s hping3 -S --flood -p %s %s &" % (duration, port, target_ip)
        attack_type_name = "tcp_syn"
    elif test_type == '3':
        duration = raw_input("duracao do ataque em segundos (ex: 10): ")
        port = raw_input("Porta alvo (ex: 53): ")
        command_template = "timeout %s hping3 --udp --flood -p %s %s &" % (duration, port, target_ip)
        attack_type_name = "udp"
    elif test_type == '4':
        duration = raw_input("duracao do iperf em segundos (ex: 10): ")
        command_template = "iperf -c %s -t %s &" % (target_ip, duration)
        attack_type_name = "iperf"
    else:
        return
    
    attackers = select_attackers()
    if not attackers:
        print "nenhum atacante selecionado. teste cancelado."
        return
    
    attackers_ips = []
    for att in attackers:
        if att in available_hosts:
            attackers_ips.append(available_hosts[att])
        else:
            attackers_ips.append(att)

    print "\niniciando teste de %s contra %s..." % (', '.join(attackers), target_ip)
    for host_name in attackers:
        command = command_template
        print "  - enviando comando para %s..." % host_name
        try:
            response = server.run_command_on_host(host_name, command)
            print "    resposta de %s: %s" % (host_name, response)
        except Exception as e:
            print "    erro ao contatar %s: %s" % (host_name, e)
    print "comandos de teste enviados."
    try:
        attack_id = attack_logger.log_attack(
            attack_type=attack_type_name,
            attackers=attackers_ips,
            target_ip=target_ip,
            target_port=port,
            duration=duration
        )
        print "\nataque registrado no CSV com ID: %s" % attack_id
    except Exception as e:
        print "\nerro ao registrar ataque: %s" % e

def view_attack_report():
    print "\n--- relatorio de ataques ---"
    try:
        report = attack_logger.generate_report()
        print report
    except Exception as e:
        print "erro ao gerar relatorio: %s" % e

def compare_metrics():
    print "\n--- Comparacao com Controlador ---"
    controller_csv = raw_input("Caminho do CSV do controlador: ")
    if not controller_csv:
        controller_csv = "../controller/controller_preds.csv"
    
    try:
        result = attack_logger.compare_with_controller(controller_csv)
        print result
    except Exception as e:
        print "Erro na comparacao: %s" % e

def main():
    if not update_available_hosts():
        print "nao foi possivel conectar ao servidor Mininet. encerrando."
        return
    
    if raw_input("Deseja limpar os logs de testes anteriores? [S/n]: ").lower() != 'n':
        clean_environment()
    
    print "Controlador conectado com sucesso."
    while True:
        print "\n====== menu principal do controlador ======"
        print "1. gerenciamento de hosts"
        print "2. lancar teste de trafego"
        print "3. visualizar relatorio de ataques"
        print "4. comparar metricas (IA vs Real)"
        print "5. sair"
        choice = raw_input("Escolha (1-5): ")
        if choice == '1':
            host_management_menu()
        elif choice == '2':
            launch_test_menu()
        elif choice == '3':
            view_attack_report()
        elif choice == '4':
            compare_metrics()
        elif choice == '5':
            break
        else:
            pass

if __name__ == "__main__":
    main()
