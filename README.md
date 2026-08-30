# Projeto AURORA — Sistema de Verificação de Decolagem

Atividade integradora (PBL) — FIAP

Sistema de análise de telemetria que decide se uma nave está apta a decolar,
combinando verificações de faixas seguras, cálculo de autonomia energética e uma
camada de análise que cruza os parâmetros em busca de discrepâncias.

---

## Sobre o projeto

O sistema recebe seis parâmetros de telemetria e emite um veredito. A parte
interessante não é a verificação em si — é o que ela **não** consegue ver sozinha.

Durante os testes, informamos energia de 105% e integridade estrutural igual a 3.
As seis verificações de segurança aprovaram tudo: 105 não é menor que 80, e 3 não
é menor que 1. O sistema teria autorizado a decolagem de uma nave com sensores
claramente corrompidos.

Foi isso que motivou a terceira camada do projeto. Cada regra estava correta
isoladamente; o conjunto delas, ainda assim, falhava.

## Como funciona

O programa trabalha em três fases:

### Fase 1 — Verificações de segurança

Seis parâmetros comparados com faixas predefinidas:

| Parâmetro | Faixa segura | Condição de aborto |
| :--- | :--- | :--- |
| Temperatura interna | 15 °C a 30 °C | fora da faixa |
| Temperatura externa | −10 °C a 45 °C | fora da faixa |
| Integridade estrutural | apenas 1 | diferente de 1 |
| Pressão dos tanques | 450 a 550 psi | fora da faixa |
| Nível de energia | mínimo de 80 % | abaixo de 80 % |
| Módulos críticos | todos online | qualquer um offline |

As verificações **não abortam em cascata**: todas são executadas, e cada uma pode
desligar a chave de autorização. O operador precisa enxergar todos os problemas de
uma vez, e não descobrir o próximo defeito só na tentativa seguinte.

### Fase 2 — Análise assistida por IA

Um sistema especialista cruza os parâmetros entre si, em quatro grupos de regras:

| Grupo | Pergunta que responde | Exemplo |
| :--- | :--- | :--- |
| 1 | Os dados são fisicamente possíveis? | energia acima de 100 % |
| 2 | Os dados são coerentes entre si? | bateria a 82 % com −8 °C lá fora |
| 3 | Algum parâmetro opera sem margem? | pressão a 548 psi (limite: 550) |
| 4 | A telemetria parece real? | todos os canais no valor nominal exato |

A escolha por regras locais, em vez de uma chamada a um modelo de linguagem
externo, foi deliberada: o sistema precisa funcionar sem internet, sem chave de API
e de forma determinística — a mesma entrada produz sempre o mesmo veredito. Em um
sistema que decide sobre segurança, reprodutibilidade é requisito.

### Fase 3 — Veredito

| Classificação | Significado |
| :--- | :--- |
| **ÓTIMO** | Autorizada, nenhuma discrepância encontrada |
| **MÉDIO** | Autorizada, mas consumindo margem de segurança — pede revisão humana |
| **HORRÍVEL** | Abortada por falha de segurança ou telemetria não confiável |

A faixa intermediária existe por decisão de projeto: um veredito binário empurra a
decisão inteiramente para o algoritmo, enquanto um resultado que diz "liberado, mas
observe estes três pontos" devolve a decisão a quem tem responsabilidade sobre ela.

---

## Instruções de execução

### Pré-requisitos

**Python 3.6 ou superior** é o único requisito obrigatório.

**Não é necessário instalar nenhuma dependência.** O programa usa apenas a
biblioteca padrão do Python (`csv`, `os`, `datetime`, `subprocess`). Não há
`requirements.txt` porque não há o que instalar.

Para verificar se o Python já está instalado, abra o terminal e digite:

```bash
python --version
```

