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

Todo o projeto é **um único programa**, `scripts/main.py`, escrito como um
roteiro lido de cima para baixo: as constantes ficam no topo, e cada etapa vem
em sequência, sem funções. A verificação de decolagem trabalha em três fases;
se a decolagem for autorizada, o mesmo programa segue para a simulação da
missão Terra → Marte (descrita mais abaixo).

### Fase 0 — Análise energética

Antes das verificações, o programa converte a carga digitada em energia e segue
os termos do material da disciplina, nesta ordem:

| Termo | Cálculo | Exemplo (carga 80 %) |
| :--- | :--- | --: |
| Energia disponível (kWh) | capacidade total × carga atual | 800 |
| Energia perdida (kWh) | energia disponível × perdas (8 %) | 64 |
| Energia útil (kWh) | energia disponível − energia perdida | 736 |
| Energia restante (kWh) | energia útil − consumo da decolagem (300 kWh) | 436 |

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
biblioteca padrão do Python (`csv`, `os`, `datetime`). Não há
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

O programa começa pedindo o nome do capitão (só para o registro) e depois
solicita os seis parâmetros pelo teclado, um de cada vez:

| Pergunta | O que digitar | Exemplo |
| :--- | :--- | :--- |
| Identifique-se, capitão | seu nome | `Douglas` |
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
parou. Se a decolagem for autorizada, o programa continua direto para a missão
Terra → Marte (item 4 abaixo); se for abortada, ele encerra com a mensagem
`MISSAO CANCELADA`.

Para reproduzir os 10 cenários da tabela mais abaixo, basta digitar as
entradas de cada linha. Para recomeçar a numeração do zero, apague os arquivos
da pasta `cenarios/` antes.

### 3. Abrir o notebook

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

### 4. A missão Terra → Marte

Não há comando separado: a missão é a continuação do `main.py` quando a
decolagem é autorizada. A IA escolhe a rota pela carga da bateria (90 % ou mais
vai pela rota rápida; abaixo disso, pela econômica) e simula a missão hora a
hora, em quatro fases: saída da atmosfera, cruzeiro interplanetário, captura
orbital em Marte e pouso. A tabela de horas vai rolando na tela.

A cada hora a IA calcula o saldo de energia (recarga solar menos o consumo dos
sistemas ligados), decide o estado da nave e age:

| Estado | Quando | O que a IA faz |
| :--- | :--- | :--- |
| 🟢 Verde | bateria alta | tudo ligado |
| 🟡 Amarelo | bateria média, ou margem de retorno ameaçada | desliga a prioridade 3, comunicação em modo econômico |
| 🔴 Vermelho | bateria baixa, tempestade, ou margem crítica | só o essencial (prioridade 1) |

Cada missão grava dois arquivos na pasta `missoes/`:

- `registro_missoes.csv` — uma linha por missão (rota, horas, bateria final, horas em cada estado)
- `missao_XX_STATUS.txt` — a "caixa preta": todas as horas e todas as decisões da IA

A tela mostra menos linhas que o arquivo: em Amarelo a telemetria sai a cada 2 h,
em Vermelho a cada 4 h. O arquivo guarda tudo.

A especificação do modelo (custos, prioridades, recarga, fases) está em
[upgrade.md](upgrade.md). A seção 6 desse documento lista as decisões tomadas
onde a especificação não dava número.

O arquivo `scripts/painel.py` é um painel de voo ao vivo (tela estilo console
de foguete, redesenhada a cada hora). Ele está no repositório como experimento e
**ainda não é usado** pelo `main.py`.

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
==============================================================
TELEMETRIA INFORMADA
==============================================================
  Temperatura interna : 29.0 C
  Temperatura externa : -8.0 C
  Integridade         : 1 (OK)
  Pressao dos tanques : 535.0 psi
  Energia             : 93.0 %
  Modulos online      : SIM

==============================================================
ANALISE ENERGETICA
==============================================================
  Capacidade total            : 1000.0 kWh
  Carga atual                 : 93.0 %
  Energia disponivel          : 930.0 kWh
  Perdas energeticas          : 8 %
  Energia perdida             : 74.4 kWh
  Energia util                : 855.6 kWh
  Consumo na decolagem        : 300.0 kWh
  Energia apos a decolagem    : 555.6 kWh (55.6% da bateria)
  Resultado: energia suficiente para a decolagem.

==============================================================
VERIFICACOES DE SEGURANCA
==============================================================
Temperatura Interna: OK
Temperatura Externa: OK
Integridade: OK
Pressão dos Tanques: OK
Energia: OK
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
  Energia disponivel          : 1050.0 kWh   <- 1050 kWh numa bateria de 1000 kWh
  ...
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

MISSAO CANCELADA: a verificacao de decolagem nao autorizou o lancamento.
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
│   ├── main.py               O PROGRAMA: verificação de decolagem + missão Terra → Marte
│   └── painel.py             painel de voo ao vivo (experimento, ainda não usado pelo main.py)
├── cenarios/                 10 cenários coletados (CSV + relatórios TXT)
├── missoes/                  missões simuladas (CSV + caixa preta TXT); criada na 1ª execução
├── notebook/
│   └── aurora_pbl.ipynb      notebook com os itens 1.1 a 1.6
├── ROADMAP.MD                especificação, faixas seguras e fluxogramas
├── upgrade.md                especificação da simulação de missão
├── analise_assistida_ia.md   classificação de dados, anomalias e riscos
└── reflexao_critica.md       ética, impacto social e sustentabilidade
```

## Documentação

| Documento | Conteúdo |
| :--- | :--- |
| [ROADMAP.MD](ROADMAP.MD) | Faixas seguras, pseudocódigo e fluxogramas |
| [upgrade.md](upgrade.md) | Simulação de missão: prioridades, estados, custos, recarga, fases e rota |
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
| Perdas energéticas | 8 % da energia armazenada | Estimativa do grupo (conversão + aquecimento) |
| Reserva mínima de pouso | 10 % | Decisão do grupo |

Vale registrar: com 300 kWh de consumo e 8 % de perdas, a energia mínima
*matemática* para decolar seria de cerca de 32,6 % de carga (326 kWh disponíveis,
300 kWh úteis). O limite de 80 % não vem do consumo da decolagem — ele existe
para garantir autonomia **depois** dela.
