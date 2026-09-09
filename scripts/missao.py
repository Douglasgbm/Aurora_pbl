# =====================================================================
# SIMULACAO DE MISSAO - PROJETO AURORA (Terra -> Marte)
# =====================================================================
# IMPLEMENTA O upgrade.md. A IA DEIXA DE SER UM VALIDADOR DE UM UNICO
# INPUT (isso continua no main.py) E PASSA A SER UM MONITOR DE MISSAO:
# A CADA "HORA" DE SIMULACAO ELA CALCULA O SALDO DE ENERGIA, DECIDE O
# ESTADO DA NAVE (VERDE / AMARELO / VERMELHO), LIGA OU DESLIGA SISTEMAS
# POR PRIORIDADE E VIGIA A MARGEM DE RETORNO A TERRA.
#
# O FLUXO DA MISSAO:
#   FASE 0  verificacao de decolagem (reaproveita as funcoes do main.py)
#   FASE 1  saida da atmosfera e orbita terrestre  (paineis fechados)
#   FASE 2  cruzeiro interplanetario               (paineis abertos, manobras, tempestade solar)
#   FASE 3  aproximacao e captura orbital de Marte (frenagem, eclipses)
#   FASE 4  pouso e exploracao                     (pouso, tempestade de poeira)
#
# CADA MISSAO GRAVA DOIS ARQUIVOS NA PASTA "missoes":
#   registro_missoes.csv   -> UMA LINHA POR MISSAO (TABELA COMPARATIVA)
#   missao_XX_STATUS.txt   -> A "CAIXA PRETA": TODAS AS HORAS E DECISOES DA IA
#
# COMO USAR:  python scripts/missao.py
#   A PRIMEIRA PERGUNTA E O MODO DE EXIBICAO:
#     R = relatorio (a tabela de horas rolando na tela, como sempre foi)
#     P = painel ao vivo (a tela e redesenhada a cada hora, como um console de voo)
# =====================================================================

import csv
import os
from datetime import datetime

import main     # O PROGRAMA DE VERIFICACAO DE DECOLAGEM. SUAS FUNCOES VIRAM A FASE 0.
import painel   # O PAINEL DE VOO (so e usado no modo P).

# =====================================================================
# CONSTANTES DO MODELO. TUDO EM % DA BATERIA, COMO NO upgrade.md.
# ONDE O DOCUMENTO NAO DAVA O NUMERO, O VALOR ESTA MARCADO COMO "ASSUMIDO".
# =====================================================================

# --- CUSTOS PONTUAIS (upgrade.md 4.1): OS "SUSTOS" NA BATERIA ---
CUSTO_DECOLAGEM = 20.0   # sair da gravidade da Terra
CUSTO_MANOBRA = 5.0      # cada ajuste de rota durante o cruzeiro
CUSTO_FRENAGEM = 5.0     # ASSUMIDO: o documento nao da o numero; usei o de uma manobra
CUSTO_POUSO = 10.0       # retropropulsao "para nao virar um meteoro"

# --- RESERVA E ESTADOS (upgrade.md 2.2 e 3.2) ---
RESERVA_CRITICA = 30.0   # % minima para a manobra de volta a Terra
LIMIAR_VERDE = 70.0      # ASSUMIDO: bateria >= 70%  -> VERDE
LIMIAR_AMARELO = 50.0    # ASSUMIDO: 50% <= bateria < 70% -> AMARELO; abaixo -> VERMELHO
FOLGA_MARGEM = 10.0      # ASSUMIDO: o alerta de margem so desliga acima de 30 + 10, para nao piscar

# QUANTAS HORAS ENTRE UMA LINHA DE TELEMETRIA E OUTRA NA TELA.
# (upgrade.md 2.2: "reducao de frequencia de telemetria" no modo de otimizacao)
# O ARQUIVO TXT GUARDA TODAS AS HORAS; SO A TELA E REDUZIDA.
FREQUENCIA_TELEMETRIA = {"VERDE": 1, "AMARELO": 2, "VERMELHO": 4}

