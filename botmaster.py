#!/usr/bin/python
# -*- coding: utf-8 -*-


import xmlrpclib
import random
import re

server = xmlrpclib.ServerProxy('http://localhost:8000')

controlled_hosts = set()

def discover_hosts():
    """Descobre novos hosts do servidor RPC."""
    print "Descobrindo hosts da rede Mininet..."
    try:
        host_names = server.get_all_hosts()
        new_hosts = 0
        for name in host_names:
            if name not in controlled_hosts:
                controlled_hosts.add(name)
                new_hosts += 1

        print "Hosts controlados (%d): %s" % (len(controlled_hosts), ', '.join(sorted(list(controlled_hosts))))
        if new_hosts > 0:
            print "%d novos hosts adicionados." % new_hosts
        else:
            print "Nenhum host novo encontrado."

    except Exception as e:
        print "Erro ao conectar ao servidor Mininet. Verifique se run_topology.py esta em execucao."
        print "Erro: %s" % e

def select_attackers():
    """Menu para selecionar quais hosts enviarao trafego."""
    attackers = []
    if not controlled_hosts:
        print "Nenhum host controlado. Descubra os hosts primeiro."
        return []

    print "Hosts disponiveis: %s" % ', '.join(sorted(list(controlled_hosts)))

    while True:
        print "\nSelecione os hosts para gerar trafego:"
        print "  1: Um host especifico"
        print "  2: Um numero aleatorio de hosts"
        print "  3: Todos os hosts controlados"
        choice = raw_input("Escolha (1-3): ")

        if choice == '1':
            host_name = raw_input("Digite o nome do host (ex: h1): ")
            if host_name in controlled_hosts:
                attackers.append(host_name)
                return attackers
            else:
                print "Host invalido ou nao controlado."

        elif choice == '2':
            try:
                num = int(raw_input("Quantos hosts aleatorios? "))
                if num > len(controlled_hosts):
                    print "Numero maior que os hosts disponiveis. Usando todos."
                    return list(controlled_hosts)
                elif num <= 0:
                    print "Numero deve ser positivo."
                else:
                    return random.sample(list(controlled_hosts), num)
            except ValueError:
                print "Entrada invalida. Digite um numero."

        elif choice == '3':
            return list(controlled_hosts)

        else:
            print "Escolha invalida."

def main_loop():
    print "--- Controlador de Trafego Mininet (Educacional) ---"

    while True:
        print "\n--- MENU PRINCIPAL ---"
        print "1. Descobrir/Atualizar hosts na rede"
        print "2. Lançar teste de geracao de trafego"
        print "3. Sair"
        choice = raw_input("Escolha (1-3): ")

        if choice == '1':
            discover_hosts()

        elif choice == '2':
            if not controlled_hosts:
                print "Voce precisa descobrir os hosts primeiro (Opcao 1)."
                continue

            target_ip = raw_input("Digite o IP do alvo (ex: 10.0.0.4): ")
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_ip):
                print "IP alvo invalido."
                continue

            print "\nSelecione o tipo de trafego:"
            print "  1: Ping (ICMP Flood simulado)"
            print "  2: iperf (TCP Traffic)"
            traffic_type = raw_input("Escolha (1-2): ")

            command = ""
            if traffic_type == '1':
                command = "ping -c 100 -i 0.1 %s" % target_ip
                print "Comando: %s" % command
            elif traffic_type == '2':
                print "AVISO: O alvo %s deve estar rodando 'iperf -s'" % target_ip
                print "Voce pode rodar isso na CLI do Mininet: h4 iperf -s &"
                command = "iperf -c %s -t 10" % target_ip
                print "Comando: %s" % command
            else:
                print "Tipo invalido."
                continue

            attackers = select_attackers()
            if not attackers:
                print "Nenhum host selecionado para o teste."
                continue

            print "\nEnviando comandos para %d hosts: %s" % (len(attackers), ', '.join(attackers))
            for host_name in attackers:
                try:
                    response = server.run_command_on_host(host_name, command)
                    print "  %s" % response
                except Exception as e:
                    print "  Erro ao enviar comando para %s: %s" % (host_name, e)

        elif choice == '3':
            print "Saindo do controlador."
            break

        else:
            print "Escolha invalida. Tente novamente."

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print "\nControlador interrompido."


