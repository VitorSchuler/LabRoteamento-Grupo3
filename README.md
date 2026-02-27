# Relatório Técnico: Implementação de Roteamento Vetor de Distâncias
**Equipe:** Grupo 3
Este projeto foi desenvolvido de forma colaborativa pelos seguintes alunos da disciplina:

* **Vitor Schuler Velloso Borges** 
* **Axel Vaz** 
* **Gabriel Cabral**
* **Francisco Julião** ```

**Topologia Principal:** Dual Ring (12 Roteadores)

## Questão 1: Análise da Convergência Inicial (Topologia em Triângulo)

**Contexto do Experimento:**
Para analisar o comportamento básico do algoritmo de Bellman-Ford, estabelecemos uma topologia de testes contendo três nós (Roteadores A, B e C) interconectados em formato de triângulo, utilizando a interface de *loopback* (`127.0.0.1`) nas portas 5000, 5001 e 5002.

**O Processo de Convergência (Algoritmo de Bellman-Ford):**
A convergência da rede ocorreu seguindo os princípios fundamentais do roteamento por vetor de distâncias. O processo se deu nas seguintes etapas:

1. **Inicialização:** Ao serem instanciados, cada roteador conhecia apenas os seus vizinhos diretamente conectados (custo local) e a sua própria rede local (custo 0), configurados através dos arquivos `.csv`.
2. **Troca de Mensagens (Vetor de Distâncias):** Periodicamente, cada nó empacotou sua tabela de roteamento em formato JSON e a enviou para seus vizinhos diretos através de requisições HTTP POST para a rota `/receive_update`.
3. **Cálculo de Rotas:** Ao receber o vetor de distâncias de um vizinho (v), o roteador (x) avaliou se havia um caminho mais "barato" para um destino (y) aplicando a equação de Bellman-Ford: 
   Dx(y) = min_v {c(x,v) + Dv(y)}
   Onde c(x,v) é o custo do link direto para o vizinho e Dv(y) é o custo relatado pelo vizinho até o destino.
4. **Estado de Convergência:** Após algumas rodadas de troca de mensagens (aproximadamente 20 segundos de execução), as tabelas pararam de sofrer alterações. Todos os nós alcançaram uma visão consistente e ótima da topologia da rede.

**Evidência da Captura de Tráfego:**
Abaixo, apresentamos a captura de rede (`captura_triangulo.pcap`) evidenciando a troca de tabelas de roteamento (mensagens HTTP) no momento da convergência:


A captura acima ilustra o tráfego na interface *loopback*, onde é possível observar o fluxo de requisições HTTP `POST` trafegando entre as portas 5000, 5001 e 5002, confirmando a troca bem-sucedida (status `200 OK`) das tabelas JSON que culminou na convergência da rede.

***

## Questão 2: Tratamento de Falhas e Prevenção de Loops (A Queda do Roteador C)

**O Cenário de Falha:**
Após a rede triangular atingir o estado de convergência, simulamos o rompimento abrupto de um link ao desligar o Roteador C (porta 5002). O objetivo deste teste foi observar a reação do algoritmo de Bellman-Ford diante de uma mudança na topologia e a readequação das rotas nos Roteadores A e B remanescentes.

**O Problema da Contagem ao Infinito (Count-to-Infinity):**
No roteamento clássico por vetor de distâncias, a queda de um nó pode gerar um problema grave de loop de roteamento. Se o Roteador C cai, o Roteador A percebe a falha do link direto. No entanto, se o Roteador B ainda possuir a rota antiga para C na sua tabela e a anunciar para A, o Roteador A pode achar que B tem um caminho alternativo válido para C. A e B começam a atualizar suas tabelas apontando um para o outro, somando os custos infinitamente até que a métrica atinja o limite máximo estabelecido pelo protocolo.

**A Solução Implementada (Split Horizon):**
Para mitigar esse problema e garantir uma rápida re-convergência, implementamos a técnica de **Split Horizon** (Horizonte Dividido). A regra fundamental inserida na lógica do nosso roteador dita que: *se um roteador X utiliza o vizinho Y como próximo salto (next-hop) para alcançar um destino Z, o roteador X não deve anunciar a rota de Z de volta para Y.*

No nosso experimento, quando o Roteador C foi desativado:
* A comunicação com a porta 5002 cessou completamente, uma vez que o nó ficou inalcançável.
* Graças ao Split Horizon, o Roteador A não retransmitiu informações defasadas sobre C para o Roteador B (e vice-versa), interrompendo a falsa sensação de que ainda existia um caminho válido.
* A ausência de atualizações contendo a rota para C forçou os roteadores A e B a invalidarem esse destino rapidamente em suas tabelas, refletindo a nova realidade da rede sem entrar em loop de roteamento.

**Evidência da Falha e Re-convergência:**
A captura de rede abaixo (`captura_falha.pcap`) demonstra o comportamento da topologia após a queda do Roteador C. Através da análise do tráfego, é possível constatar a comunicação restrita aos roteadores remanescentes (tráfego TCP e HTTP originado e destinado às portas 5000 e 5001). A ausência absoluta de pacotes envolvendo a porta 5002 comprova o isolamento da falha, enquanto a troca contínua e estável de mensagens entre A e B atesta a eficácia do Split Horizon em estabilizar a rede de forma limpa.

***

## 1.3 Projeto da Topologia (Dual Ring - 12 Roteadores)

Para o cenário principal exigido, desenvolvemos a topologia em "Anel Duplo" (pertencente ao Grupo 3), composta por 12 nós. A arquitetura consiste em dois anéis de controle contendo 6 roteadores cada. Os anéis são interligados por links redundantes de maior custo (Custo 3) para garantir a tolerância a falhas e a comunicação fluida entre as duas redes.

**Diagrama da Arquitetura:**


Análise de Convergência (Tabela de Roteamento Global):
Para validar a precisão do algoritmo de Bellman-Ford implementado, realizamos o teste de mesa mapeando os caminhos ótimos a partir da perspectiva do Roteador 1 (R1) para todas as outras 11 redes da topologia, após a rede alcançar o estado de convergência total.

O Roteador 1 possui conexões diretas com R2 (custo 1), R6 (custo 2) e R7 (custo 3). Devido à execução em ambiente local, as portas foram mapeadas sequencialmente de 5001 a 5012. A tabela abaixo demonstra a métrica final calculada e o próximo salto (Next-Hop) escolhido por R1 para alcançar cada destino com o menor custo possível:

Rede de Destino	Next-Hop (Próximo Salto)	Custo Total Acumulado	Caminho Lógico do Algoritmo
**R2** (10.0.2.0/24)	R2 (192.168.0.2:5002)	1	R1 → R2
**R3** (10.0.3.0/24)	R2 (192.168.0.2:5002)	3	R1 → R2 → R3
**R4** (10.0.4.0/24)	R2 (192.168.0.2:5002)	4	R1 → R2 → R3 → R4
**R5** (10.0.5.0/24)	R6 (192.168.0.6:5006)	3	R1 → R6 → R5
**R6** (10.0.6.0/24)	R6 (192.168.0.6:5006)	2	R1 → R6
**R7** (10.0.7.0/24)	R7 (192.168.0.7:5007)	3	R1 → R7 (Link redundante)
**R8** (10.0.8.0/24)	R7 (192.168.0.7:5007)	4	R1 → R7 → R8
**R9** (10.0.9.0/24)	R7 (192.168.0.7:5007)	6	R1 → R7 → R8 → R9
**R10** (10.0.10.0/24)	R7 (192.168.0.7:5007)	7	R1 → R7 → R8 → R9 → R10
**R11** (10.0.11.0/24)	R7 (192.168.0.7:5007)	6	R1 → R7 → R12 → R11
**R12** (10.0.12.0/24)	R7 (192.168.0.7:5007)	5	R1 → R7 → R12

Nota: A utilização de portas distintas (5001-5012) permitiu a emulação fidedigna de processos independentes em uma mesma interface física. O tráfego de R1 para a rede de R10 ilustra a eficiência matemática do protocolo: o algoritmo descobre e utiliza a ponte de redundância (R7), provando que a topologia Dual Ring funciona como um ecossistema único de roteamento através da minimização de custos.

# 🌐 Simulador de Roteamento: Vetor de Distâncias (Bellman-Ford)

![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-success?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST_API-lightgrey?style=flat-square&logo=flask&logoColor=white)
![Redes](https://img.shields.io/badge/Redes-Roteamento-orange?style=flat-square)

Este repositório contém a implementação completa de um roteador virtual construído em Python, utilizando o protocolo de roteamento por **Vetor de Distâncias** baseado no algoritmo de **Bellman-Ford**. 

O projeto foi desenvolvido como requisito de avaliação laboratorial de Redes de Computadores, englobando a troca dinâmica de rotas, cálculo de caminhos de menor custo e mecanismos avançados de estabilidade de rede.

---

## ✨ Funcionalidades Implementadas

* **Descoberta Dinâmica de Rotas:** Cálculo automático do caminho mais curto para qualquer rede alcançável utilizando a equação de Bellman-Ford.
* **Comunicação RESTful:** Troca contínua de tabelas de roteamento entre nós vizinhos através de requisições `HTTP POST` com payloads estruturados em `JSON`.
* **Prevenção de Loops (Split Horizon):** Implementação rigorosa da regra de "Horizonte Dividido" para evitar o problema de *Count-to-Infinity* em cenários de queda abrupta de links e roteadores inoperantes.
* **Sumarização de Rotas:** Agrupamento inteligente de sub-redes contíguas na tabela de roteamento através de operações bit-a-bit (XOR e AND), otimizando o tamanho dos pacotes de atualização.

---

## 🗺️ Topologia de Teste: Dual Ring (Anel Duplo)

A arquitetura principal avaliada neste projeto (referente ao **Grupo 3**) é a topologia de Anel Duplo. 

O cenário é composto por **12 roteadores** divididos em dois anéis de controle contendo 6 nós cada. Os anéis operam de forma independente, mas são interligados por links redundantes de maior custo (Custo 3). Essa redundância garante tolerância a falhas, permitindo que o tráfego flua de um anel para o outro de forma transparente caso uma rota principal seja rompida.

> 📂 *O diagrama visual (`architecture.png`), o manifesto geral (`topologia.json`) e todos os arquivos de configuração CSV dos 12 nós estão localizados no diretório `/grupo3` deste repositório.*

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos e Instalação
Certifique-se de ter o Python 3.x instalado. É altamente recomendado o uso de um ambiente virtual para isolar as dependências.

Abra o terminal na raiz do projeto e execute:
```bash
# Criação do ambiente virtual
python -m venv venv

# Ativação do ambiente
source venv/bin/activate  # No Linux/Mac
# venv\Scripts\activate   # No Windows

# Instalação das dependências necessárias
pip install flask requests
