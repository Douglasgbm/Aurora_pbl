# Esqueleto da IA — Projeto Aurora

> Anotações de 08/09/2026, 15:37. Ideias para o upgrade do código.

---

## 1. Conceito atual

A "IA" opera como um **Sistema Especialista** (simulação baseada em regras). O fluxo é:

1. Input de dados (humano / sensores).
2. Processamento via tabela de parâmetros.
3. Tomada de decisão autônoma para liberação de decolagem.

---

## 2. Nova implementação: gestão energética e otimização

A IA deve evoluir de uma **análise pontual** para um **monitoramento constante** da carga
energética, com foco em:

- **Análise constante:** loop de monitoramento da carga da nave.
- **Otimização de energia:** ajuste dinâmico do consumo com base na carga disponível.
- **Adaptação de consumo:** gestão de prioridades de sistemas.

### 2.1 Hierarquia de prioridades

| Prioridade | Classe       | Sistemas                                   |
| :--------: | :----------- | :----------------------------------------- |
| **1**      | Essenciais   | Telemetria, Controle de Voo, Comunicação   |
| **2**      | Importantes  | Sensores secundários, Câmeras              |
| **3**      | Secundários  | Sistemas não críticos                      |

### 2.2 Estados de saúde da nave (lógica fuzzy / especialista)

| Estado          | Carga | Comportamento                                                                                   |
| :-------------- | :---: | :---------------------------------------------------------------------------------------------- |
| 🟢 **Verde**    | Alta  | Performance máxima. Todos os sistemas ativos.                                                   |
| 🟡 **Amarelo**  | Média | **Modo de Otimização.** Reduz a frequência de telemetria e desliga os sistemas de Prioridade 3. |
| 🔴 **Vermelho** | Baixa | **Modo de Sobrevivência.** Desliga Prioridade 2 e 3, mantendo só o essencial para a missão.     |

---

## 3. Simulação de missão e gestão energética dinâmica

### 3.1 Fluxo de consumo energético

A IA deixa de ser um validador de input único e passa a ser um **monitor de missão em
tempo real**. O consumo se divide em:

- **Gastos pontuais (eventos):** ex. decolagem, um consumo massivo único.
- **Gastos constantes (sustentação):** ex. suporte à vida, navegação, comunicação. Consumo
  por hora de voo.

### 3.2 Viabilidade e retorno (ponto de não retorno)

A IA deve calcular a margem de segurança para o retorno à Terra.

- **Reserva crítica:** 30% de energia mínima para a manobra de volta.
- **Cálculo de margem:**

  ```
  Margem de Segurança = Energia Atual − (Consumo Médio × Tempo de Retorno)
  ```

- **Ação autônoma:** se a margem de segurança for ameaçada, a IA inicia o desligamento
  escalonado de sistemas (Prioridade 3 → Prioridade 2) para preservar a reserva de 30%.

### 3.3 Dinâmica de recarga (opcional / painéis solares)

Recuperação de energia via painéis solares:

- **Recarga ativa:** ganho de X% por hora enquanto houver exposição solar.
- **Interrupção:** perda de recarga em zonas de sombra (ex. órbita de planetas), forçando
  a IA a adaptar o consumo instantaneamente.

---

## 4. Tabela de custos energéticos

### 4.1 Gastos pontuais (eventos únicos)

São os "sustos" na bateria. A IA precisa prever esses gastos **antes** de autorizar a manobra.

| Evento                              | Custo             | Observação                                  |
| :---------------------------------- | :---------------: | :------------------------------------------ |
| Decolagem / Ignição                 | **−20%**          | Gasto massivo para sair da gravidade.       |
| Manobra de órbita / Ajuste de rota  | **−5%** por manobra |                                           |
| Pouso / Retropropulsão              | **−10%**          | Para não virar um meteoro no planeta.       |

### 4.2 Gastos constantes (por hora de voo)

Aqui é onde a IA trabalha no monitoramento constante.

| Sistema                                          | Consumo     | Prioridade | Pode desligar?                       |
| :----------------------------------------------- | :---------: | :--------: | :----------------------------------- |
| Suporte à vida (O2, temperatura, pressão)        | 0,5 % / h   | 1          | **Não.**                             |
| Navegação e IA (cálculo de rota, telemetria)     | 0,3 % / h   | 1          | **Não.** Essencial.                  |
| Comunicação de longo alcance (rádio com a Terra) | 0,2 % / h   | 2          | Pode ser reduzida a "modo econômico". |
| Sensores científicos e câmeras                   | 0,2 % / h   | 3          | Sim. Primeira coisa a ser desligada. |
| Iluminação e sistemas internos                   | 0,1 % / h   | 3          | Sim.                                 |

### 4.3 Dinâmica de recarga solar

A recarga não é constante. Ela depende do ambiente.

