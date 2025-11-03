#!/usr/bin/env python

import sys
import threading
import SimpleXMLRPCServer
import imp

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel
from mininet.topo import LinearTopo

net = None

def get_all_hosts_info():
    info = {}
    if net:
        for host in net.hosts:
            info[host.name] = host.IP()
    return info

def run_command_on_host(host_name, command):
    if net:
        host = net.get(host_name)
        if host:
            try:
                output = host.cmd(command)
                return "Comando executado em %s. Saida:\n%s" % (host_name, output)
            except Exception as e:
                return "Erro ao executar comando em %s: %s" % (host_name, str(e))
        else:
            return "Erro: Host %s nao encontrado." % host_name
    return "Erro: Rede Mininet nao iniciada."

def start_rpc_server():
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 8000), logRequests=False, allow_none=True)
    server.register_function(get_all_hosts_info)
    server.register_function(run_command_on_host)
    server.serve_forever()

def run_mininet(topo):
    global net
    try:
        c0 = RemoteController('c0', ip='172.17.0.1', port=6653)
        net = Mininet(topo=topo, controller=c0)
        net.start()

        rpc_thread = threading.Thread(target=start_rpc_server)
        rpc_thread.daemon = True
        rpc_thread.start()

        CLI(net)

    except Exception as e:
        pass
    finally:
        if net:
            net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    topo = None

    if len(sys.argv) > 1:
        topo_file = sys.argv[1]
        try:
            module_name = topo_file.replace('.py', '')
            topo_module = imp.load_source(module_name, topo_file)

            if hasattr(topo_module, 'topos') and topo_module.topos:
                topo_name = topo_module.topos.keys()[0]
                topo = topo_module.topos[topo_name]()
            else:
                pass
        except ImportError as e:
            print "Erro ao importar %s: %s" % (topo_file, e)
        except Exception as e:
             print "Erro ao carregar topologia: %s" % e

    if topo is None:
        topo = LinearTopo(k=4)

    run_mininet(topo)



