# REGRAS FIXAS DA NAVE (constantes, por isso MAIÚSCULO)
CONSUMO_DECOLAGEM = 300.0
PERDAS = 0.08
energia = input("Digite a energia inicial (%): ")
energia = float(energia)



# A CONTA (copiada do main.py, linhas 23 a 26)
def calcular_energia(energia, capacidade_total=1000.0):
    energia = 999
    energia_disponivel = capacidade_total * (energia / 100)
    consumo_real = CONSUMO_DECOLAGEM * (1 + PERDAS)
    energia_restante = energia_disponivel - consumo_real
    autonomia_restante = (energia_restante / capacidade_total) * 100
    return energia_disponivel, consumo_real, energia_restante, autonomia_restante

# MOSTRA OS RESULTADOS USANDO A FUNÇÃO
energia_disponivel, consumo_real, energia_restante, autonomia_restante = calcular_energia(energia)
print(energia_disponivel)
print(consumo_real)
print(energia_restante)
print(autonomia_restante)

