# Projeto em Grupo - FIAP
Introdução
1.1 Organização e descrição da telemetria

Interpretar dados referentes a:

Temperatura interna e externa;
Integridade estrutural (0/1);
Níveis de energia (%);
Pressão dos tanques;
Status dos módulos críticos.

1.2 Algoritmo de verificação

Construir um algoritmo (fluxograma/pseudocódigo) capaz de decidir: “PRONTO PARA DECOLAR” ou “DECOLAGEM ABORTADA” com base em faixas seguras predefinidas.

1.3 Script em Python

Implementar a lógica do algoritmo em Python, simulando:

Leitura dos dados;
Execução das verificações;
Resultado final impresso.

1.4 Análise energética

Calcular autonomia inicial considerando:

Capacidade total (kwh); 1000 - 80% - 800 - 500
Carga atual (%);
Consumo estimado na decolagem; - 300kwh
Perdas energéticas. - 

1.5 Análise assistida por IA - implementar uma IA que analise os resultados informados pelo usuario a fim de identificar 
discrepancias nos dados informados.

Solicitar à IA: 

Classificação dos dados;
Identificação de possíveis anomalias;
Sugestões de risco.


1.6 Reflexão crítica

Texto sobre: 

Ética e responsabilidade;
Impacto social da exploração espacial;
Sustentabilidade tecnológica.

Em relação aos entregáveis, é necessário:

Um relatório em PDF contendo todos os dados pedidos na atividade integradora (códigos, análises, algoritmos etc.);
Link do repositório público no GitHub contendo:
Notebook Python (.ipynb);
Arquivo README.md contendo:
Explicação do projeto;
Prints da execução;
Instruções de execução do código.

3 Critérios de avaliação (10 pontos totais)


------------------------------------------------------------------------

ALGORITMO DE VERIFICAÇÃO

Minha sugestão de tabela para a gente validar:

| Parâmetro | Valor Nominal (Ideal) | Margem de Tolerância / Limite | Condição de Aborto |
| :--- | :--- | :--- | :--- |
| Temp. Interna | 22°C | 15°C a 30°C | < 15°C ou > 30°C |
| Temp. Externa | 25°C | -10°C a 45°C | < -10°C ou > 45°C |
| Integridade | 1 (OK) | Apenas 1 | = 0 |
| Energia | 100% | Mínimo 80% | < 80\% |
| Pressão Tanques | 500 psi | 450 psi a 550 psi | < 450 ou > 550 |
| Módulos Críticos | Online | Todos Online | Qualquer módulo Offline |

Por que esses valores?
- Temperatura: Mantém a eletrônica em range industrial padrão.
- Energia: Garante que não falte carga no pico da decolagem.
- Pressão: Define um range de ± 10\% do nominal, que é comum em sistemas hidráulicos/pneumáticos.

ALGORITMO EM PSEUDOCÓDIGO

Uma observação importante sobre o desenho: as verificações **não abortam em
cascata**. Todas as seis são executadas sempre, e cada uma pode desligar a chave
`decolagem_autorizada`. Isso é proposital — em telemetria, o operador precisa ver
todos os problemas de uma vez, e não descobrir o próximo defeito só na tentativa
seguinte.

Início: Verificação de Decolagem

FASE 1 — VERIFICAÇÕES DE SEGURANÇA (todas executam, acumulando erros)
1. Temperatura Interna entre 15°C e 30°C?      Não → registra erro, chave = False
2. Temperatura Externa entre -10°C e 45°C?     Não → registra erro, chave = False
3. Integridade Estrutural igual a 1?           Não → registra erro, chave = False
4. Pressão dos Tanques entre 450 e 550 psi?    Não → registra erro, chave = False
5. Energia ≥ 80\%?                              Não → registra erro, chave = False
   5a. Se passou: reserva pós-decolagem ≥ 10\%? Não → registra erro, chave = False
6. Módulos Críticos todos online?              Não → registra erro, chave = False

FASE 2 — ANÁLISE ASSISTIDA POR IA (cruzamento entre os parâmetros)
7. Grupo 1 — Os dados são fisicamente possíveis?
   - Não → registra DISCREPÂNCIA CRÍTICA e desliga a chave.
8. Grupos 2, 3 e 4 — Existem combinações de risco entre parâmetros válidos?
   - Sim → registra ALERTA (não bloqueia por si só).

FASE 3 — VEREDITO E CLASSIFICAÇÃO
9. Chave desligada?          → HORRÍVEL  → DECOLAGEM ABORTADA
10. Chave ligada com alertas → MÉDIO     → DECOLAGEM COM RESSALVAS
11. Chave ligada sem alertas → ÓTIMO     → SUCESSO ABSOLUTO

Fim: registro do cenário em `cenarios/` (planilha CSV + relatório TXT)

FLUXOGRAMA — VISÃO GERAL

```mermaid
graph LR
    A("Coleta de<br/>Telemetria") --> F1["FASE 1<br/>6 verificações<br/>de segurança"]
    F1 --> F2["FASE 2<br/>Análise assistida<br/>por IA"]
    F2 --> F3{"FASE 3<br/>Veredito"}
    F3 --> RO("ÓTIMO<br/>sucesso absoluto")
    F3 --> RM("MÉDIO<br/>com ressalvas")
    F3 --> RH("HORRÍVEL<br/>abortada")
    RO --> REG("Registro<br/>em cenarios/")
    RM --> REG
    RH --> REG
```