# --- SISTEMAS DA NAVE (upgrade.md 4.2): CONSUMO EM % POR HORA ---
# UMA LISTA DE DICIONARIOS: CADA SISTEMA E UMA "FICHA" COM NOME, CONSUMO E PRIORIDADE.
SISTEMAS = [
    {"nome": "Suporte a vida",        "consumo": 0.5, "prioridade": 1},
    {"nome": "Navegacao e IA",        "consumo": 0.3, "prioridade": 1},
    {"nome": "Comunicacao",           "consumo": 0.2, "prioridade": 2, "economico": 0.1},  # ASSUMIDO: modo economico = metade
    {"nome": "Sensores e cameras",    "consumo": 0.2, "prioridade": 3},
    {"nome": "Iluminacao e internos", "consumo": 0.1, "prioridade": 3},
]

# --- RECARGA SOLAR (upgrade.md 4.3): GANHO EM % POR HORA ---
RECARGA = {
    "total":   0.8,   # espaco aberto
    "parcial": 0.2,   # sombra parcial, nuvens ou poeira nos paineis
    "eclipse": 0.0,   # sombra total (atras de um planeta)
    "fechado": 0.0,   # paineis recolhidos (atmosfera ou tempestade solar)
}

# --- ROTAS (upgrade.md 5.2) E ROTEIRO (5.1) ---
# ASSUMIDO: as duracoes sao uma escala didatica, em "horas de simulacao".
# Uma viagem real a Marte leva ~6.000 h; com o consumo da tabela a bateria
# nao chegaria nem perto, entao o roteiro foi encurtado para a dinamica aparecer.
LIMIAR_ROTA_RAPIDA = 90.0   # bateria >= 90% -> rota rapida; abaixo -> economica
ROTAS = {
    "RAPIDA":    {"nome": "Rota Rapida",              "horas_cruzeiro": 60,  "manobras": 4},
    "ECONOMICA": {"nome": "Rota Economica (Hohmann)", "horas_cruzeiro": 100, "manobras": 2},
}
HORAS_ATMOSFERA = 2
HORAS_ORBITA_MARTE = 10
HORAS_SUPERFICIE = 24
TEMPESTADE_SOLAR = {"inicio": 30, "duracao": 6}    # hora do cruzeiro em que comeca, e quantas horas dura
TEMPESTADE_POEIRA = {"inicio": 8, "duracao": 12}   # hora na superficie em que comeca, e quantas horas dura

# --- MODO DE EXIBICAO ---
# False = RELATORIO (as linhas vao aparecendo na tela). True = PAINEL AO VIVO
# (a tela e desenhada pelo painel.py e o relatorio fica mudo, so vai para o TXT).
# NAO E UMA CONSTANTE: executar_missao() LIGA ESTA CHAVE QUANDO O USUARIO ESCOLHE "P".
MODO_PAINEL = False


# =====================================================================
# FUNCOES DE APOIO
# =====================================================================
def anotar(relatorio, texto, mostrar=True):
    # GUARDA SEMPRE NO RELATORIO (A "CAIXA PRETA" QUE VAI PARA O TXT).
    # MOSTRA NA TELA SO SE mostrar FOR True (E O PADRAO) E O PAINEL NAO ESTIVER LIGADO:
    # NO MODO PAINEL, QUALQUER print() SOLTO EMPURRARIA O PAINEL PARA CIMA.
    relatorio.append(texto)
    if mostrar and not MODO_PAINEL:
        print(texto)


def escolher_rota(energia):
    # upgrade.md 5.2: A IA DECIDE A ROTA COM BASE NA BATERIA.
    if energia >= LIMIAR_ROTA_RAPIDA:
        return "RAPIDA"
    return "ECONOMICA"


