#!/usr/bin/python2
import xmlrpclib
import random
import re

server = xmlrpclib.ServerProxy('http://localhost:8000')

controlled_hosts = set()
available_hosts = {}

def update_available_hosts():
    global available_hosts
    try:
        host_info = server.get_all_hosts_info()
        available_hosts = host_info
        return True
    except Exception as e:
        print "Erro ao conectar ao servidor Mininet. Verifique se run_topology.py esta em execucao."
        print "Erro: %s" % e
        return False

def host_management_menu():
    global controlled_hosts

    while True:
        print "\n--- Gerenciamento de Hosts ---"
        print "1. Listar hosts"
        print "2. Adicionar hosts (manual)"
        print "3. Adicionar N hosts aleatorios"
        print "4. Adicionar TODOS os hosts disponiveis"
        print "5. Listar hosts controlados ('infectados')"
        print "6. Voltar ao menu principal"
        choice = raw_input("Escolha (1-6): ")

        if choice == '1':
            print "Buscando hosts na rede..."
            if update_available_hosts():
                if not available_hosts:
                    print "Nenhum host encontrado."
                    continue

                print "Hosts disponiveis na rede:"
                for host_name, ip in sorted(available_hosts.items()):
                    status = "(controlado)" if host_name in controlled_hosts else "(não controlado)"
                    print "  - %s ip: %s %s" % (host_name, ip, status)

        elif choice == '2':
            if not update_available_hosts(): continue
            infectable_hosts = [h for h in available_hosts.keys() if h not in controlled_hosts]
            if not infectable_hosts:
                print "Nenhum host novo disponivel para 'infecção'."
                continue

            print "Hosts disponiveis para 'infecção':"
            for h in sorted(infectable_hosts):
                print "  - %s (IP: %s)" % (h, available_hosts[h])
            hosts_to_infect_input = raw_input("Digite os hosts para adicionar (separados por espaco, ex: h1 h2): ")
            hosts_list = hosts_to_infect_input.replace(',', ' ').split()

            added_count = 0
            for host_name in hosts_list:
                host_name = host_name.strip()
                if not host_name: continue
                if host_name in infectable_hosts:
                    controlled_hosts.add(host_name)
                    print "  - Host %s adicionado aos hosts controlados." % host_name
                    added_count += 1
                elif host_name in controlled_hosts:
                    print "  - Host %s ja esta sob controle." % host_name
                else:
                    print "  - Host '%s' nao e um alvo valido." % host_name
            if added_count > 0:
                print "%d host(s) adicionado(s) com sucesso." % added_count

        elif choice == '3':
            if not update_available_hosts(): continue
            infectable_hosts = [h for h in available_hosts.keys() if h not in controlled_hosts]
            if not infectable_hosts:
                print "Nenhum host novo disponivel para 'infecção'."
                continue
            try:
                num_to_add_str = raw_input("Quantos hosts aleatorios adicionar? ")
                num_to_add = int(num_to_add_str)
            except ValueError:
                print "Numero invalido."
                continue
            if num_to_add <= 0:
                print "O numero deve ser positivo."
                continue
            if num_to_add > len(infectable_hosts):
                print "Voce so pode adicionar no maximo %d hosts. Adicionando todos os disponiveis." % len(infectable_hosts)
                num_to_add = len(infectable_hosts)
            hosts_to_add = random.sample(infectable_hosts, num_to_add)
            for host_name in hosts_to_add:
                controlled_hosts.add(host_name)
            print "%d hosts aleatorios adicionados ao controle." % num_to_add

        elif choice == '4':
            if not update_available_hosts(): continue
            infectable_hosts = [h for h in available_hosts.keys() if h not in controlled_hosts]
            if not infectable_hosts:
                print "Nenhum host novo disponivel para 'infecção'. Todos ja estao controlados."
                continue
            count = 0
            for host_name in infectable_hosts:
                controlled_hosts.add(host_name)
                count += 1
            print "%d hosts disponiveis foram adicionados ao controle." % count

        elif choice == '5':
            if not controlled_hosts:
                print "Nenhum host controlado no momento."
            else:
                print "Hosts controlados (%d): %s" % (len(controlled_hosts), ', '.join(sorted(list(controlled_hosts))))

        elif choice == '6':
            print "Voltando ao menu principal..."
            break
        else:
            print "Escolha invalida."

