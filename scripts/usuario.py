temp_interna = float(input("Digite a temperatura interna: "))
temp_externa = float(input("Digite a temperatura externa: "))
integridade = int(input("Digite a integridade (1 para OK, 0 para Falha): "))
pressao_tanques = float(input("Digite a pressão dos tanques: "))
energia = float(input("Digite a porcentagem de energia: "))
modulos_online = input("Módulos online? (S/N): ").upper() == "S" # O UPPER() CONVERTE A ENTRADA PARA MAIÚSCULO, E O == "S" 
# VERIFICA SE O USUÁRIO DIGITOU "S" PARA SIM, RETORNANDO TRUE OU FALSE.
capacidade_total = 1000.0  # kWh - capacidade total da bateria (valor fixo do projeto)
decolagem_autorizada = True

# CONSTANTES DO PROJETO (em MAIÚSCULO por convenção: são valores fixos da nave).
CONSUMO_DECOLAGEM = 300.0   # kWh - consumo estimado na fase de decolagem
PERDAS = 0.08               # 8% de perdas (conversão do inversor + aquecimento)
RESERVA_MINIMA = 0.10       # 10% da capacidade deve sobrar como reserva de pouso

# ANÁLISE ENERGÉTICA (item 1.4)
# A VARIÁVEL "energia" ESTÁ EM PORCENTAGEM (%), ENTÃO PRECISA VIRAR kWh.
energia_disponivel = capacidade_total * (energia / 100)   # ex: 1000 * 0.80 = 800 kWh
consumo_real = CONSUMO_DECOLAGEM * (1 + PERDAS)           # ex: 300 * 1.08 = 324 kWh
energia_restante = energia_disponivel - consumo_real      # ex: 800 - 324 = 476 kWh
autonomia_restante = (energia_restante / capacidade_total) * 100  # volta para %

# FLOAT INPUTS SERVE PARA O USUARIO DAR AS MEDIDAS DE TEMPERATURA, PRESSÃO E ENERGIA, ENQUANTO O 
# INTEIRO SERVE PARA A INTEGRIDADE (1 OU 0) E O BOOLEANO PARA OS MODULOS ONLINE (S/N).
# NO CASO DE INTEGRIDADE, 1 SIGNIFICA QUE ESTÁ TUDO OK, ENQUANTO 0 SIGNIFICA QUE HOUVE UMA FALHA.
# O USUARIO DEVE ALIMENTAR OS DADOS CORRETAMENTE PARA QUE O SISTEMA FUNCIONE ADEQUADAMENTE.
# CASO OS DADOS SEJAM DIVERGENTES DOS PREDEFINIDOS, O SISTEMA IRÁ BLOQUEAR A DECOLAGEM, INFORMANDO O ERRO AO USUARIO.
# IF E ELSE SAO CONDICIONAIS QUE VERIFICAM SE OS DADOS ESTÃO DENTRO DO RANGE ACEITÁVEL, E CASO NÃO ESTEJAM, DESLIGAM A 
# CHAVE DE DECOLAGEM, IMPEDINDO O LANÇAMENTO.
# OS VALORES DENTRO DE IF E ELSE SAO OS LIMITES DE SEGURANÇA PARA CADA VARIÁVEL, E O USUARIO DEVE SEGUIR 
# ESSES LIMITES PARA GARANTIR A SEGURANÇA DO LANÇAMENTO.

# Verificação 1 - TEMPERATURA INTERNA E EXTERNA
if temp_interna > 30 or temp_interna < 15: # SE A TEMPERATURA FOR MAIOR QUE 30 OU MENOR QUE 15, O SISTEMA IRÁ BLOQUEAR A DECOLAGEM.
    print("Erro: Temperatura Interna fora do range!")
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Temperatura Interna: OK")

if temp_externa > 45 or temp_externa < -10: # SE A TEMPERATURA FOR MAIOR QUE 45 OU MENOR QUE -10, O SISTEMA IRÁ BLOQUEAR A DECOLAGEM.
    print("Erro: Temperatura Externa fora do range!")   
    decolagem_autorizada = False  # Desliga a chave