def montar_roteiro(rota):
    # upgrade.md 5.1 e 5.3: A LISTA DE FASES ("CHECKPOINTS") DA MISSAO.
    # A DURACAO DO CRUZEIRO E O NUMERO DE MANOBRAS DEPENDEM DA ROTA.
    horas_cruzeiro = ROTAS[rota]["horas_cruzeiro"]
    quantidade = ROTAS[rota]["manobras"]

    # ESPALHA AS MANOBRAS POR IGUAL AO LONGO DO CRUZEIRO.
    # ex: 100 h e 2 manobras -> intervalo 33 -> manobras nas horas 33 e 66.
    intervalo = horas_cruzeiro // (quantidade + 1)
    horas_de_manobra = []
    for numero in range(1, quantidade + 1):
        horas_de_manobra.append(intervalo * numero)

    roteiro = [
        {"local": "Atmosfera",       "nome": "Saida da atmosfera e orbita terrestre",
         "horas": HORAS_ATMOSFERA,    "paineis": "fechado",   "manobras": []},
        {"local": "Espaco Profundo", "nome": "Cruzeiro interplanetario",
         "horas": horas_cruzeiro,     "paineis": "total",     "manobras": horas_de_manobra},
        {"local": "Orbita de Marte", "nome": "Aproximacao e captura orbital",
         "horas": HORAS_ORBITA_MARTE, "paineis": "alternado", "manobras": []},
        {"local": "Superficie",      "nome": "Pouso e exploracao",
         "horas": HORAS_SUPERFICIE,   "paineis": "total",     "manobras": []},
    ]
    return roteiro


def definir_clima(fase, hora_na_fase):
    # OS RISCOS DO upgrade.md 5.1: TEMPESTADE SOLAR NO CRUZEIRO E DE POEIRA NA SUPERFICIE.
    # SAO PROGRAMADOS (NAO ALEATORIOS) PARA A MESMA ENTRADA DAR SEMPRE O MESMO RESULTADO.
    if fase["local"] == "Espaco Profundo":
        inicio = TEMPESTADE_SOLAR["inicio"]
        fim = inicio + TEMPESTADE_SOLAR["duracao"]
        if inicio <= hora_na_fase < fim:
            return "tempestade_solar"
    if fase["local"] == "Superficie":
        inicio = TEMPESTADE_POEIRA["inicio"]
        fim = inicio + TEMPESTADE_POEIRA["duracao"]
        if inicio <= hora_na_fase < fim:
            return "tempestade_poeira"
    return "normal"


def definir_exposicao(fase, hora_na_fase, clima):
    # QUANTO SOL CHEGA NOS PAINEIS NESTA HORA (upgrade.md 4.3 e 5.1).
    if fase["paineis"] == "fechado":
        return "fechado"
    if clima == "tempestade_solar":
        return "fechado"      # A IA RECOLHEU OS PAINEIS PARA PROTEGER OS CIRCUITOS
    if clima == "tempestade_poeira":
        return "parcial"      # POEIRA COBRINDO OS PAINEIS
    if fase["paineis"] == "alternado":
        if hora_na_fase % 2 == 0:
            return "eclipse"  # HORAS PARES: A NAVE PASSA POR TRAS DE MARTE
        return "total"
    return fase["paineis"]


def calcular_margem(energia, gasto_liquido, horas_com_paineis, horas_retorno):
    # upgrade.md 3.2:  Margem = Energia Atual - (Consumo Medio x Tempo de Retorno)
    # CONSUMO MEDIO = QUANTO A BATERIA CAIU POR HORA DESDE QUE OS PAINEIS ABRIRAM
    # (JA DESCONTANDO A RECARGA). TEMPO DE RETORNO = UM CRUZEIRO INTEIRO DE VOLTA.
    if horas_com_paineis == 0:
        consumo_medio = 0.0
    else:
        consumo_medio = max(gasto_liquido, 0.0) / horas_com_paineis
    custo_retorno = consumo_medio * horas_retorno
    margem = energia - custo_retorno
    return margem, custo_retorno


def piorar(estado):
    # DESCE UM DEGRAU: VERDE -> AMARELO -> VERMELHO (E VERMELHO FICA VERMELHO).
    if estado == "VERDE":
        return "AMARELO"
    return "VERMELHO"


def decidir_estado(energia, alerta_margem, clima):
    # upgrade.md 2.2: O ESTADO DE SAUDE DA NAVE.
    if clima != "normal":
        return "VERMELHO"     # MODO DE PROTECAO (tempestade solar) OU SOBREVIVENCIA (poeira)

    if energia >= LIMIAR_VERDE:
        estado = "VERDE"
    elif energia >= LIMIAR_AMARELO:
        estado = "AMARELO"
    else:
        estado = "VERMELHO"

    # upgrade.md 3.2: SE A MARGEM DE RETORNO ESTA AMEACADA, DESLIGA MAIS UM DEGRAU.
    if alerta_margem:
        estado = piorar(estado)
    return estado