def select_attackers():
    attackers = []
    if not controlled_hosts:
        print "Nenhum host controlado."
        return []

    while True:
        print "\n--- Selecionar Atacantes (de %d controlados) ---" % len(controlled_hosts)
        print "1. Um host especifico"
        print "2. N hosts aleatorios"
        print "3. Todos os hosts controlados"
        choice = raw_input("Escolha (1-3): ")

        hosts_controlados_lista = sorted(list(controlled_hosts))

        if choice == '1':
            print "Hosts controlados:"
            for i, host_name in enumerate(hosts_controlados_lista):
                print "  %d: %s (IP: %s)" % (i + 1, host_name, available_hosts.get(host_name, "N/A"))
            try:
                host_choice = raw_input("Digite o nome do host (ex: h1): ")
                if host_choice in controlled_hosts:
                    attackers = [host_choice]
                    break
                else:
                    print "Host invalido ou nao controlado."
            except (IndexError, ValueError):
                print "Selecao invalida."

        elif choice == '2':
            try:
                num_str = raw_input("Quantos hosts aleatorios? ")
                num = int(num_str)
                if num <= 0:
                    print "Numero deve ser positivo."
                elif num > len(hosts_controlados_lista):
                    print "Numero maior que os hosts controlados (%d). Usando todos." % len(hosts_controlados_lista)
                    attackers = hosts_controlados_lista
                    break
                else:
                    attackers = random.sample(hosts_controlados_lista, num)
                    break
            except ValueError:
                print "Numero invalido."

        elif choice == '3':
            attackers = hosts_controlados_lista
            break
        else:
            print "Opcao invalida."

    print "Atacantes selecionados: %s" % ', '.join(attackers)
    return attackers

def launch_test_menu():
    if not controlled_hosts:
        print "Nenhum host controlado. 'Infecte' hosts primeiro usando o Menu 1."
        return

    if not update_available_hosts():
        return

    print "\n--- Lancar Teste de Trafego ---"
    print "Alvos disponiveis (apenas hosts nao controlados):"

    available_targets = {}
    for host_name, ip in available_hosts.items():
        if host_name not in controlled_hosts:
            available_targets[host_name] = ip

    if not available_targets:
        print "Nenhum alvo disponivel. (Todos os hosts da rede ja estao sob seu controle)."
        return

    for host_name, ip in sorted(available_targets.items()):
        print "  - %s (IP: %s)" % (host_name, ip)

    target_ip = raw_input("Digite o IP do alvo (ex: 10.0.0.4): ")

    if not any(ip == target_ip for ip in available_targets.values()):
        print "Aviso: O IP '%s' nao e um alvo valido ou pertence a um host controlado." % target_ip
        if raw_input("Deseja continuar mesmo assim? (s/n): ").lower() != 's':
            print "Teste cancelado."
            return

    print "\n--- Tipo de Trafego ---"
    print "1. Ping (ICMP Flood)"
    print "2. hping3 (TCP SYN Flood)"
    print "3. hping3 (UDP Flood)"
    print "4. iperf (TCP/UDP Flood - requer iperf instalado nos hosts)"
    test_type = raw_input("Escolha (1-4): ")
    
    command_template = ""
    if test_type == '1':
        duration = raw_input("Duracao do ping em segundos (ex: 10): ")
        command_template = "timeout %s ping -f %s &" % (duration, target_ip)
        print "Nota: Usando 'ping -f' (flood). O 'timeout' ira parar."
    
    elif test_type == '2':
        duration = raw_input("Duracao do ataque em segundos (ex: 10): ")
        port = raw_input("Porta alvo (ex: 80): ")
        command_template = "timeout %s hping3 -S --flood -p %s %s &" % (duration, port, target_ip)
        print "Nota: 'hping3' deve estar instalado nos hosts (apt-get install hping3)."

    elif test_type == '3':
        duration = raw_input("Duracao do ataque em segundos (ex: 10): ")
        port = raw_input("Porta alvo (ex: 53): ")
        command_template = "timeout %s hping3 --udp --flood -p %s %s &" % (duration, port, target_ip)
        print "Nota: 'hping3' deve estar instalado nos hosts (apt-get install hping3)."

    elif test_type == '4':
        duration = raw_input("Duracao do iperf em segundos (ex: 10): ")
        command_template = "iperf -c %s -t %s &" % (target_ip, duration)
    else:
        print "Tipo invalido. Teste cancelado."
        return

    attackers = select_attackers()

    if not attackers:
        print "Nenhum atacante selecionado. Teste cancelado."
        return

    print "\nIniciando teste de %s contra %s..." % (', '.join(attackers), target_ip)

    for host_name in attackers:
        command = command_template
        print "  - Enviando comando para %s..." % host_name
        try:
            response = server.run_command_on_host(host_name, command)
            print "    Resposta de %s: %s" % (host_name, response)
        except Exception as e:
            print "    Erro ao contatar %s: %s" % (host_name, e)

    print "Comandos de teste enviados."

def main():
    if not update_available_hosts():
        print "Nao foi possivel conectar ao servidor Mininet. Encerrando."
        return

    print "Controlador conectado com sucesso."

    while True:
        print "\n====== Menu Principal do Controlador ======"
        print "1. Gerenciamento de Hosts ('Infeccao')"
        print "2. Lancar Teste de Trafego"
        print "3. Sair"
        choice = raw_input("Escolha (1-3): ")

        if choice == '1':
            host_management_menu()
        elif choice == '2':
            launch_test_menu()
        elif choice == '3':
            print "Encerrando controlador."
            break
        else:
            print "Opcao invalida."

if __name__ == "__main__":
    main()