else:  
    print("Temperatura Externa: OK")

# Verificação 2 - INTEGRIDADE
if integridade < 1: # SE A INTEGRIDADE FOR MENOR QUE 1, O SISTEMA IRÁ BLOQUEAR A DECOLAGEM.
    print("Erro: Integridade comprometida!")
    decolagem_autorizada = False  # Desliga a chave 
else:
    print("Integridade: OK")

# Verificação 3 - PRESSÃO DOS TANQUES
if pressao_tanques < 450 or pressao_tanques > 550: # SE A PRESSÃO FOR MENOR QUE 450 OU MAIOR QUE 550, O SISTEMA IRÁ BLOQUEAR A DECOLAGEM.
    print("Erro: Pressão dos tanques fora do range!")
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Pressão dos Tanques: OK")

# Verificação 4 - ENERGIA
if energia < 80: # SE A ENERGIA FOR MENOR QUE 80, O SISTEMA IRÁ BLOQUEAR A DECOLAGEM.
    print("Erro: Energia insuficiente!")
    decolagem_autorizada = False  # Desliga a chave
elif energia_restante < capacidade_total * RESERVA_MINIMA:
    # DECOLA MAS NÃO SOBRA CARGA PARA MANOBRA/POUSO -> TAMBÉM ABORTA.
    print("Erro: Reserva pós-decolagem insuficiente ({:.1f} kWh)!".format(energia_restante))
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Energia: OK")
    print("  Disponivel na bateria : {:.1f} kWh ({:.0f}%)".format(energia_disponivel, energia))
    print("  Consumo + perdas      : {:.1f} kWh".format(consumo_real))
    print("  Sobra apos decolagem  : {:.1f} kWh ({:.1f}%)".format(energia_restante, autonomia_restante))


# Verificação 5 - MÓDULOS ONLINE
if not modulos_online: # SE OS MÓDULOS ESTIVEREM OFFLINE, O SISTEMA IRÁ BLOQUEAR A DECOLAGEM.
    print("Erro: Módulos offline!")
    decolagem_autorizada = False  # Desliga a chave
else:
    print("Módulos: OK")

# =====================================================================
# ANÁLISE ASSISTIDA POR IA (item 1.5)
# =====================================================================
# AS VERIFICAÇÕES ACIMA OLHAM CADA PARÂMETRO SOZINHO. ESTA ETAPA CRUZA OS
# DADOS ENTRE SI, PROCURANDO DISCREPÂNCIAS QUE NENHUMA VERIFICAÇÃO ISOLADA
# CONSEGUE ENXERGAR. É UM SISTEMA ESPECIALISTA: A "INTELIGÊNCIA" ESTÁ NAS
# REGRAS DE CORRELAÇÃO ENTRE OS SENSORES.

criticos = []   # LISTA DE DADOS IMPOSSÍVEIS (TELEMETRIA NÃO CONFIÁVEL)
alertas = []    # LISTA DE COMBINAÇÕES DE RISCO (DADOS VÁLIDOS, MAS PERIGOSOS)

# --- GRUPO 1: OS DADOS INFORMADOS SÃO FISICAMENTE POSSÍVEIS? ---
if energia > 100 or energia < 0:
    criticos.append("Energia de {:.1f}% está fora do domínio físico (0 a 100%). Sensor descalibrado ou erro de digitação.".format(energia))

if integridade != 0 and integridade != 1:
    criticos.append("Integridade informada como {}. O indicador é binário (0 ou 1); valor fora disso indica corrupção de dados.".format(integridade))

if capacidade_total <= 0:
    criticos.append("Capacidade da bateria informada como {:.1f} kWh. Valor impossível.".format(capacidade_total))

if pressao_tanques < 0:
    criticos.append("Pressão negativa ({:.1f} psi) é fisicamente impossível em tanque pressurizado.".format(pressao_tanques))