def consumo_do_estado(estado):
    # upgrade.md 2.1 e 2.2: QUAIS SISTEMAS FICAM LIGADOS EM CADA ESTADO, E QUANTO CONSOMEM.
    #   VERDE    -> tudo ligado
    #   AMARELO  -> prioridade 3 desligada, comunicacao em modo economico
    #   VERMELHO -> so prioridade 1 (o essencial)
    total = 0.0
    ligados = []
    for sistema in SISTEMAS:
        prioridade = sistema["prioridade"]
        if estado == "VERDE":
            ligado = True
        elif estado == "AMARELO":
            ligado = prioridade <= 2
        else:
            ligado = prioridade == 1

        if not ligado:
            continue  # PULA PARA O PROXIMO SISTEMA DA LISTA

        consumo = sistema["consumo"]
        if estado == "AMARELO" and "economico" in sistema:
            consumo = sistema["economico"]
        total = total + consumo
        ligados.append(sistema["nome"])
    return total, ligados


def descrever_estado(estado):
    if estado == "VERDE":
        return "performance maxima, todos os sistemas ativos"
    if estado == "AMARELO":
        return "MODO DE OTIMIZACAO: prioridade 3 desligada, comunicacao economica, telemetria a cada 2 h"
    return "MODO DE SOBREVIVENCIA: prioridades 2 e 3 desligadas, so o essencial, telemetria a cada 4 h"


def aplicar_evento(relatorio, energia, custo, descricao):
    # UM GASTO PONTUAL (upgrade.md 4.1). A BATERIA NUNCA FICA NEGATIVA.
    energia = max(energia - custo, 0.0)
    anotar(relatorio, "[EVENTO] {}: -{:.1f}%  -> bateria em {:.1f}%".format(descricao, custo, energia))
    return energia