| Condição                                     | Recarga     |
| :------------------------------------------- | :---------: |
| Exposição total (espaço aberto)              | **+0,8 % / h** |
| Exposição parcial (sombra de planeta / nuvens) | **+0,2 % / h** |
| Eclipse / sombra total                       | **0 % / h**    |

### 4.4 Como a IA opera com esses dados

A cada "hora" de simulação, a IA calcula:

```
Saldo = Recarga Solar − Soma dos Sistemas Ativos
```

- **Saldo positivo:** a bateria sobe. A IA pode liberar o uso de sistemas de Prioridade 3
  (câmeras, luzes).
- **Saldo negativo:** a bateria desce. A IA começa a monitorar a margem de retorno (os 30%).
- **Margem de retorno ameaçada:** a IA corta Prioridade 3 → Prioridade 2 → e avisa que a
  missão está em risco.

---

## 5. Mapa de trajeto: Terra → Marte

O trajeto Terra → Marte não é uma linha reta. Ele tem fases e riscos. Proposta de roteiro
da missão, dividida por etapas, com os eventos que a IA terá que gerenciar.

### 5.1 Fases da missão

#### Fase 1 — Saída da atmosfera e órbita terrestre

- **Evento:** Decolagem (gasto massivo de energia).
- **Ação da IA:** Monitorar a estabilidade da subida.
- **Energia:** Painéis solares ainda fechados, para evitar danos com o atrito da atmosfera.

#### Fase 2 — Cruzeiro interplanetário (o "vazio")

- **Evento:** Abertura dos painéis solares.
- **Ação da IA:** Assim que sair da atmosfera, autoriza a abertura dos painéis para começar
  a recarga.
- **Risco:** Tempestades solares. A IA pode ter que recolher os painéis ou entrar em
  **"Modo de Proteção"** (desligando sistemas não essenciais para evitar que a radiação
  queime os circuitos).

#### Fase 3 — Aproximação e captura orbital (Marte)

- **Evento:** Frenagem (gasto de energia para não passar direto por Marte).
- **Ação da IA:** Calcular se a bateria aguenta a frenagem e ainda mantém a reserva de 30%
  para a volta.
- **Risco:** Sombra de Marte. Ao entrar na órbita, a nave pode entrar em eclipses
  frequentes, cortando a recarga solar.

#### Fase 4 — Pouso e exploração (superfície)

- **Evento:** Pouso (gasto massivo).
- **Ação da IA:** Gerenciar a energia limitada enquanto a nave está no chão.
- **Risco:** Tempestades de poeira marcianas. A poeira cobre os painéis → a recarga cai
  drasticamente → a IA precisa desligar tudo para sobreviver até a poeira baixar.

### 5.2 A "melhor rota" (lógica de navegação)

A IA pode sugerir duas rotas:

1. **Rota Rápida:** menos tempo de viagem, mas exige mais manobras de correção (gasta mais
   energia).
2. **Rota Econômica (Hohmann Transfer):** mais lenta, mas usa a gravidade a favor e gasta o
   mínimo de energia possível.

A IA decide a rota com base na bateria:

| Bateria   | Rota       |
| :-------: | :--------- |
| > 90%     | Rápida     |
| < 90%     | Econômica  |

### 5.3 Como isso entra no código Python?

Criar uma lista de **checkpoints**. A cada checkpoint, a IA dispara um evento.

```
# PSEUDOCÓDIGO — rascunho da ideia, não é o código final

checkpoints = ["Atmosfera", "Espaço Profundo", "Órbita de Marte", "Superfície"]

if local == "Espaço Profundo":
    IA: "Saindo da atmosfera. Autorizando abertura de painéis solares."
    → Ativa a função de recarga.

if local == "Órbita de Marte":
    IA: "Iniciando manobra de frenagem."
    → Subtrai o gasto pontual de frenagem e verifica se a reserva de 30%
      para a volta ainda está segura.

if local == "Superfície":
    IA: "Pouso concluído. Monitorando acúmulo de poeira nos painéis."
    → Reduz a eficiência da recarga solar.
```

---

## 6. Como foi implementado (09/09/2026)

Tudo acima virou código em [scripts/missao.py](scripts/missao.py). O `main.py` foi
reorganizado em funções, sem mudar o comportamento (os 10 cenários foram regerados e
conferidos linha a linha), para poder ser importado como a "fase 0" da missão.

### 6.1 Mapa: seção do documento → código

