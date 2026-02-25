import json
import subprocess
import time
import os
import sys

TOPOLOGIA_FILE = 'grupo3/topologia.json'
PASTA_CENARIO = 'grupo3/'

def iniciar_roteadores():
    try:
        with open(TOPOLOGIA_FILE, 'r') as f:
            roteadores = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo {TOPOLOGIA_FILE} não encontrado.")
        sys.exit(1)

    processos = []
    print("Iniciando a rede Dual Ring do Grupo 3...\n")

    for r in roteadores:
        porta = r['address'].split(':')[1]
        
        config_file = os.path.join(PASTA_CENARIO, r['config_file'])
        network = r['network']
        nome = r['name']

        comando = [
            sys.executable, 'roteador.py', 
            '-p', porta, 
            '-f', config_file, 
            '--network', network
        ]

        print(f"Iniciando {nome} na porta {porta} (Rede: {network})...")
        
        p = subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processos.append((nome, p))
        time.sleep(0.5) 

    print("Todos os 12 roteadores foram iniciados e estão convergindo.")
    print("Pressione CTRL+C para desligar toda a rede.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDesligando a rede. Matando os processos...")
        for nome, p in processos:
            p.terminate()
        print("Rede desligada com sucesso.")

if __name__ == '__main__':
    iniciar_roteadores()