# =====================================================================
# A SIMULACAO EM SI: O LOOP DE HORAS (upgrade.md 4.4)
# =====================================================================
def simular_missao(energia_inicial, rota, classificacao_decolagem):
    relatorio = []
    roteiro = montar_roteiro(rota)
    horas_totais = 0
    for fase in roteiro:
        horas_totais = horas_totais + fase["horas"]
    horas_retorno = ROTAS[rota]["horas_cruzeiro"]   # VOLTAR = UM CRUZEIRO INTEIRO NO SENTIDO CONTRARIO

    # --- O ESTADO DA NAVE, QUE MUDA A CADA HORA ---
    energia = energia_inicial
    energia_apos_decolagem = energia_inicial
    hora_missao = 0
    estado = "VERDE"
    clima = "normal"
    alerta_margem = False        # A IA JA PERCEBEU QUE A VOLTA ESTA AMEACADA?
    em_risco = False             # A MISSAO ESTA EM RISCO NESTE MOMENTO?
    avisos_risco = 0             # QUANTAS VEZES A IA DECLAROU "MISSAO EM RISCO"
    horas_por_estado = {"VERDE": 0, "AMARELO": 0, "VERMELHO": 0}
    bateria_minima = energia
    hora_da_minima = 0
    energia_ao_abrir_paineis = None   # None = OS PAINEIS AINDA NAO ABRIRAM
    horas_com_paineis = 0
    falhou = False
    historico = []           # A BATERIA AO FIM DE CADA HORA (PARA O GRAFICO DO PAINEL)
    ultimo_painel = None     # OS DADOS DA ULTIMA HORA DESENHADA (PARA A TELA FINAL)

    # --- CABECALHO DO RELATORIO ---
    anotar(relatorio, "=" * 78)
    anotar(relatorio, "PROJETO AURORA - SIMULACAO DE MISSAO TERRA -> MARTE")
    anotar(relatorio, "=" * 78)
    anotar(relatorio, "Verificacao de decolagem : {} (bateria em {:.1f}%)".format(classificacao_decolagem, energia_inicial))
    anotar(relatorio, "Rota escolhida pela IA   : {} ({} h de cruzeiro, {} manobra(s))".format(
        ROTAS[rota]["nome"], ROTAS[rota]["horas_cruzeiro"], ROTAS[rota]["manobras"]))
    anotar(relatorio, "Reserva critica de volta : {:.0f}% da bateria".format(RESERVA_CRITICA))
    anotar(relatorio, "")
    anotar(relatorio, "SISTEMAS DA NAVE (consumo em % por hora)")
    for sistema in SISTEMAS:
        anotar(relatorio, "  P{}  {:<22} {:.1f}%/h".format(sistema["prioridade"], sistema["nome"], sistema["consumo"]))

    cabecalho = "{:>4} | {:<15} | {:<8} | {:<8} | {:>5} | {:>5} | {:>5} | {:>7} | {:>6}".format(
        "HORA", "FASE", "PAINEIS", "ESTADO", "CONS", "RECAR", "SALDO", "BATERIA", "MARGEM")

    # --- UMA FASE DE CADA VEZ ---
    for fase in roteiro:
        local = fase["local"]
        anotar(relatorio, "")
        anotar(relatorio, "-" * 78)
        anotar(relatorio, "FASE: {} ({} h)".format(fase["nome"], fase["horas"]))
        anotar(relatorio, "-" * 78)

        # ---- CHECKPOINT (upgrade.md 5.3): O QUE A IA FAZ AO ENTRAR NA FASE ----
        if local == "Atmosfera":
            anotar(relatorio, "[IA] Decolagem. Monitorando a estabilidade da subida. Paineis fechados (atrito da atmosfera).")
            energia = aplicar_evento(relatorio, energia, CUSTO_DECOLAGEM, "Decolagem / ignicao")
            energia_apos_decolagem = energia

        elif local == "Espaco Profundo":
            anotar(relatorio, "[IA] Saindo da atmosfera. Autorizando abertura dos paineis solares. Recarga ativa.")
            anotar(relatorio, "[IA] Plano de voo: {} manobra(s) de correcao nas horas {} do cruzeiro.".format(
                len(fase["manobras"]), fase["manobras"]))
            energia_ao_abrir_paineis = energia
            horas_com_paineis = 0

        elif local == "Orbita de Marte":
            anotar(relatorio, "[IA] Iniciando manobra de frenagem para captura orbital.")
            if energia - CUSTO_FRENAGEM < RESERVA_CRITICA:
                anotar(relatorio, "[IA] AVISO: apos a frenagem a bateria fica abaixo da reserva de retorno ({:.0f}%). MISSAO EM RISCO.".format(RESERVA_CRITICA))
                avisos_risco = avisos_risco + 1
            energia = aplicar_evento(relatorio, energia, CUSTO_FRENAGEM, "Frenagem orbital")
            anotar(relatorio, "[IA] Em orbita. A nave passa por tras de Marte hora sim, hora nao: eclipse corta a recarga.")

        elif local == "Superficie":
            anotar(relatorio, "[IA] Iniciando descida com retropropulsao.")
            if energia - CUSTO_POUSO < RESERVA_CRITICA:
                anotar(relatorio, "[IA] AVISO: apos o pouso a bateria fica abaixo da reserva de retorno ({:.0f}%). MISSAO EM RISCO.".format(RESERVA_CRITICA))
                avisos_risco = avisos_risco + 1
            energia = aplicar_evento(relatorio, energia, CUSTO_POUSO, "Pouso / retropropulsao")
            anotar(relatorio, "[IA] Pouso concluido. Monitorando acumulo de poeira nos paineis.")

        anotar(relatorio, cabecalho)

        # ---- O LOOP DE HORAS DESTA FASE ----
        for hora_na_fase in range(1, fase["horas"] + 1):
            hora_missao = hora_missao + 1
            houve_evento = False   # SE ALGO ACONTECEU, A LINHA DESTA HORA APARECE NA TELA

            # 1) CLIMA: COMECOU OU TERMINOU UMA TEMPESTADE?
            clima_novo = definir_clima(fase, hora_na_fase)
            if clima_novo != clima:
                if clima_novo == "tempestade_solar":
                    anotar(relatorio, "[IA] Tempestade solar detectada! Recolhendo os paineis e entrando em MODO DE PROTECAO.")
                elif clima_novo == "tempestade_poeira":
                    anotar(relatorio, "[IA] Tempestade de poeira! Recarga solar caindo. Desligando tudo que nao e essencial para sobreviver.")
                else:
                    anotar(relatorio, "[IA] Condicoes normalizadas. Retomando a operacao.")
                clima = clima_novo
                houve_evento = True

            # 2) MANOBRA PROGRAMADA NESTA HORA?
            if hora_na_fase in fase["manobras"]:
                energia = aplicar_evento(relatorio, energia, CUSTO_MANOBRA, "Manobra de correcao de rota")
                houve_evento = True

            # 3) MARGEM DE RETORNO (upgrade.md 3.2)
            if energia_ao_abrir_paineis is None:
                gasto_liquido = 0.0
            else:
                gasto_liquido = energia_ao_abrir_paineis - energia
            margem, custo_retorno = calcular_margem(energia, gasto_liquido, horas_com_paineis, horas_retorno)

            if energia_ao_abrir_paineis is not None:
                if not alerta_margem and margem < RESERVA_CRITICA:
                    alerta_margem = True
                    houve_evento = True
                    anotar(relatorio, "[IA] Margem de retorno ameacada: no ritmo atual a volta custaria {:.1f}%, sobrariam {:.1f}% (minimo {:.0f}%). Iniciando desligamento escalonado.".format(
                        custo_retorno, margem, RESERVA_CRITICA))
                elif alerta_margem and margem >= RESERVA_CRITICA + FOLGA_MARGEM:
                    alerta_margem = False
                    houve_evento = True
                    anotar(relatorio, "[IA] Margem de retorno recuperada ({:.1f}%). Liberando sistemas.".format(margem))

            # 4) ESTADO DA NAVE (upgrade.md 2.2)
            estado_novo = decidir_estado(energia, alerta_margem, clima)
            if estado_novo != estado:
                anotar(relatorio, "[IA] Estado {} -> {}: {}.".format(estado, estado_novo, descrever_estado(estado_novo)))
                estado = estado_novo
                houve_evento = True

            if estado == "VERMELHO" and alerta_margem and not em_risco:
                em_risco = True
                avisos_risco = avisos_risco + 1
                houve_evento = True
                anotar(relatorio, "[IA] *** MISSAO EM RISCO: mesmo so com o essencial, a reserva de retorno nao esta garantida. ***")
            if em_risco and (estado != "VERMELHO" or not alerta_margem):
                em_risco = False

            # 5) O BALANCO DA HORA (upgrade.md 4.4): Saldo = Recarga - Soma dos Sistemas Ativos
            consumo, ligados = consumo_do_estado(estado)
            exposicao = definir_exposicao(fase, hora_na_fase, clima)
            recarga = RECARGA[exposicao]
            saldo = recarga - consumo
            energia = energia + saldo
            energia = min(max(energia, 0.0), 100.0)   # A BATERIA FICA ENTRE 0 E 100

            # 6) ESTATISTICAS PARA O RESUMO
            horas_por_estado[estado] = horas_por_estado[estado] + 1
            if energia_ao_abrir_paineis is not None:
                horas_com_paineis = horas_com_paineis + 1
            if energia < bateria_minima:
                bateria_minima = energia
                hora_da_minima = hora_missao
            historico.append(energia)

            # 7) A LINHA DE TELEMETRIA DESTA HORA
            linha = "{:>4} | {:<15} | {:<8} | {:<8} | {:>5.2f} | {:>5.2f} | {:>+5.2f} | {:>6.1f}% | {:>6.1f}".format(
                hora_missao, local, exposicao, estado, consumo, recarga, saldo, energia, margem)
            mostrar = houve_evento or (hora_na_fase % FREQUENCIA_TELEMETRIA[estado] == 0)
            anotar(relatorio, linha, mostrar)

            # 8) PAINEL AO VIVO (opcional): REDESENHA A TELA COM OS NUMEROS DESTA HORA.
            #    O PAINEL NAO CONHECE A SIMULACAO; ELE SO RECEBE ESTE DICIONARIO E DESENHA.
            if MODO_PAINEL:
                ultimo_painel = {
                    "hora": hora_missao,
                    "horas_totais": horas_totais,
                    "rota": ROTAS[rota]["nome"],
                    "fase": fase["nome"],
                    "exposicao": exposicao,
                    "estado": estado,
                    "energia": energia,
                    "margem": margem,
                    "reserva": RESERVA_CRITICA,
                    "consumo": consumo,
                    "recarga": recarga,
                    "saldo": saldo,
                    "sistemas": SISTEMAS,
                    "ligados": ligados,
                    "historico": historico[-40:],   # SO AS ULTIMAS 40 HORAS CABEM NA TELA
                    "relatorio": relatorio,
                    "status": None,
                    "resumo": None,
                }
                painel.desenhar(ultimo_painel, houve_evento)

            if energia <= 0:
                anotar(relatorio, "[FALHA] Bateria esgotada na hora {}. A nave perdeu o suporte a vida.".format(hora_missao))
                falhou = True
                break   # SAI DO LOOP DE HORAS

        if falhou:
            break       # SAI DO LOOP DE FASES

    # --- STATUS FINAL ---
    if falhou:
        status = "FALHA"
    elif avisos_risco > 0 or energia < RESERVA_CRITICA:
        status = "CONCLUIDA COM RISCO"
    else:
        status = "SUCESSO"

    resumo = {
        "status": status,
        "energia_inicial": energia_inicial,
        "rota": ROTAS[rota]["nome"],
        "horas": hora_missao,
        "bateria_final": energia,
        "bateria_minima": bateria_minima,
        "horas_verde": horas_por_estado["VERDE"],
        "horas_amarelo": horas_por_estado["AMARELO"],
        "horas_vermelho": horas_por_estado["VERMELHO"],
        "avisos_risco": avisos_risco,
    }

    # NO MODO PAINEL, DESENHA UMA ULTIMA VEZ COM O STATUS E O RESUMO DENTRO DO QUADRO.
    if MODO_PAINEL and ultimo_painel is not None:
        ultimo_painel["status"] = status
        ultimo_painel["resumo"] = resumo
        painel.desenhar(ultimo_painel, True)
        print("")

    anotar(relatorio, "")
    anotar(relatorio, "=" * 78)
    anotar(relatorio, "RESUMO DA MISSAO")
    anotar(relatorio, "=" * 78)
    anotar(relatorio, "Rota                : {}".format(ROTAS[rota]["nome"]))
    anotar(relatorio, "Horas simuladas     : {}".format(hora_missao))
    anotar(relatorio, "Bateria             : inicial {:.1f}% | apos decolagem {:.1f}% | final {:.1f}%".format(
        energia_inicial, energia_apos_decolagem, energia))
    anotar(relatorio, "Bateria minima      : {:.1f}% (hora {})".format(bateria_minima, hora_da_minima))
    anotar(relatorio, "Horas por estado    : VERDE {} | AMARELO {} | VERMELHO {}".format(
        horas_por_estado["VERDE"], horas_por_estado["AMARELO"], horas_por_estado["VERMELHO"]))
    anotar(relatorio, "Avisos de risco     : {}".format(avisos_risco))
    anotar(relatorio, "STATUS              : {}".format(status))
    anotar(relatorio, "=" * 78)
    return resumo, relatorio


