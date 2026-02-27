import csv
import json
import threading
import time
from argparse import ArgumentParser

import requests
from flask import Flask, jsonify, request

class Router:
    """
    Representa um roteador que executa o algoritmo de Vetor de Distância.
    """

    def __init__(self, my_address, neighbors, my_network, update_interval=1):
        """
        Inicializa o roteador.

        :param my_address: O endereço (ip:porta) deste roteador.
        :param neighbors: Um dicionário contendo os vizinhos diretos e o custo do link.
                          Ex: {'127.0.0.1:5001': 5, '127.0.0.1:5002': 10}
        :param my_network: A rede que este roteador administra diretamente.
                           Ex: '10.0.1.0/24'
        :param update_interval: O intervalo em segundos para enviar atualizações, o tempo que o roteador espera 
                                antes de enviar atualizações para os vizinhos.        """
        self.my_address = my_address
        self.neighbors = neighbors
        self.my_network = my_network
        self.update_interval = update_interval

        # =====================================================================
        # FASE 1: INICIALIZAÇÃO DA TABELA DE ROTEAMENTO
        # =====================================================================
        
      
        self.routing_table = {}

        self.routing_table[self.my_network] = {
            'cost': 0,
            'next_hop': self.my_network 
        }

       
        for neighbor_ip_port, cost in self.neighbors.items():
             self.routing_table[neighbor_ip_port] = {
                 'cost': cost,
                 'next_hop': neighbor_ip_port
             }
        
        # =====================================================================

        print("Tabela de roteamento inicial:")
        print(json.dumps(self.routing_table, indent=4))

        self._start_periodic_updates()

    def _start_periodic_updates(self):
        """Inicia uma thread para enviar atualizações periodicamente."""
        thread = threading.Thread(target=self._periodic_update_loop)
        thread.daemon = True
        thread.start()

    def _periodic_update_loop(self):
        """Loop que envia atualizações de roteamento em intervalos regulares."""
        while True:
            time.sleep(self.update_interval)
            print(f"[{time.ctime()}] Enviando atualizações periódicas para os vizinhos...")
            try:
                self.send_updates_to_neighbors()
            except Exception as e:
                print(f"Erro durante a atualização periódida: {e}")

    # =====================================================================
    # FASE 3: FUNÇÕES AUXILIARES DE BITS PARA SUMARIZAÇÃO
    # =====================================================================
    def ip_to_int(self, ip_str):
        """Converte um IP em string para um inteiro de 32 bits."""
        parts = ip_str.split('.')
        return (int(parts[0]) << 24) | (int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])

    def int_to_ip(self, ip_int):
        """Converte um inteiro de 32 bits de volta para string IP."""
        return f"{(ip_int >> 24) & 255}.{(ip_int >> 16) & 255}.{(ip_int >> 8) & 255}.{ip_int & 255}"

    def summarize_table(self, table):
        """Implementa a sumarização de rotas com operações de bits puras."""
        groups = {}
        summarized = {}
        
        for net, info in table.items():
            if '/' not in net:
                summarized[net] = info.copy()
                continue
                
            nh = info['next_hop']
            if nh not in groups:
                groups[nh] = []
            groups[nh].append((net, info))
            
        for nh, routes in groups.items():
            changed = True
            while changed:
                changed = False
                i = 0
                while i < len(routes):
                    j = i + 1
                    merged = False
                    while j < len(routes):
                        net1, info1 = routes[i]
                        net2, info2 = routes[j]
                        
                        ip1_str, pref1_str = net1.split('/')
                        ip2_str, pref2_str = net2.split('/')
                        pref1, pref2 = int(pref1_str), int(pref2_str)
                        
                        if pref1 == pref2:
                            ip1 = self.ip_to_int(ip1_str)
                            ip2 = self.ip_to_int(ip2_str)
                            
                            diff = ip1 ^ ip2
                            target_bit = 1 << (32 - pref1) 
                            
                            if diff == target_bit:
                                base_ip = min(ip1, ip2)
                                if (base_ip & target_bit) == 0:
                                    new_pref = pref1 - 1
                                    new_net = f"{self.int_to_ip(base_ip)}/{new_pref}"
                                    new_cost = max(info1['cost'], info2['cost']) 
                                    
                                    routes.pop(j)
                                    routes.pop(i)
                                    routes.append((new_net, {'cost': new_cost, 'next_hop': nh}))
                                    
                                    changed = True
                                    merged = True
                                    break
                    if merged:
                        break
                    i += 1
        
            for net, info in routes:
                summarized[net] = info
                
        return summarized

    def send_updates_to_neighbors(self):
        """Envia a tabela com Split Horizon e Sumarização."""
        for neighbor_address in self.neighbors:
            
            # =====================================================================
            # FASE 4: SPLIT HORIZON (Vacina contra Loop / Desafio Extra)
            # =====================================================================
            table_for_neighbor = {}
            for net, info in self.routing_table.items():
              
                if info['next_hop'] != neighbor_address:
                    table_for_neighbor[net] = info.copy()
            
            summarized_table = self.summarize_table(table_for_neighbor)
            
            payload = {
                "sender_address": self.my_address,
                "routing_table": summarized_table
            }

            url = f'http://{neighbor_address}/receive_update'
            try:
                requests.post(url, json=payload, timeout=2)
            except requests.exceptions.RequestException:
                # ALERTA DE QUEDA: O vizinho não respondeu!
                # Vamos definir o custo para o infinito (16) para as rotas que dependem dele.
                table_changed = False
                for net, info in list(self.routing_table.items()):
                    if info['next_hop'] == neighbor_address and info['cost'] < 16:
                        self.routing_table[net]['cost'] = 16
                        table_changed = True
                
                if table_changed:
                    print(f"\n[!] ALERTA: Link com {neighbor_address} caiu! Rotas ajustadas para o infinito (16).")
                    print(json.dumps(self.routing_table, indent=4))