| Seção     | O que é                                      | Onde está no `missao.py`                                        |
| :-------: | :------------------------------------------- | :-------------------------------------------------------------- |
| 1         | Conceito atual (sistema especialista)        | `main.py`, chamado em `executar_missao()`                        |
| 2.1       | Hierarquia de prioridades                    | lista `SISTEMAS`, campo `prioridade`                            |
| 2.2       | Estados Verde / Amarelo / Vermelho           | `decidir_estado()`, `consumo_do_estado()`, `FREQUENCIA_TELEMETRIA` |
| 3.1       | Gastos pontuais × gastos constantes          | `aplicar_evento()` e o loop de horas em `simular_missao()`      |
| 3.2       | Margem de retorno e desligamento escalonado  | `calcular_margem()`, variável `alerta_margem`, `piorar()`       |
| 3.3 / 4.3 | Recarga solar                                | dicionário `RECARGA`, `definir_exposicao()`                     |
| 4.1       | Custos pontuais                              | `CUSTO_DECOLAGEM`, `CUSTO_MANOBRA`, `CUSTO_POUSO`               |
| 4.2       | Consumo por sistema                          | lista `SISTEMAS`                                                |
| 4.4       | Saldo = Recarga − Sistemas ativos            | passo 5 do loop de horas                                        |
| 5.1       | Fases e riscos                               | `montar_roteiro()`, `definir_clima()`                           |
| 5.2       | Rota rápida × econômica                      | `ROTAS`, `escolher_rota()`                                      |
| 5.3       | Checkpoints                                  | o bloco `if local == ...` no início de cada fase                |

### 6.2 Decisões tomadas onde o documento não dava o número (revisar)

| #  | Decisão                                   | Valor adotado                                                              | Onde mudar                        |
| :-: | :--------------------------------------- | :------------------------------------------------------------------------- | :-------------------------------- |
| 1  | Custo da frenagem em Marte                | 5% (igual a uma manobra)                                                   | `CUSTO_FRENAGEM`                  |
| 2  | Limiares dos estados por carga            | Verde ≥ 70%, Amarelo ≥ 50%, Vermelho abaixo                                | `LIMIAR_VERDE`, `LIMIAR_AMARELO`  |
| 3  | "Modo econômico" da comunicação           | 0,1 %/h (metade)                                                           | campo `economico` em `SISTEMAS`   |
| 4  | Folga pra desligar o alerta de margem     | margem ≥ 30 + 10 (evita ligar/desligar toda hora)                          | `FOLGA_MARGEM`                    |
| 5  | Bateria exatamente em 90%                 | vai pra rota rápida (`>=`)                                                 | `escolher_rota()`                 |
| 6  | Duração das fases (horas de simulação)    | atmosfera 2 · cruzeiro 60 (rápida) / 100 (econômica) · órbita 10 · superfície 24 | `HORAS_*` e `ROTAS`         |
| 7  | Tempestade solar                          | hora 30 do cruzeiro, 6 h, painéis recolhidos                               | `TEMPESTADE_SOLAR`                |
| 8  | Tempestade de poeira                      | hora 8 na superfície, 12 h, recarga parcial                                | `TEMPESTADE_POEIRA`               |
| 9  | Eclipses em órbita de Marte               | hora sim, hora não                                                         | `definir_exposicao()`             |
| 10 | "Tempo de retorno" da fórmula da margem   | um cruzeiro inteiro de volta                                               | `horas_retorno` em `simular_missao()` |
| 11 | "Consumo médio" da fórmula da margem      | queda média da bateria por hora desde a abertura dos painéis (já descontada a recarga) | `calcular_margem()`   |
| 12 | Redução de frequência de telemetria (2.2) | na tela: Amarelo a cada 2 h, Vermelho a cada 4 h; o TXT guarda todas as horas | `FREQUENCIA_TELEMETRIA`        |
| 13 | Eventos programados, não aleatórios       | a mesma entrada produz sempre o mesmo resultado                            | `definir_clima()`                 |

### 6.3 Conflitos entre este documento e o `main.py` (ainda em aberto)

| Item                | `main.py` (verificação)     | `upgrade.md` (missão) | Como está hoje                                                    |
| :------------------ | :-------------------------- | :-------------------- | :---------------------------------------------------------------- |
| Custo da decolagem  | 300 kWh + 8% = 32,4%        | 20%                   | os dois convivem: a verificação usa 32,4%, a missão usa 20%       |
| Reserva mínima      | 10% depois da decolagem     | 30% pra voltar        | os dois convivem, são regras diferentes                           |
| Unidade             | kWh (capacidade 1000)       | %                     | a missão trabalha em %; 1% = 10 kWh                               |

### 6.4 O que os números do documento produzem (observado nos testes)

- **A bateria nunca sobe.** A recarga máxima é 0,8 %/h e só o essencial (prioridade 1)
  já consome 0,8 %/h. Em Vermelho o saldo é zero; em Verde e Amarelo é negativo. O
  "saldo positivo" da seção 4.4 não acontece com esses valores.
- **Toda missão termina "com risco".** O pouso custa 10% e deixa a bateria abaixo dos 30%
  de reserva em todos os testes. Com 100% de carga inicial a nave chega ao pouso com 38%.
- Pra ver os três estados nas duas direções, o caminho mais curto é subir `RECARGA["total"]`
  (ex. 1,5 %/h) ou baixar os custos pontuais. São decisões de projeto, não de código.

Testes feitos: 92% (rota rápida), 85% (rota econômica), 100% (rota rápida) e 70%
(verificação abortou, missão cancelada). Nenhum erro.