# =====================================================================
# REGISTRO DA MISSAO (MESMO PADRAO DO registrar_cenario DO main.py)
# =====================================================================
def registrar_missao(resumo, relatorio):
    pasta_scripts = os.path.dirname(os.path.abspath(__file__))
    pasta_missoes = os.path.normpath(os.path.join(pasta_scripts, "..", "missoes"))
    os.makedirs(pasta_missoes, exist_ok=True)
    arquivo_csv = os.path.join(pasta_missoes, "registro_missoes.csv")

    numero_missao = 1
    if os.path.exists(arquivo_csv):
        arquivo = open(arquivo_csv, "r", encoding="utf-8-sig")
        numero_missao = len(arquivo.readlines())
        arquivo.close()

    cabecalho = ["missao", "data_hora", "status", "energia_inicial_pct", "rota", "horas",
                 "bateria_final_pct", "bateria_minima_pct",
                 "horas_verde", "horas_amarelo", "horas_vermelho", "avisos_risco"]
    linha = [numero_missao,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             resumo["status"], resumo["energia_inicial"], resumo["rota"], resumo["horas"],
             round(resumo["bateria_final"], 1), round(resumo["bateria_minima"], 1),
             resumo["horas_verde"], resumo["horas_amarelo"], resumo["horas_vermelho"],
             resumo["avisos_risco"]]

    csv_ja_existe = os.path.exists(arquivo_csv)
    arquivo = open(arquivo_csv, "a", newline="", encoding="utf-8-sig")
    escritor = csv.writer(arquivo, delimiter=";")
    if not csv_ja_existe:
        escritor.writerow(cabecalho)
    escritor.writerow(linha)
    arquivo.close()

    # NO NOME DO ARQUIVO O STATUS VIRA UMA PALAVRA SO: SUCESSO, RISCO OU FALHA.
    if resumo["status"] == "CONCLUIDA COM RISCO":
        rotulo = "RISCO"
    else:
        rotulo = resumo["status"]
    nome_txt = "missao_{:02d}_{}.txt".format(numero_missao, rotulo)
    arquivo_txt = os.path.join(pasta_missoes, nome_txt)

    conteudo = ["Missao Nº {:02d}  |  {}".format(numero_missao, datetime.now().strftime("%d/%m/%Y %H:%M:%S")), ""]
    arquivo = open(arquivo_txt, "w", encoding="utf-8")
    arquivo.write("\n".join(conteudo + relatorio))
    arquivo.close()

    print("")
    print("Missao registrada como {} (status: {})".format(nome_txt, resumo["status"]))
    print("Planilha acumulada em: missoes/registro_missoes.csv")


