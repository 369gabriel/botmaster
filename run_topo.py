#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import sys
import imp
from mininet.net import Mininet
from mininet.topo import LinearTopo
from mininet.cli import CLI
from SimpleXMLRPCServer import SimpleXMLRPCServer

net = None

class MininetRPCServer:
    def __init__(self, host='localhost', port=8000):
        self.net = net
        if not self.net:
            raise ValueError("Rede Mininet nao foi iniciada")

        self.server = SimpleXMLRPCServer((host, port), logRequests=False, allow_none=True)
        self.server.register_function(self.get_all_hosts, 'get_all_hosts')
        self.server.register_function(self.get_host_ip, 'get_host_ip')
        self.server.register_function(self.run_command_on_host, 'run_command_on_host')
        print "Servidor RPC ouvindo em http://%s:%s" % (host, port)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def get_all_hosts(self):
        """Retorna uma lista de nomes de todos os hosts (ex: ['h1', 'h2'])"""
        return [host.name for host in self.net.hosts]

    def get_host_ip(self, host_name):
        """Retorna o IP de um host especifico"""
        try:
            host = self.net.get(host_name)
            return host.IP()
        except:
            return None

    def run_command_on_host(self, host_name, command):
        """Executa um comando em um host e retorna a saida"""
        try:
            host = self.net.get(host_name)
            # Adiciona '&' para rodar em background e nao bloquear
            output = host.cmd(command + ' &')
            return "Comando '%s' enviado para %s." % (command, host_name)
        except Exception as e:
            return "Erro ao executar comando em %s: %s" % (host_name, str(e))

def start_network():
    global net

    topo = None

    if len(sys.argv) > 1:
        topo_file = sys.argv[1]
        print "Carregando topologia customizada de: %s" % topo_file
        try:
            module_name = topo_file.split('/')[-1].replace('.py', '')

            custom_topo_module = imp.load_source(module_name, topo_file)

            if hasattr(custom_topo_module, 'topos'):
                topo_key = custom_topo_module.topos.keys()[0]
                topo_builder = custom_topo_module.topos[topo_key]
                topo = topo_builder()
                print "Topologia '%s' carregada com sucesso." % topo_key
            else:
                print "Arquivo de topologia nao contem um dicionario 'topos'. Usando LinearTopo."

        except Exception as e:
            print "Erro ao carregar topologia customizada: %s" % e
            print "Usando topologia LinearTopo padrao."

    if topo is None:
        print "Usando topologia LinearTopo(k=4) padrao."
        topo = LinearTopo(k=4)

    net = Mininet(topo=topo)

    print "Iniciando a rede Mininet..."
    net.start()

    print "Hosts disponiveis:"
    for host in net.hosts:
        print "%s: %s" % (host.name, host.IP())

    rpc_server = MininetRPCServer()
    rpc_server.start()

    print "Iniciando CLI do Mininet. Deixe este terminal aberto."
    CLI(net)

    print "Parando a rede Mininet..."
    net.stop()

if __name__ == '__main__':
    start_network()



