#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Modulo para registrar ataques em formato CSV.
"""

import csv
import os
from datetime import datetime
try:
    import uuid
except ImportError:
    # Fallback para Python mais antigo
    import random
    class uuid:
        @staticmethod
        def uuid4():
            return str(random.randint(100000, 999999))

class AttackLogger:
    """Classe responsavel por registrar ataques em formato CSV."""
    
    def __init__(self, csv_file='attack_flows.csv'):
        """
        Inicializa o logger de ataques.
        
        Args:
            csv_file: Caminho para o arquivo CSV onde os ataques serao salvos.
        """
        self.csv_file = csv_file
        self.fieldnames = [
            'timestamp',
            'attack_id',
            'attack_type',
            'attackers',
            'target_ip',
            'target_port',
            'duration',
            'num_attackers'
        ]
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Cria o arquivo CSV com headers se nao existir."""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
    
    def log_attack(self, attack_type, attackers, target_ip, target_port=None, duration=None):
        """
        Registra um ataque no arquivo CSV.
        
        Args:
            attack_type: Tipo do ataque (ping, tcp_syn, udp, iperf)
            attackers: Lista de hosts atacantes
            target_ip: IP do alvo
            target_port: Porta do alvo (opcional)
            duration: Duracao do ataque em segundos (opcional)
            
        Returns:
            attack_id: ID unico do ataque registrado
        """
        attack_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Converte lista de atacantes para string
        attackers_str = ','.join(attackers) if isinstance(attackers, list) else str(attackers)
        
        attack_data = {
            'timestamp': timestamp,
            'attack_id': attack_id,
            'attack_type': attack_type,
            'attackers': attackers_str,
            'target_ip': target_ip,
            'target_port': target_port if target_port else '',
            'duration': duration if duration else '',
            'num_attackers': len(attackers) if isinstance(attackers, list) else 1
        }
        
        with open(self.csv_file, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(attack_data)
        
        return attack_id
    
    def generate_report(self):
        """
        Gera um relatorio dos ataques registrados.
        
        Returns:
            String com o relatorio formatado ou None se nao houver ataques.
        """
        if not os.path.exists(self.csv_file):
            return None
        
        attacks = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                attacks.append(row)
        
        if not attacks:
            return None
        
        # Gera estatisticas
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("RELATORIO DE ATAQUES")
        report_lines.append("=" * 60)
        report_lines.append("")
        report_lines.append("Total de ataques registrados: %d" % len(attacks))
        report_lines.append("")
        
        # Conta ataques por tipo
        attack_types = {}
        for attack in attacks:
            attack_type = attack['attack_type']
            attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        
        report_lines.append("Ataques por tipo:")
        for attack_type, count in sorted(attack_types.items()):
            report_lines.append("  - %s: %d" % (attack_type, count))
        report_lines.append("")
        
        # Lista ultimos 10 ataques
        report_lines.append("Ultimos %d ataques:" % min(10, len(attacks)))
        for attack in attacks[-10:]:
            report_lines.append("  - [%s] %s -> %s (tipo: %s, atacantes: %s)" % (
                attack['timestamp'][:19],  # Remove microssegundos
                attack['attackers'],
                attack['target_ip'],
                attack['attack_type'],
                attack['num_attackers']
            ))
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return '\n'.join(report_lines)


def test_logger():
    """Funcao de teste para o AttackLogger."""
    print("Testando AttackLogger...")
    
    # Cria logger de teste
    test_file = 'test_attacks.csv'
    if os.path.exists(test_file):
        os.remove(test_file)
    
    logger = AttackLogger(csv_file=test_file)
    
    # Testa registro de varios tipos de ataque
    print("Registrando ataque de ping...")
    attack_id1 = logger.log_attack('ping', ['h1', 'h2'], '10.0.0.5', duration=10)
    print("  Attack ID: %s" % attack_id1)
    
    print("Registrando ataque TCP SYN...")
    attack_id2 = logger.log_attack('tcp_syn', ['h3'], '10.0.0.6', target_port=80, duration=15)
    print("  Attack ID: %s" % attack_id2)
    
    print("Registrando ataque UDP...")
    attack_id3 = logger.log_attack('udp', ['h1', 'h2', 'h3'], '10.0.0.7', target_port=53, duration=20)
    print("  Attack ID: %s" % attack_id3)
    
    print("\nGerando relatorio...")
    report = logger.generate_report()
    if report:
        print(report)
    else:
        print("Nenhum ataque registrado.")
    
    print("\nArquivo CSV criado: %s" % test_file)
    print("Teste concluido!")


if __name__ == '__main__':
    test_logger()
