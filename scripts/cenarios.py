# =====================================================================
# GERADOR DE CENÁRIOS DE TESTE - PROJETO AURORA
# =====================================================================
# ESTE SCRIPT NÃO REFAZ A LÓGICA DE VERIFICAÇÃO. ELE EXECUTA O PRÓPRIO
# main.py E ENTREGA AS RESPOSTAS AUTOMATICAMENTE, COMO SE ALGUÉM
# ESTIVESSE DIGITANDO. ASSIM EXISTE UMA ÚNICA FONTE DA VERDADE: SE AS
# REGRAS MUDAREM NO main.py, OS CENÁRIOS ACOMPANHAM SOZINHOS.
#
# O main.py GRAVA CADA EXECUÇÃO EM cenarios/ E, QUANDO A DECOLAGEM É
# AUTORIZADA, SEGUE PARA A MISSÃO E GRAVA TAMBÉM EM missoes/.
#
# COMO USAR:  python scripts/cenarios.py
# PARA GERAR TUDO DE NOVO: apague os arquivos de cenarios/ e missoes/ antes.
# =====================================================================

import os
import subprocess   # PERMITE EXECUTAR OUTRO PROGRAMA A PARTIR DESTE
import sys          # DÁ ACESSO AO INTERPRETADOR PYTHON EM USO

TOTAL_DE_CENARIOS = 10      # META DEFINIDA PELO GRUPO
NOME_CAPITAO = "Douglas"    # A PRIMEIRA PERGUNTA DO main.py É O NOME DO CAPITÃO

# A ORDEM DAS RESPOSTAS SEGUE EXATAMENTE A ORDEM DAS PERGUNTAS DO main.py:
# temperatura interna, temperatura externa, integridade, pressão, energia, módulos.
# (O NOME DO CAPITÃO É ACRESCENTADO NA FRENTE, AUTOMATICAMENTE.)
# A LISTA ESTÁ NA MESMA ORDEM DA TABELA "Cenários coletados" DO README.
CENARIOS = [
    {
        "titulo": "Tudo fora da faixa",
        "esperado": "HORRIVEL",
        "respostas": ["10", "50", "0", "350", "70", "S"],
    },
    {
        "titulo": "Pressao e energia exatamente no limite",
        "esperado": "MEDIO",
        "respostas": ["25", "30", "1", "550", "80", "S"],
    },
    {
        "titulo": "Bateria cheia em dia quente",
        "esperado": "OTIMO",
        "respostas": ["25", "30", "1", "480", "100", "S"],
    },
    {
        "titulo": "Operacao padrao em dia ameno",
        "esperado": "OTIMO",
        "respostas": ["23", "20", "1", "495", "92", "S"],
    },
    {
        "titulo": "Lancamento em clima frio com bateria parcial",
        "esperado": "MEDIO",
        "respostas": ["21", "-9", "1", "500", "85", "S"],
    },
    {
        "titulo": "Cabine quente, tanque pressurizado e frio externo",
        "esperado": "MEDIO",
        "respostas": ["29", "-8", "1", "535", "93", "S"],
    },
    {
        "titulo": "Falha estrutural detectada",
        "esperado": "HORRIVEL",
        "respostas": ["22", "25", "0", "500", "90", "S"],
    },
    {
        "titulo": "Telemetria corrompida (energia 105% e integridade 3)",
        "esperado": "HORRIVEL",
        "respostas": ["22", "25", "3", "500", "105", "S"],
    },
    {
        "titulo": "Noite fresca com bateria cheia",
        "esperado": "OTIMO",
        "respostas": ["20", "5", "1", "470", "98", "S"],
    },
    {
        "titulo": "Energia insuficiente para o perfil de missao",
        "esperado": "HORRIVEL",
        "respostas": ["24", "28", "1", "505", "55", "S"],
    },
]

# --- LOCALIZA OS ARQUIVOS DO PROJETO ---
pasta_scripts = os.path.dirname(os.path.abspath(__file__))
pasta_projeto = os.path.normpath(os.path.join(pasta_scripts, ".."))
caminho_main = os.path.join(pasta_scripts, "main.py")
arquivo_csv = os.path.join(pasta_projeto, "cenarios", "registro_execucoes.csv")

# --- DESCOBRE QUANTOS CENÁRIOS JÁ FORAM REGISTRADOS ---
# ISSO EVITA DUPLICAR OS CENÁRIOS CASO O SCRIPT SEJA EXECUTADO DUAS VEZES.
ja_registrados = 0
if os.path.exists(arquivo_csv):
    arquivo = open(arquivo_csv, "r", encoding="utf-8-sig")
    ja_registrados = len(arquivo.readlines()) - 1  # DESCONTA A LINHA DO CABEÇALHO
    arquivo.close()

faltam = TOTAL_DE_CENARIOS - ja_registrados

print("=" * 62)
print("GERADOR DE CENARIOS - PROJETO AURORA")
print("=" * 62)
print("Cenarios ja registrados : {}".format(ja_registrados))
print("Meta do grupo           : {}".format(TOTAL_DE_CENARIOS))
print("Serao gerados agora     : {}".format(max(faltam, 0)))
print("=" * 62)
print("")

if faltam <= 0:
    print("Nada a fazer: a meta de {} cenarios ja foi atingida.".format(TOTAL_DE_CENARIOS))
    print("Para gerar novamente, apague os arquivos das pastas cenarios/ e missoes/.")
    sys.exit()  # ENCERRA O PROGRAMA AQUI

# GARANTE QUE OS ACENTOS SEJAM LIDOS CORRETAMENTE NO WINDOWS
ambiente = os.environ.copy()
ambiente["PYTHONIOENCODING"] = "utf-8"

# --- EXECUTA OS CENÁRIOS QUE FALTAM ---
# A FATIA [ja_registrados:] PULA OS QUE JÁ EXISTEM E CONTINUA DE ONDE PAROU.
for cenario in CENARIOS[ja_registrados:]:
    # JUNTA AS RESPOSTAS EM UM ÚNICO TEXTO, UMA POR LINHA (COMO SE FOSSEM DIGITADAS)
    entrada = "\n".join([NOME_CAPITAO] + cenario["respostas"]) + "\n"

    resultado = subprocess.run(
        [sys.executable, caminho_main],
        input=entrada,
        capture_output=True,   # CAPTURA O QUE O PROGRAMA IMPRIMIU
        text=True,
        encoding="utf-8",
        env=ambiente,
    )

    # PROCURA NA SAÍDA AS LINHAS QUE CONFIRMAM OS REGISTROS
    confirmacao = ""
    missao = ""
    for linha in resultado.stdout.splitlines():
        if linha.startswith("Cenario registrado"):
            confirmacao = linha
        if linha.startswith("Missao registrada"):
            missao = linha

    print("-> " + cenario["titulo"])
    print("   dados     : " + " | ".join(cenario["respostas"]))
    if confirmacao:
        print("   resultado : " + confirmacao.replace("Cenario registrado como ", ""))
        if missao:
            print("   missao    : " + missao.replace("Missao registrada como ", ""))
    else:
        print("   ERRO ao executar este cenario:")
        print(resultado.stderr.strip())
    print("")

print("=" * 62)
print("Concluido. Confira as pastas cenarios/ e missoes/.")
print("=" * 62)
