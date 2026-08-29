# 1.5 — Análise Assistida por IA

> Análise gerada com apoio de IA (Claude) sobre a telemetria e o algoritmo de
> verificação do Projeto AURORA. Cobre os três pontos exigidos pelo roadmap:
> **classificação dos dados**, **identificação de anomalias** e
> **sugestões de risco**.

---

## 1. Classificação dos Dados

### 1.1 Por natureza da variável

| Parâmetro | Natureza estatística | Unidade | Faixa segura |
| :--- | :--- | :--- | :--- |
| Temperatura Interna | Quantitativa contínua | °C | 15 a 30 |
| Temperatura Externa | Quantitativa contínua | °C | −10 a 45 |
| Integridade Estrutural | Qualitativa binária (indicador) | — | apenas 1 |
| Pressão dos Tanques | Quantitativa contínua | psi | 450 a 550 |
| Nível de Energia | Quantitativa contínua (proporção) | % | mínimo de 80 |
| Módulos Críticos | Qualitativa binária | — | todos online |

A distinção importa para o desenho do algoritmo: variáveis **contínuas** admitem
faixa de tolerância e banda de atenção; variáveis **binárias** não admitem
meio-termo — ou estão no valor esperado, ou são aborto imediato.

### 1.2 Por criticidade (consequência da violação)

| Classe | Parâmetros | Característica da falha | Tempo de reação |
| :--- | :--- | :--- | :--- |
| **A — Catastrófica** | Integridade, Módulos Críticos | Binária, súbita, sem aviso prévio | Nenhum |
| **B — Progressiva** | Pressão, Energia | Degrada ao longo do voo | Minutos |
| **C — Ambiental** | Temperatura Interna e Externa | Degrada componentes, raramente causa perda imediata | Dezenas de minutos |

Esta classificação **justifica a ordem do fluxograma** proposto no roadmap:
testar primeiro a Classe A é a decisão correta, porque nenhuma leitura posterior
tem valor se a estrutura já está comprometida.

### 1.3 Faixas de classificação operacional

O algoritmo atual é **binário** (OK / Erro). Um sistema de telemetria real
classifica em três estados. Proposta de banda de atenção:

| Parâmetro | 🟢 NOMINAL | 🟡 ATENÇÃO | 🔴 CRÍTICO (aborto) |
| :--- | :--- | :--- | :--- |
| Temperatura Interna | 20 a 25 °C | 15 a 20 ou 25 a 30 °C | abaixo de 15 ou acima de 30 °C |
| Temperatura Externa | 0 a 35 °C | −10 a 0 ou 35 a 45 °C | abaixo de −10 ou acima de 45 °C |
| Pressão | 480 a 520 psi | 450 a 480 ou 520 a 550 psi | abaixo de 450 ou acima de 550 psi |
| Energia | 90 % ou mais | 80 a 90 % | abaixo de 80 % |
| Integridade | 1 | — | qualquer valor diferente de 1 |
| Módulos | Online | — | Offline |

**Interpretação:** a faixa 🟡 não impede a decolagem, mas indica que o parâmetro
está consumindo a margem de segurança. Dois ou mais parâmetros simultaneamente
em 🟡 configuram um cenário que merece revisão humana antes do lançamento.

---

## 2. Identificação de Anomalias

### 2.1 Anomalias nos dados de telemetria

| ID | Anomalia | Como se manifesta | Por que é suspeita |
| :--- | :--- | :--- | :--- |
| **A1** | Valor fora do domínio físico | Energia informada como 250 % ou como valor negativo | Uma bateria não pode ter 250 % de carga. Indica sensor descalibrado ou erro de digitação — e o algoritmo atual **autoriza a decolagem** nessa condição |
| **A2** | Integridade fora do domínio binário | Integridade informada como 2, 7 ou qualquer valor acima de 1 | O indicador é binário por definição; valor fora do domínio revela corrupção de dados. O algoritmo atual **trata como íntegro** |
| **A3** | Diferencial térmico incoerente | Interna a 29 °C com externa a −9 °C (diferença de 38 °C) | Os dois valores passam individualmente, mas o diferencial sugere falha de isolamento térmico ou sensor travado |
| **A4** | Telemetria perfeitamente nominal | Todos os canais exatamente no valor ideal (22 / 25 / 1 / 500 / 100 / online) | Estatisticamente improvável em hardware real. Sugere dado sintético ou sensores retornando valor padrão de fábrica |
| **A5** | Operação na fronteira | Energia em exatamente 80 % ou pressão em exatamente 450 psi | Passa na verificação, mas sem nenhuma margem para a incerteza do próprio sensor (tipicamente ±2 %). O valor real pode já estar abaixo do limite |
| **A6** | Acoplamento pressão–temperatura | Pressão a 545 psi com temperatura interna a 29 °C | Pela lei dos gases, a pressão sobe com a temperatura. Ambos passam no solo, mas o aquecimento da decolagem pode empurrar a pressão além de 550 psi **já em voo** |
| **A7** | Sensor travado | Mesmo valor repetido em leituras sucessivas | Não detectável na arquitetura atual — exigiria histórico de leituras |