Se aparecer algo como `Python 3.12.10`, está tudo certo. Se o comando não for
reconhecido, baixe o Python em [python.org/downloads](https://www.python.org/downloads/).

> **Windows:** durante a instalação, marque a opção **"Add Python to PATH"** na
> primeira tela. Sem isso, o comando `python` não funciona no terminal.
>
> Em algumas instalações o comando é `python3` em vez de `python`. Se um não
> funcionar, tente o outro.

### 1. Obter o projeto

Com Git instalado:

```bash
git clone https://github.com/Douglasgbm/Aurora_pbl.git
cd Aurora_pbl
```

Sem Git: baixe o ZIP pelo botão verde **Code > Download ZIP** na página do
repositório, extraia a pasta e abra o terminal dentro dela.

### 2. Executar o programa

```bash
python scripts/main.py
```

O programa solicita os seis parâmetros pelo teclado, um de cada vez:

| Pergunta | O que digitar | Exemplo |
| :--- | :--- | :--- |
| Temperatura interna | número em °C | `23` |
| Temperatura externa | número em °C | `20` |
| Integridade | `1` para OK, `0` para falha | `1` |
| Pressão dos tanques | número em psi | `495` |
| Porcentagem de energia | número de 0 a 100 | `92` |
| Módulos online | `S` para sim, `N` para não | `S` |

Use **ponto** para decimais (`22.5`), não vírgula — é a notação que o Python
entende.

Cada execução grava automaticamente dois arquivos na pasta `cenarios/`:

- `registro_execucoes.csv` — uma linha por execução, acumulativo (abre no Excel)
- `cenario_XX_CLASSE.txt` — o relatório completo daquela execução

A pasta é criada sozinha na primeira execução, e a numeração continua de onde
parou.

### 3. Gerar os cenários de teste (opcional)

```bash
python scripts/cenarios.py
```

Executa os cenários pré-definidos que ainda faltam para completar a meta de 10,
sem precisar digitar nada. Rodar duas vezes não duplica registros — o script conta
o que já existe e para quando a meta é atingida.

Para gerar tudo de novo do zero, apague os arquivos da pasta `cenarios/` antes.

### 4. Abrir o notebook

O notebook reúne os itens 1.1 a 1.6 e executa de ponta a ponta. Diferente dos
scripts, ele **exige a instalação do Jupyter**:

```bash
pip install jupyter
jupyter notebook notebook/aurora_pbl.ipynb
```

Depois de abrir no navegador, use o menu **Run > Run All Cells** para executar
tudo em ordem.

Alternativa sem instalar nada: o GitHub renderiza o notebook automaticamente ao
clicar no arquivo, e o VS Code o abre com a extensão *Jupyter*.

**Gráfico opcional.** A célula final gera um gráfico de barras se a biblioteca
`matplotlib` estiver instalada:

```bash
pip install matplotlib
```

Sem ela, nada quebra — os mesmos dados aparecem em formato de tabela nas células
anteriores.

### Problemas comuns

| Sintoma | Causa provável | Solução |
| :--- | :--- | :--- |
| `python: command not found` | Python não instalado ou fora do PATH | Reinstale marcando "Add Python to PATH", ou tente `python3` |
| `ValueError: could not convert string to float` | Foi digitado texto ou vírgula onde se espera número | Use apenas números, com ponto decimal (`22.5`) |
| Acentos aparecem como `?` ou `Ã§` no terminal | Codificação do console do Windows | Rode `chcp 65001` antes, ou use o Windows Terminal |
| `can't open file 'scripts/main.py'` | Terminal está na pasta errada | Entre na pasta raiz do projeto antes de executar |

---

## Prints da execução

### Cenário MÉDIO — decolagem autorizada com ressalvas

Entrada: `29` `-8` `1` `535` `93` `S`

```
Temperatura Interna: OK
Temperatura Externa: OK
Integridade: OK
Pressão dos Tanques: OK
Energia: OK
  Disponivel na bateria : 930.0 kWh (93%)
  Consumo + perdas      : 324.0 kWh
  Sobra apos decolagem  : 606.0 kWh (60.6%)
Módulos: OK

==============================================================
ANÁLISE ASSISTIDA POR IA - DIAGNÓSTICO DE DISCREPÂNCIAS
==============================================================

ALERTAS (dados válidos, mas em combinação de risco):
  [!] Pressão de 535 psi já alta com temperatura interna de 29C. Pela lei dos
      gases a pressão sobe com o aquecimento, podendo ultrapassar 550 psi
      durante a subida.
  [!] Diferencial térmico de 37C entre interna e externa. Sugere falha de
      isolamento térmico ou sensor travado.
  [!] Temperatura interna de 29C próxima do teto de 30C, e o calor dos motores
      ainda vai somar durante a decolagem.

>> PARECER: DECOLAGEM VIÁVEL, COM RESSALVAS.
   3 ponto(s) de atenção acima. Recomenda-se revisão humana.
==============================================================

Decolagem Autorizada!

Cenario registrado como cenario_06_MEDIO.txt (classificacao: MEDIO)
```

### Cenário HORRÍVEL — telemetria corrompida

Entrada: `22` `25` `3` `500` `105` `S`

```
Integridade: OK                      <- a verificação tradicional aprovou
Energia: OK                          <- a verificação tradicional aprovou

DISCREPÂNCIAS CRÍTICAS (telemetria não confiável):
  [X] Energia de 105.0% está fora do domínio físico (0 a 100%).
      Sensor descalibrado ou erro de digitação.
  [X] Integridade informada como 3. O indicador é binário (0 ou 1);
      valor fora disso indica corrupção de dados.

>> PARECER: DADOS INCONSISTENTES.
   A decolagem não pode ser avaliada com telemetria corrompida.

Decolagem Não Autorizada!            <- a análise barrou
```

<!-- ESPAÇO PARA OS PRINTS EM IMAGEM
Para adicionar capturas de tela do terminal:
1. Salve as imagens na pasta docs/ (crie a pasta se necessário)
2. Referencie assim:  ![Execução do cenário ótimo](docs/print-otimo.png)
-->

---

## Cenários coletados

Foram registradas 10 execuções, cobrindo as três classificações:

| # | Classificação | T.int | T.ext | Integr. | Pressão | Energia | Críticos | Alertas |
| :-- | :--- | --: | --: | --: | --: | --: | --: | --: |
| 01 | HORRÍVEL | 10 | 50 | 0 | 350 | 70 | 0 | 1 |
| 02 | MÉDIO | 25 | 30 | 1 | 550 | 80 | 0 | 2 |
| 03 | ÓTIMO | 25 | 30 | 1 | 480 | 100 | 0 | 0 |
| 04 | ÓTIMO | 23 | 20 | 1 | 495 | 92 | 0 | 0 |
| 05 | MÉDIO | 21 | −9 | 1 | 500 | 85 | 0 | 1 |
| 06 | MÉDIO | 29 | −8 | 1 | 535 | 93 | 0 | 3 |
| 07 | HORRÍVEL | 22 | 25 | 0 | 500 | 90 | 0 | 0 |
| 08 | HORRÍVEL | 22 | 25 | 3 | 500 | 105 | **2** | 0 |
| 09 | ÓTIMO | 20 | 5 | 1 | 470 | 98 | 0 | 0 |
| 10 | HORRÍVEL | 24 | 28 | 1 | 505 | 55 | 0 | 0 |

Dois cenários merecem destaque:

O **08** é o caso em que a análise barrou o que as verificações aprovaram. Note a
energia disponível calculada para ele: **1050 kWh em uma bateria de 1000 kWh** — a
prova numérica de que o dado era impossível.

O **09** cumpre o papel oposto: com temperatura externa de 5 °C, ele *não* dispara
o alerta de frio. Isso demonstra que a regra discrimina de fato, em vez de alertar
sobre qualquer coisa.

---

## Estrutura do repositório

```
├── scripts/
│   ├── main.py               programa principal (interativo)
│   └── cenarios.py           gerador automático de cenários
├── cenarios/                 10 cenários coletados (CSV + relatórios TXT)
├── notebook/
│   └── aurora_pbl.ipynb      notebook com os itens 1.1 a 1.6
├── ROADMAP.MD                especificação, faixas seguras e fluxogramas
├── analise_assistida_ia.md   classificação de dados, anomalias e riscos
└── reflexao_critica.md       ética, impacto social e sustentabilidade
```

## Documentação

| Documento | Conteúdo |
| :--- | :--- |
| [ROADMAP.MD](ROADMAP.MD) | Faixas seguras, pseudocódigo e fluxogramas |
| [analise_assistida_ia.md](analise_assistida_ia.md) | Classificação dos dados, anomalias e riscos |
| [reflexao_critica.md](reflexao_critica.md) | Ética, impacto social e sustentabilidade |

Os fluxogramas estão em formato Mermaid e são renderizados automaticamente pelo
GitHub ao abrir o `ROADMAP.MD`.

---

## Parâmetros do modelo energético

| Constante | Valor | Origem |
| :--- | :--- | :--- |
| Capacidade da bateria | 1000 kWh | Definida na especificação |
| Consumo na decolagem | 300 kWh | Definido na especificação |
| Perdas energéticas | 8 % | Estimativa do grupo (conversão + aquecimento) |
| Reserva mínima de pouso | 10 % | Decisão do grupo |

Vale registrar: com 300 kWh de consumo e 8 % de perdas, a energia mínima
*matemática* para decolar seria de 32,4 %. O limite de 80 % não vem do consumo da
decolagem — ele existe para garantir autonomia **depois** dela.