FLUXOGRAMA — FASE 1: VERIFICAÇÕES DE SEGURANÇA

```mermaid
graph TD
    A("INÍCIO<br/>Coleta de Telemetria") --> B["decolagem_autorizada = True"]

    B --> V1{"Temp. Interna<br/>entre 15 e 30 C?"}
    V1 -- Não --> X1["Erro: Temp. Interna<br/>chave = False"]
    V1 -- Sim --> V2{"Temp. Externa<br/>entre -10 e 45 C?"}
    X1 --> V2

    V2 -- Não --> X2["Erro: Temp. Externa<br/>chave = False"]
    V2 -- Sim --> V3{"Integridade<br/>igual a 1?"}
    X2 --> V3

    V3 -- Não --> X3["Erro: Integridade<br/>chave = False"]
    V3 -- Sim --> V4{"Pressão entre<br/>450 e 550 psi?"}
    X3 --> V4

    V4 -- Não --> X4["Erro: Pressão<br/>chave = False"]
    V4 -- Sim --> V5{"Energia<br/>maior ou igual a 80%?"}
    X4 --> V5

    V5 -- Não --> X5["Erro: Energia<br/>chave = False"]
    V5 -- Sim --> V6{"Reserva pós-decolagem<br/>maior ou igual a 10%?"}

    V6 -- Não --> X6["Erro: Reserva<br/>chave = False"]
    V6 -- Sim --> V7{"Módulos críticos<br/>online?"}
    X5 --> V7
    X6 --> V7

    V7 -- Não --> X7["Erro: Módulos<br/>chave = False"]
    V7 -- Sim --> IA("segue para a FASE 2")
    X7 --> IA
```

FLUXOGRAMA — FASES 2 E 3: ANÁLISE POR IA E VEREDITO

```mermaid
graph TD
    IA["ANÁLISE ASSISTIDA POR IA<br/>cruza os parâmetros entre si"]

    IA --> G1{"Grupo 1<br/>Dados fisicamente<br/>possíveis?"}
    G1 -- Não --> CR["Registra CRÍTICOS<br/>chave = False"]
    G1 -- Sim --> G2{"Grupos 2, 3 e 4<br/>Combinações<br/>de risco?"}
    CR --> G2

    G2 -- Sim --> AL["Registra ALERTAS<br/>não bloqueia sozinho"]
    G2 -- Não --> D1{"Chave<br/>autorizada?"}
    AL --> D1

    D1 -- Não --> RH("HORRÍVEL<br/>DECOLAGEM ABORTADA")
    D1 -- Sim --> D2{"Existem<br/>alertas?"}

    D2 -- Sim --> RM("MÉDIO<br/>DECOLAGEM COM RESSALVAS")
    D2 -- Não --> RO("ÓTIMO<br/>SUCESSO ABSOLUTO")

    RH --> REG["Grava em cenarios/<br/>planilha CSV + relatório TXT"]
    RM --> REG
    RO --> REG
    REG --> FIM("FIM")
```

CENÁRIOS POSSÍVEIS

O ponto central do novo fluxo é que **autorizar não é o mesmo que estar tudo
bem**. A camada de IA separa o "decolou porque nada impediu" do "decolou sem
nenhuma ressalva", que o veredito binário anterior não distinguia.

| Classificação | Chave | Alertas | Significado | Exemplo real coletado |
| :--- | :--- | :--- | :--- | :--- |
| **ÓTIMO** | Autorizada | Nenhum | Sucesso absoluto: nenhuma discrepância no cruzamento dos dados | Cenário 09 — noite fresca, bateria a 98% |
| **MÉDIO** | Autorizada | 1 ou mais | Decolagem viável, mas consumindo margem de segurança. Recomenda revisão humana | Cenário 06 — cabine a 29°C, externa a -8°C, tanque a 535 psi (3 alertas) |
| **HORRÍVEL** | Abortada | — | Falha em verificação de segurança **ou** telemetria não confiável | Cenário 08 — energia lida como 105% e integridade como 3 |

O caso mais instrutivo é o **cenário 08**: as seis verificações clássicas
aprovaram todos os parâmetros (105 não é menor que 80; 3 não é menor que 1), e
foi a Fase 2 que barrou a decolagem ao perceber que os valores eram fisicamente
impossíveis. É exatamente a lacuna que motivou incluir a IA no fluxo.

Como funciona
<pre> ```mermaid graph TD A[Início] --> B{Energia ≥ 80%?} B -- Não --> C[ABORTAR] B -- Sim --> D[DECOLAR] ``` </pre>
Três peças e só:

Peça	Sintaxe	Vira
Direção	graph TD / graph LR	de cima p/ baixo · da esquerda p/ direita
Caixa retangular	A[Texto]	processo / ação
Losango	B{Texto?}	decisão
Balão	C(Texto)	início / fim
Seta	A --> B	fluxo
Seta com rótulo	B -- Não --> C	saída de decisão
O A, B, C são só apelidos internos — não aparecem no desenho. Servem para você ligar as caixas. Por isso C --> E mais adiante reaproveita a caixa C já declarada, sem repetir o texto.

Onde isso aparece renderizado
GitHub — renderiza nativo. Como o entregável é repositório público, o fluxograma vai aparecer desenhado direto no .md. ✅
Obsidian — renderiza nativo.
VS Code — o preview embutido não renderiza; precisa da extensão Markdown Preview Mermaid Support. É bem provável que seja por isso que você achou que não estava funcionando.

