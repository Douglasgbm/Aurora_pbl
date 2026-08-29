temp_interna = 22
temp_externa = 30
integridade = 1
pressao_tanques = 500
energia = 100
modulos_online = True
decolagem_autorizada = True




# Verificação 1
if temp_interna > 30 or temp_interna < 15:
    print("Erro: Temperatura Interna fora do range!")
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Temperatura Interna: OK")

if temp_externa > 45 or temp_externa < -10:
    print("Erro: Temperatura Externa fora do range!")   
    decolagem_autorizada = False  # Desliga a chave
else:  
    print("Temperatura Externa: OK")

# Verificação 2
if integridade < 1:
    print("Erro: Integridade comprometida!")
    decolagem_autorizada = False  # Desliga a chave 
else:
    print("Integridade: OK")

# Verificação 3
if pressao_tanques < 450 or pressao_tanques > 550:
    print("Erro: Pressão dos tanques fora do range!")
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Pressão dos Tanques: OK")

# Verificação 4
if energia < 80:
    print("Erro: Energia insuficiente!")
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Energia: OK")

# Verificação 5
if not modulos_online:
    print("Erro: Módulos offline!")
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Módulos: OK")

# Verificação Final
if decolagem_autorizada:
    print("Decolagem Autorizada!")
else:
    print("Decolagem Não Autorizada!")





