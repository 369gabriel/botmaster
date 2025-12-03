#!/usr/bin/python2
# -*- coding: utf-8 -*-

import csv
import os
import time
from datetime import datetime, timedelta

try:
    import uuid
except ImportError:
    import random
    class uuid:
        @staticmethod
        def uuid4():
            return str(random.randint(100000, 999999))

class AttackLogger(object):

    def __init__(self, csv_file='../controller/attack_flows.csv'):
        self.csv_file = csv_file
        self.fieldnames = [
            'timestamp', 'attack_id', 'attack_type', 'attackers',
            'target_ip', 'target_port', 'duration', 'num_attackers'
        ]
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        directory = os.path.dirname(self.csv_file)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                pass

        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def log_attack(self, attack_type, attackers, target_ip, target_port=None, duration=None):
        attack_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        if isinstance(attackers, list):
            attackers_str = ','.join(attackers)
            num_attackers = len(attackers)
        else:
            attackers_str = str(attackers)
            num_attackers = 1

        attack_data = {
            'timestamp': timestamp,
            'attack_id': attack_id,
            'attack_type': attack_type,
            'attackers': attackers_str,
            'target_ip': target_ip,
            'target_port': target_port if target_port else '',
            'duration': str(duration) if duration else '0',
            'num_attackers': num_attackers
        }

        with open(self.csv_file, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(attack_data)

        return attack_id

    def generate_report(self):
        if not os.path.exists(self.csv_file):
            return "Nenhum arquivo de log encontrado."

        attacks = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                attacks.append(row)

        if not attacks:
            return "Nenhum ataque registrado."

        lines = []
        lines.append("=" * 60)
        lines.append("RELATORIO DE ATAQUES")
        lines.append("=" * 60)
        lines.append("Total: %d" % len(attacks))
        lines.append("")
        
        lines.append("Ultimos 5 ataques:")
        for atk in attacks[-5:]:
            lines.append(" - [%s] %s -> %s (%s)" % (atk['timestamp'], atk['attackers'], atk['target_ip'], atk['attack_type']))
            
        return "\n".join(lines)

    def compare_with_controller(self, controller_log_path):
        if not os.path.exists(self.csv_file):
            return "Erro: Log de ataques (Ground Truth) nao encontrado."
        
        if not os.path.exists(controller_log_path):
            return "Erro: Log do controlador nao encontrado em: %s" % controller_log_path

        print "\n" + "="*50
        print "ANALISE: GROUND TRUTH vs PREDICAO (CONTROLADOR)"
        print "="*50

        ground_truth_attacks = []
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    time_str = row['timestamp'].split('.')[0]
                    start_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                    
                    dur = float(row['duration']) if row['duration'] else 0
                    end_time = start_time + timedelta(seconds=dur)
                    
                    src_ips = [ip.strip() for ip in row['attackers'].split(',')]
                    
                    ground_truth_attacks.append({
                        'start': start_time,
                        'end': end_time,
                        'src_ips': src_ips,
                        'dst_ip': row['target_ip'],
                        'type': row['attack_type'],
                        'detected': False
                    })
                except Exception as e:
                    continue

        predictions = []
        with open(controller_log_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    time_str = row['timestamp'].split('.')[0]
                    detect_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                    
                    predictions.append({
                        'time': detect_time,
                        'src': row['src_ip'],
                        'dst': row['dst_ip'],
                        'matched': False
                    })
                except Exception as e:
                    continue

        tp = 0; fp = 0; fn = 0

        for attack in ground_truth_attacks:
            attack_detected = False
            margin_start = attack['start'] - timedelta(seconds=2)
            margin_end = attack['end'] + timedelta(seconds=5)

            for pred in predictions:
                if margin_start <= pred['time'] <= margin_end:
                    if pred['src'] in attack['src_ips'] and pred['dst'] == attack['dst_ip']:
                        attack_detected = True
                        pred['matched'] = True
            
            if attack_detected:
                tp += 1
            else:
                fn += 1

        for pred in predictions:
            if not pred['matched']:
                fp += 1

        precision = float(tp) / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = float(tp) / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        res = []
        res.append("Verdadeiros Positivos (TP): %d" % tp)
        res.append("Falsos Negativos      (FN): %d" % fn)
        res.append("Falsos Positivos      (FP): %d" % fp)
        res.append("-" * 30)
        res.append("PRECISAO: %.2f%%" % (precision * 100))
        res.append("RECALL:   %.2f%%" % (recall * 100))
        res.append("F1-SCORE: %.2f%%" % (f1 * 100))
        
        return "\n".join(res)
