import json
import os

PASTA = 'grupo3'

roteadores = []
for i in range(1, 13):
    roteadores.append({
        "name": f"R{i}",
        "network": f"10.0.{i}.0/24",
        "address": f"192.168.0.{i}:5000",
        "config_file": f"R{i}.csv"
    })

with open(os.path.join(PASTA, 'topologia.json'), 'w') as f:
    json.dump(roteadores, f, indent=4)

conexoes = {
    1: {2: 1, 6: 2, 7: 3}, 2: {1: 1, 3: 2}, 3: {2: 2, 4: 1},
    4: {3: 1, 5: 2, 10: 3}, 5: {4: 2, 6: 1}, 6: {5: 1, 1: 2},
    7: {8: 1, 12: 2, 1: 3}, 8: {7: 1, 9: 2}, 9: {8: 2, 10: 1},
    10: {9: 1, 11: 2, 4: 3}, 11: {10: 2, 12: 1}, 12: {11: 1, 7: 2}
}

for r_id, vizinhos in conexoes.items():
    with open(os.path.join(PASTA, f'R{r_id}.csv'), 'w') as f:
        f.write("neighbor_address,cost\n")
        for vizinho_id, custo in vizinhos.items():
            f.write(f"192.168.0.{vizinho_id}:5000,{custo}\n")

print("Arquivos de entrega gerados com sucesso na pasta 'grupo3'")