# --- API Endpoints ---

app = Flask(__name__)
router_instance = None

@app.route('/routes', methods=['GET'])
def get_routes():
    """Endpoint para visualizar a tabela de roteamento atual."""
    if router_instance:
        return jsonify({
            "message": "Tabela de roteamento recuperada com sucesso!",
            "vizinhos" : router_instance.neighbors,
            "my_network": router_instance.my_network,
            "my_address": router_instance.my_address,
            "update_interval": router_instance.update_interval,
            "routing_table": router_instance.routing_table 
        }), 200 
    return jsonify({"error": "Roteador não inicializado"}), 500

@app.route('/receive_update', methods=['POST'])
def receive_update():
    """Endpoint que recebe atualizações de roteamento de um vizinho."""
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400

    update_data = request.json
    sender_address = update_data.get("sender_address")
    sender_table = update_data.get("routing_table")

    if not sender_address or not isinstance(sender_table, dict):
        return jsonify({"error": "Missing sender_address or routing_table"}), 400

    # =====================================================================
    # FASE 2: LÓGICA DE BELLMAN-FORD
    # =====================================================================
    
    sender_ip = sender_address.split(':')[0]
    matched_address = next((addr for addr in router_instance.neighbors if addr.startswith(sender_ip)), None)

    #if not matched_address:
    #    return jsonify({"error": f"Unknown neighbor IP: {sender_ip}"}), 403
        
    direct_cost = router_instance.neighbors[matched_address]
    table_changed = False 

    for network, info in sender_table.items():
        if network == router_instance.my_network:
            continue
            
        new_cost = direct_cost + info['cost']
       
        if network not in router_instance.routing_table:
            router_instance.routing_table[network] = {
                'cost': new_cost,
                'next_hop': sender_address
            }
            table_changed = True
            
        else:
            current_cost = router_instance.routing_table[network]['cost']
            current_next_hop = router_instance.routing_table[network]['next_hop']
            
            if new_cost < current_cost:
                router_instance.routing_table[network] = {
                    'cost': new_cost,
                    'next_hop': sender_address
                }
                table_changed = True
        
            elif current_next_hop == sender_address and new_cost != current_cost:
                router_instance.routing_table[network] = {
                    'cost': new_cost,
                    'next_hop': sender_address
                }
                table_changed = True

    if table_changed:
        print(f"\n[!] Tabela atualizada com informações de {sender_address}:")
        print(json.dumps(router_instance.routing_table, indent=4))

    return jsonify({"status": "success", "message": "Update processed"}), 200

if __name__ == '__main__':
    parser = ArgumentParser(description="Simulador de Roteador com Vetor de Distância")
    parser.add_argument('-p', '--port', type=int, default=5000, help="Porta para executar o roteador.")
    parser.add_argument('--ip', type=str, default="127.0.0.1", help="Endereço IP deste roteador (ex: 192.168.0.1).")
    parser.add_argument('-f', '--file', type=str, required=True, help="Arquivo CSV de configuração de vizinhos.")
    parser.add_argument('--network', type=str, required=True, help="Rede administrada por este roteador (ex: 10.0.1.0/24).")
    parser.add_argument('--interval', type=int, default=10, help="Intervalo de atualização periódica em segundos.")
    args = parser.parse_args()

    neighbors_config = {}
    try:
        with open(args.file, mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                neighbors_config[row['neighbor_address']] = int(row['cost'])
    except FileNotFoundError:
        print(f"Erro: Arquivo de configuração '{args.file}' não encontrado.")
        exit(1)
    except (KeyError, ValueError) as e:
        print(f"Erro no formato do arquivo CSV: {e}. Verifique as colunas 'neighbor_address' e 'cost'.")
        exit(1)

    my_full_address = f"{args.ip}:{args.port}"
    
    print("--- Iniciando Roteador ---")
    print(f"Endereço: {my_full_address}")
    print(f"Rede Local: {args.network}")
    print(f"Vizinhos Diretos: {neighbors_config}")
    print(f"Intervalo de Atualização: {args.interval}s")
    print("--------------------------")

    router_instance = Router(
        my_address=my_full_address,
        neighbors=neighbors_config,
        my_network=args.network,
        update_interval=args.interval
    )

    # Inicia o servidor Flask
    app.run(host='0.0.0.0', port=args.port, debug=False)