# =====================================================================
# O FLUXO COMPLETO: FASE 0 (main.py) E DEPOIS A MISSAO
# =====================================================================
def executar_missao():
    # "global" AVISA O PYTHON QUE MODO_PAINEL AQUI E A CAIXA DE FORA (A DO TOPO DO
    # ARQUIVO), E NAO UMA VARIAVEL NOVA SO DESTA FUNCAO. SEM ISSO, A LINHA
    # "MODO_PAINEL = True" CRIARIA UMA COPIA LOCAL E anotar() NUNCA FICARIA SABENDO.
    global MODO_PAINEL

    print("=" * 78)
    print("PROJETO AURORA - SIMULACAO DE MISSAO")
    print("=" * 78)
    resposta = input("Modo de exibicao: [R] relatorio  [P] painel ao vivo  (padrao R): ").strip().upper()
    if resposta == "P":
        MODO_PAINEL = True
        painel.preparar_terminal()
        painel.verificar_tamanho()

    print("")
    print("=" * 78)
    print("FASE 0: VERIFICACAO DE DECOLAGEM")
    print("=" * 78)
    print("")

    # registrar=False: A VERIFICACAO DA MISSAO NAO GRAVA UM CENARIO NA PASTA cenarios/
    resultado = main.executar_verificacao(registrar=False)

    if not resultado["decolagem_autorizada"]:
        print("")
        print("MISSAO CANCELADA: a verificacao de decolagem nao autorizou o lancamento.")
        return

    energia_inicial = resultado["telemetria"]["energia"]
    rota = escolher_rota(energia_inicial)

    print("")
    if rota == "RAPIDA":
        print("[IA] Bateria em {:.1f}% (>= {:.0f}%): escolhendo a {}.".format(energia_inicial, LIMIAR_ROTA_RAPIDA, ROTAS[rota]["nome"]))
    else:
        print("[IA] Bateria em {:.1f}% (< {:.0f}%): escolhendo a {}.".format(energia_inicial, LIMIAR_ROTA_RAPIDA, ROTAS[rota]["nome"]))
    print("[IA] Nota: no modelo de missao a decolagem custa {:.0f}% da bateria (upgrade.md 4.1).".format(CUSTO_DECOLAGEM))
    print("     A verificacao acima usa 300 kWh + 8% de perdas (32.4%). Sao dois modelos; ver upgrade.md, secao 6.")
    print("")

    if MODO_PAINEL:
        input("Pressione Enter para iniciar a contagem regressiva... ")
        painel.contagem_regressiva()

    resumo, relatorio = simular_missao(energia_inicial, rota, resultado["classificacao"])
    registrar_missao(resumo, relatorio)


if __name__ == "__main__":
    executar_missao()