### 2.2 Pontos cegos do algoritmo

Anomalias que o algoritmo **não consegue enxergar** por construção:

| ID | Ponto cego | Consequência |
| :--- | :--- | :--- |
| **B1** | Ausência de tratamento de entrada inválida | Uma entrada em texto onde se espera número interrompe o programa **no meio da checagem**, sem veredito e sem registro |
| **B2** | Integridade testada por "menor que 1" em vez de "diferente de 1" | Valores acima de 1 passam como íntegros (ver A2) |
| **B3** | Energia sem limite superior | O teto de 100 % não é validado (ver A1) |
| **B4** | Verificações independentes entre si | Não existe nenhuma regra que cruze dois parâmetros; as anomalias A3 e A6 são invisíveis |
| **B5** | Análise pontual, de um único instante | Sem série temporal, deriva lenta e sensor travado não são detectáveis |
| **B6** | Ausência de registro das leituras | Não há rastreabilidade dos valores avaliados para investigação pós-falha |
| **B7** | Verificação única, não contínua | Um módulo crítico pode cair no segundo seguinte à autorização |

> **Observação sobre os módulos críticos:** a leitura converte para maiúscula e
> compara com "S", de modo que qualquer entrada diferente disso é interpretada
> como offline. Um erro de digitação bloqueia a decolagem indevidamente — mas
> esse é o comportamento **correto** para sistemas críticos: na dúvida, o
> sistema falha para o lado seguro (*fail-safe*).

---

## 3. Sugestões de Risco

Severidade e probabilidade avaliadas para o cenário atual do projeto.

| ID | Risco | Gatilho | Severidade | Prob. | Mitigação recomendada |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | **Ruptura do tanque em voo** | Pressão limítrofe (A5) somada ao aquecimento durante a subida (A6) | Catastrófica | Média | Estreitar o limite operacional para 470 a 530 psi, reservando a faixa de 450 a 550 como limite absoluto de projeto |
| **R2** | **Perda de potência antes do pouso** | Perdas energéticas reais acima dos 8 % estimados | Catastrófica | Média | Manter a reserva mínima pós-decolagem de 10 % e revisar o coeficiente de perdas com dados de bancada |
| **R3** | **Falha estrutural em voo** | Integridade corrompida aceita como válida (A2 e B2) | Catastrófica | Baixa | Validar o domínio do indicador, exigindo igualdade a 1 |
| **R4** | **Perda de controle** | Módulo crítico cai após a autorização (B7) | Catastrófica | Baixa | Reverificar os módulos em janela curta imediatamente antes da ignição |
| **R5** | **Degradação da bateria pelo frio** | Temperatura externa próxima de −10 °C com energia próxima de 80 % | Alta | **Alta** | Baterias de lítio perdem capacidade **utilizável** em baixa temperatura: 80 % indicados a −10 °C não equivalem a 80 % entregáveis. Elevar o mínimo de energia exigido quando a temperatura externa for negativa |
| **R6** | **Superaquecimento da aviônica** | Temperatura interna em 29 a 30 °C somada ao calor gerado pelos motores | Alta | Média | Tratar a temperatura interna pré-ignição como **preditor** da temperatura em voo, e não como valor final |
| **R7** | **Autorização a partir de dado inválido** | Entrada fora do domínio físico (A1) ou erro de digitação | Alta | **Alta** | Validar a faixa física de cada entrada antes de avaliar as regras de segurança |
| **R8** | **Falso senso de segurança** | Veredito binário oculta que vários parâmetros estão no limite | Média | **Alta** | Adotar a classificação de três faixas da seção 1.3 e exigir revisão humana quando dois ou mais parâmetros estiverem em 🟡 |

### 3.1 Risco de maior retorno: R5 (acoplamento energia × temperatura)

É o achado mais relevante desta análise porque **nenhuma verificação individual
o detecta**. Energia em 80 % passa. Temperatura externa em −10 °C passa. A
combinação das duas, porém, representa uma condição em que a energia realmente
disponível é significativamente menor que a indicada — exatamente o cenário que
o limite de 80 % pretendia evitar.

### 3.2 Prioridade de correção

1. **R7 e B1** — validar as entradas (maior probabilidade, correção simples)
2. **R3 e B2** — corrigir o teste de integridade para exigir igualdade a 1
3. **R5** — criar regra cruzada entre energia e temperatura externa
4. **R8** — adotar a classificação em três faixas
5. **R1** — estreitar a faixa operacional de pressão

---

## 4. Conclusão

O algoritmo cumpre corretamente o que foi especificado: valida seis parâmetros
contra faixas predefinidas e emite um veredito. As fragilidades encontradas não
são erros de implementação da especificação, e sim **limites da própria
especificação** — que trata os parâmetros como independentes, avalia um único
instante no tempo e assume que os dados de entrada são confiáveis.

Em telemetria aeroespacial real, os três pressupostos são falsos. As anomalias
A3 e A6 e o risco R5 mostram que a informação crítica frequentemente está na
**relação entre os parâmetros**, e não no valor isolado de cada um.
