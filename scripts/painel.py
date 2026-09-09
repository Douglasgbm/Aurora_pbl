# =====================================================================
# PAINEL DE VOO - PROJETO AURORA
# =====================================================================
# DESENHA NO TERMINAL, A CADA HORA DA MISSAO, UM PAINEL ESTILO CONSOLE DE
# FOGUETE: BARRAS DE BATERIA E MARGEM, ESTADO DA NAVE, SISTEMAS LIGADOS,
# HISTORICO DA CARGA E AS ULTIMAS MENSAGENS DA IA.
#
# NAO USA NENHUMA BIBLIOTECA EXTERNA. SO print(), TEXTO E TRES TRUQUES
# DO PROPRIO TERMINAL:
#   1. CODIGOS DE COR: "\033[32m" DEIXA O TEXTO VERDE, "\033[0m" VOLTA AO NORMAL.
#   2. LIMPAR A TELA: "\033[2J" APAGA TUDO. USADO UMA VEZ SO, NO INICIO.
#   3. VOLTAR AO TOPO: "\033[H" LEVA O CURSOR PARA O CANTO SUPERIOR ESQUERDO.
#      A CADA HORA O PAINEL E ESCRITO POR CIMA DO ANTERIOR, LINHA POR LINHA.
#      COMO TODAS AS LINHAS TEM A MESMA LARGURA, NAO SOBRA NADA DO QUADRO
#      VELHO. E POR ISSO QUE O PAINEL FICA PARADO NO LUGAR, SEM PISCAR E
#      SEM EMPILHAR.
#
# ESTE ARQUIVO NAO SABE NADA DA SIMULACAO. ELE SO RECEBE UM DICIONARIO
# COM OS NUMEROS DA HORA E DESENHA. QUEM CHAMA E O missao.py.
# =====================================================================

import os
import shutil     # DESCOBRE O TAMANHO DA JANELA DO TERMINAL
import sys
import time
import textwrap   # QUEBRA TEXTOS LONGOS EM VARIAS LINHAS

LARGURA = 64            # LARGURA INTERNA DO PAINEL, EM CARACTERES
LARGURA_BARRA = 30      # TAMANHO DAS BARRAS DE BATERIA E MARGEM
ALTURA_PAINEL = 24      # LINHAS QUE O PAINEL OCUPA NO QUADRO FINAL (COM O RESUMO)
PAUSA = 0.15            # SEGUNDOS ENTRE UMA HORA E OUTRA: A "VELOCIDADE" DA VIAGEM
PAUSA_EVENTO = 1.2      # PAUSA MAIOR QUANDO A IA FEZ ALGO, PARA DAR TEMPO DE LER
LINHAS_DE_MENSAGEM = 3  # QUANTAS LINHAS O QUADRO DE MENSAGENS OCUPA

# CODIGOS DE COR DO TERMINAL. AS TRES PRIMEIRAS CHAVES SAO OS NOMES DOS
# ESTADOS DA NAVE, ENTAO COR[estado] JA DA A COR CERTA.
COR = {
    "VERDE": "\033[32m",
    "AMARELO": "\033[33m",
    "VERMELHO": "\033[31m",
    "ciano": "\033[36m",
    "cinza": "\033[90m",
    "negrito": "\033[1m",
    "normal": "\033[0m",
}

DESCRICAO_CURTA = {
    "VERDE": "performance maxima",
    "AMARELO": "modo de otimizacao",
    "VERMELHO": "modo de sobrevivencia",
}

BLOCOS = " ▁▂▃▄▅▆▇█"   # 9 ALTURAS PARA O HISTORICO: ESPACO = VAZIO, █ = CHEIO


# =====================================================================
# PECAS BASICAS
# =====================================================================
def preparar_terminal():
    # NO PROMPT ANTIGO DO WINDOWS OS CODIGOS DE COR SO FUNCIONAM DEPOIS
    # DESTA CHAMADA VAZIA. NO MAC, LINUX E WINDOWS TERMINAL NAO FAZ NADA.
    if os.name == "nt":
        os.system("")


