# 🌐 Roteamento Vetor de Distâncias (Bellman-Ford)

Este repositório contém a implementação prática de um roteador virtual (em Python) utilizando o protocolo de roteamento por **Vetor de Distâncias** baseado no algoritmo de **Bellman-Ford**. 

O projeto foi desenvolvido como requisito de avaliação laboratorial, englobando a troca dinâmica de rotas, cálculo de caminhos de menor custo e mecanismos de prevenção de loops de rede.

## 👥 Equipe
* **Grupo 3**
* **Membro:** Vitor Schuler Velloso Borges

## 🚀 Funcionalidades Implementadas

* **Roteamento Dinâmico:** Descoberta automática de rotas e cálculo do caminho mais curto (Bellman-Ford).
* **Comunicação REST:** Troca de tabelas de roteamento entre nós vizinhos utilizando requisições HTTP POST com payloads em formato JSON.
* **Prevenção de Loops (Split Horizon):** Implementação da regra de "Horizonte Dividido" para evitar o problema de *Count-to-Infinity* em caso de queda de links.
* **Orquestração Automática:** Scripts auxiliares para inicializar múltiplos nós da topologia simultaneamente.

## 🗺️ Topologia (Cenário Principal)

A arquitetura principal exigida para o Grupo 3 foi a **Dual Ring** (Anel Duplo). 
O cenário é composto por **12 roteadores** divididos em dois anéis de controle de 6 nós cada, interligados por links redundantes de maior custo para garantir a tolerância a falhas e balanceamento da rede.

Os arquivos de configuração dessa topologia, bem como o diagrama da arquitetura e as capturas de tráfego (`.pcap`), encontram-se no diretório `/grupo3`.

## ⚙️ Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o Python 3.x instalado em sua máquina. É altamente recomendado o uso de um ambiente virtual (`venv`).

### 1. Instalação das dependências
Abra o terminal na raiz do projeto e instale os pacotes necessários:
```bash
python -m venv venv
source venv/bin/activate  # No Windows, use: venv\Scripts\activate
pip install flask requests




📁 Estrutura do Repositório
Plaintext
/
├── roteador.py            # Código-fonte principal do roteador (Flask)
├── rodar_rede.py          # Script de orquestração para subir os 12 nós
├── setup_entrega.py       # Script para gerar IPs de submissão (192.168.0.X)
├── Relatorio.pdf          # Relatório Técnico com análise de convergência e falhas
├── captura_triangulo.pcap # Captura Wireshark: Convergência inicial
├── captura_falha.pcap     # Captura Wireshark: Tratamento de falha (Split Horizon)
└── grupo3/                # Diretório da Topologia Dual Ring
    ├── architecture.png   # Diagrama da rede
    ├── topologia.json     # Metadados da topologia
    ├── captura.pcap       # Tráfego de convergência dos 12 nós
    └── R1.csv a R12.csv   # Arquivos de configuração de vizinhos e custos