import os

os.makedirs('triangulo', exist_ok=True)
ip = "127.0.0.1" # Usando o localhost para bater com o nome interno do roteador

# Roteador A
with open('triangulo/config_A.csv', 'w') as f:
    f.write(f"vizinho,custo\n{ip}:5001,1\n{ip}:5002,10\n")

# Roteador B
with open('triangulo/config_B.csv', 'w') as f:
    f.write(f"vizinho,custo\n{ip}:5000,1\n{ip}:5002,2\n")

# Roteador C
with open('triangulo/config_C.csv', 'w') as f:
    f.write(f"vizinho,custo\n{ip}:5000,10\n{ip}:5001,2\n")

print("Arquivos do triângulo ajustados para 127.0.0.1!")