def verificar_tamanho():
    # O PAINEL SO FICA PARADO NO LUGAR SE COUBER INTEIRO NA JANELA.
    # SE O TERMINAL FOR BAIXO DEMAIS, AVISA E ESPERA O USUARIO AUMENTAR.
    tamanho = shutil.get_terminal_size()
    while tamanho.lines < ALTURA_PAINEL or tamanho.columns < LARGURA + 4:
        print("")
        print("O terminal tem {} linhas x {} colunas. O painel precisa de {} linhas x {} colunas.".format(
            tamanho.lines, tamanho.columns, ALTURA_PAINEL, LARGURA + 4))
        print("Aumente a janela (no VS Code, maximize o terminal pelo botao ^ do canto) e aperte Enter.")
        input()
        tamanho = shutil.get_terminal_size()


def limpar_tela():
    print("\033[2J\033[H", end="")


def voltar_ao_topo():
    print("\033[H", end="")


def colorir(texto, cor):
    return COR[cor] + texto + COR["normal"]


def barra(valor, maximo, largura):
    # ex: barra(63.2, 100, 30) -> "███████████████████░░░░░░░░░░░"
    valor = max(min(valor, maximo), 0)          # PRENDE O VALOR ENTRE 0 E O MAXIMO
    cheio = int(round(largura * valor / maximo))
    return "█" * cheio + "░" * (largura - cheio)


def sparkline(valores, maximo):
    # UM CARACTERE POR VALOR. QUANTO MAIS ALTO O BLOCO, MAIS BATERIA.
    texto = ""
    ultimo = len(BLOCOS) - 1
    for valor in valores:
        valor = max(min(valor, maximo), 0)
        indice = int(round(ultimo * valor / maximo))
        texto = texto + BLOCOS[indice]
    return texto


def linha(texto, cor=None):
    # UMA LINHA DO PAINEL, COM AS BORDAS LATERAIS.
    # O TEXTO E CORTADO SE PASSAR DA LARGURA, OU COMPLETADO COM ESPACOS SE FALTAR.
    # A COR E APLICADA DEPOIS DE COMPLETAR, PORQUE OS CODIGOS DE COR SAO
    # CARACTERES INVISIVEIS QUE ATRAPALHARIAM A CONTAGEM.
    texto = texto[:LARGURA]
    texto = texto + " " * (LARGURA - len(texto))
    if cor is not None:
        texto = colorir(texto, cor)
    return "║ " + texto + " ║"


def borda(posicao):
    meio = "═" * (LARGURA + 2)
    if posicao == "topo":
        return "╔" + meio + "╗"
    if posicao == "base":
        return "╚" + meio + "╝"
    return "╠" + meio + "╣"


def ultimas_mensagens(relatorio, quantidade_de_linhas):
    # PEGA AS LINHAS DO RELATORIO QUE COMECAM COM "[" (AS DA IA E DOS EVENTOS),
    # QUEBRA CADA UMA PARA CABER NO PAINEL E DEVOLVE SO AS ULTIMAS N LINHAS.
    linhas = []
    for texto in relatorio:
        if texto.startswith("["):
            linhas = linhas + textwrap.wrap(texto, LARGURA)
    return linhas[-quantidade_de_linhas:]   # FATIA NEGATIVA: OS ULTIMOS N ITENS


# =====================================================================
# AS TELAS
# =====================================================================
def contagem_regressiva():
    limpar_tela()
    print(borda("topo"))
    print(linha("PROJETO AURORA  ·  DECOLAGEM AUTORIZADA", "VERDE"))
    print(borda("base"))
    print("")
    for numero in [3, 2, 1]:
        print("   DECOLAGEM EM {} ...".format(numero))
        sys.stdout.flush()   # FORCA O TEXTO A APARECER AGORA, ANTES DA PAUSA
        time.sleep(1)
    print("   IGNICAO!")
    sys.stdout.flush()
    time.sleep(1)