# --- GRUPO 2: OS DADOS SÃO COERENTES ENTRE SI? ---
diferenca_termica = abs(temp_interna - temp_externa)  # ABS = VALOR ABSOLUTO (SEM SINAL)

if temp_externa < 0 and energia < 90:
    alertas.append("Energia em {:.0f}% com temperatura externa de {:.0f}C. Baterias de lítio perdem capacidade UTILIZÁVEL no frio: a autonomia real tende a ficar abaixo da calculada.".format(energia, temp_externa))

if pressao_tanques > 520 and temp_interna > 27:
    alertas.append("Pressão de {:.0f} psi já alta com temperatura interna de {:.0f}C. Pela lei dos gases a pressão sobe com o aquecimento, podendo ultrapassar 550 psi durante a subida.".format(pressao_tanques, temp_interna))

if diferenca_termica > 35:
    alertas.append("Diferencial térmico de {:.0f}C entre interna e externa. Sugere falha de isolamento térmico ou sensor travado.".format(diferenca_termica))

# --- GRUPO 3: ALGUM PARÂMETRO OPERA SEM MARGEM DE SEGURANÇA? ---
if 80 <= energia <= 82:
    alertas.append("Energia a {:.1f}%, no limiar dos 80% exigidos. Não sobra margem para a incerteza do próprio sensor (tipicamente +/- 2%).".format(energia))

if 450 <= pressao_tanques <= 460 or 540 <= pressao_tanques <= 550:
    alertas.append("Pressão de {:.0f} psi opera na fronteira da faixa segura (450 a 550 psi).".format(pressao_tanques))

if temp_interna >= 28:
    alertas.append("Temperatura interna de {:.0f}C próxima do teto de 30C, e o calor dos motores ainda vai somar durante a decolagem.".format(temp_interna))

if 0 < autonomia_restante < 20:
    alertas.append("Reserva pós-decolagem de apenas {:.1f}% da bateria. Pouca folga para manobra e pouso.".format(autonomia_restante))

# --- GRUPO 4: A TELEMETRIA PARECE REAL? ---
if temp_interna == 22 and temp_externa == 25 and pressao_tanques == 500 and energia == 100:
    alertas.append("Todos os canais retornaram exatamente o valor nominal. Em hardware real isso é estatisticamente improvável: conferir se os sensores não estão devolvendo valor padrão de fábrica.")

# --- RELATÓRIO DA ANÁLISE ---
print("")
print("=" * 62)
print("ANÁLISE ASSISTIDA POR IA - DIAGNÓSTICO DE DISCREPÂNCIAS")
print("=" * 62)

if criticos:  # UMA LISTA VAZIA É AVALIADA COMO FALSA PELO PYTHON
    print("")
    print("DISCREPÂNCIAS CRÍTICAS (telemetria não confiável):")
    for item in criticos:  # O FOR PERCORRE CADA ITEM GUARDADO NA LISTA
        print("  [X] " + item)

if alertas:
    print("")
    print("ALERTAS (dados válidos, mas em combinação de risco):")
    for item in alertas:
        print("  [!] " + item)

print("")
if criticos:
    print(">> PARECER: DADOS INCONSISTENTES.")
    print("   A decolagem não pode ser avaliada com telemetria corrompida.")
    decolagem_autorizada = False  # A IA TAMBÉM PODE DESLIGAR A CHAVE
elif not decolagem_autorizada:
    print(">> PARECER: DECOLAGEM JÁ BLOQUEADA pelas verificações de segurança.")
    print("   Corrigir a causa raiz antes de nova tentativa.")
elif alertas:
    print(">> PARECER: DECOLAGEM VIÁVEL, COM RESSALVAS.")
    print("   {} ponto(s) de atenção acima. Recomenda-se revisão humana.".format(len(alertas)))
else:
    print(">> PARECER: SUCESSO ABSOLUTO.")
    print("   Nenhuma discrepância encontrada no cruzamento dos dados.")

print("=" * 62)
print("")

# Verificação Final - DECOLAGEM
if decolagem_autorizada:
    print("Decolagem Autorizada!")
else:
    print("Decolagem Não Autorizada!")
