import json
import subprocess
import time
import os
import sys

# Ajuste os caminhos abaixo conforme a sua pasta
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
    print("Iniciando a rede de 12 roteadores (Portas 5001-5012)...\n")

    # O loop corrigido com a variável 'roteadores' definida
    for i, r in enumerate(roteadores, start=1):
        # Forçamos a porta sequencial para evitar o erro de porta ocupada
        porta = str(5000 + i)
        
        config_file = os.path.join(PASTA_CENARIO, r['config_file'])
        network = r['network']
        nome = r['name']
        
        # Comando para rodar o roteador
        comando = [
            sys.executable, 'roteador.py', 
            '-p', porta, 
            '-f', config_file, 
            '--network', network
        ]

        print(f"Iniciando {nome} na porta {porta} (Rede: {network})...")
        
        # Abrimos um arquivo de log para cada roteador (r1.log, r2.log...)
        log_file = open(f"{nome.lower()}.log", "w")
        p = subprocess.Popen(comando, stdout=log_file, stderr=log_file)
        
        # Guardamos o processo e o arquivo de log para fechar depois
        processos.append((nome, p, log_file))
        time.sleep(0.5) 

    print("\nTodos os 12 roteadores estão rodando em background.")
    print("Acompanhe o R1 com: tail -f r1.log")
    print("Pressione CTRL+C para desligar toda a rede.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nFinalizando processos...")
        for nome, p, log in processos:
            p.terminate()
            log.close()
        print("Rede desligada.")

if __name__ == '__main__':
    iniciar_roteadores()