def desenhar(dados, houve_evento=False):
    # dados E UM DICIONARIO MONTADO PELO missao.py COM OS NUMEROS DESTA HORA.
    # O PAINEL E ESCRITO POR CIMA DO ANTERIOR, SEMPRE COM O MESMO NUMERO DE LINHAS.
    estado = dados["estado"]

    voltar_ao_topo()
    print(borda("topo"))

    titulo = "PROJETO AURORA  ·  MISSAO TERRA -> MARTE"
    relogio = "HORA {:>3} / {}".format(dados["hora"], dados["horas_totais"])
    espaco = " " * (LARGURA - len(titulo) - len(relogio))
    print(linha(titulo + espaco + relogio, "negrito"))
    print(borda("meio"))

    print(linha("ROTA      {:<30} PAINEIS  {}".format(dados["rota"], dados["exposicao"])))
    print(linha("FASE      {}".format(dados["fase"])))
    print(linha("ESTADO    ● {:<10} {}".format(estado, DESCRICAO_CURTA[estado]), estado))

    energia = dados["energia"]
    print(linha("BATERIA   {} {:5.1f}%".format(barra(energia, 100, LARGURA_BARRA), energia), estado))

    margem = dados["margem"]
    reserva = dados["reserva"]
    if margem < reserva:
        aviso = "▼ RESERVA {:.0f}%".format(reserva)
        cor_margem = "VERMELHO"
    else:
        aviso = "reserva {:.0f}%".format(reserva)
        cor_margem = "ciano"
    print(linha("MARGEM    {} {:5.1f}%  {}".format(barra(margem, 100, LARGURA_BARRA), margem, aviso), cor_margem))

    print(linha("CONSUMO   {:.2f} %/h     RECARGA  {:.2f} %/h     SALDO  {:+.2f} %/h".format(
        dados["consumo"], dados["recarga"], dados["saldo"])))

    rotulo = "SISTEMAS "   # SO A PRIMEIRA LINHA DE SISTEMA LEVA O ROTULO
    for sistema in dados["sistemas"]:
        nome = sistema["nome"]
        if nome in dados["ligados"]:
            if estado == "AMARELO" and "economico" in sistema:
                situacao = "● ECO"
                cor = "AMARELO"
            else:
                situacao = "● ON"
                cor = "VERDE"
        else:
            situacao = "○ OFF"
            cor = "cinza"
        print(linha("{} P{}  {:<24} {}".format(rotulo, sistema["prioridade"], nome, situacao), cor))
        rotulo = "         "

    historico = dados["historico"]
    print(linha("HISTORICO {}  ({} h)".format(sparkline(historico, 100), len(historico)), "ciano"))
    print(borda("meio"))

    # QUADRO DE MENSAGENS: SEMPRE O MESMO NUMERO DE LINHAS, PARA O PAINEL NAO "PULAR".
    mensagens = ultimas_mensagens(dados["relatorio"], LINHAS_DE_MENSAGEM)
    while len(mensagens) < LINHAS_DE_MENSAGEM:
        mensagens = [""] + mensagens
    for texto in mensagens:
        print(linha(texto, "cinza"))

    # NO QUADRO FINAL, O RESUMO ENTRA DENTRO DO PROPRIO PAINEL.
    if dados["status"] is not None:
        resumo = dados["resumo"]
        print(borda("meio"))
        print(linha("STATUS    {}".format(dados["status"]), "negrito"))
        print(linha("BATERIA   final {:.1f}%  |  minima {:.1f}%  |  avisos de risco {}".format(
            resumo["bateria_final"], resumo["bateria_minima"], resumo["avisos_risco"])))
        print(linha("HORAS     VERDE {}  |  AMARELO {}  |  VERMELHO {}  |  total {}".format(
            resumo["horas_verde"], resumo["horas_amarelo"], resumo["horas_vermelho"], resumo["horas"])))

    print(borda("base"))
    sys.stdout.flush()

    if houve_evento:
        time.sleep(PAUSA_EVENTO)
    else:
        time.sleep(PAUSA)
