# 1.6 — Reflexão Crítica

> Reflexão sobre as implicações éticas, sociais e ambientais do sistema
> desenvolvido no Projeto AURORA. As considerações partem de decisões concretas
> tomadas durante a implementação, e não de princípios abstratos.

---

## 1. Ética e Responsabilidade

### 1.1 Quem responde quando o sistema erra?

O sistema que construímos termina imprimindo uma frase: "Decolagem Autorizada" ou
"Decolagem Não Autorizada". É uma sentença curta, e é fácil esquecer que por trás
dela existe uma cadeia de decisões humanas — nossas.

Os valores que determinam essa frase foram escolhidos por nós: energia mínima de
80%, pressão entre 450 e 550 psi, temperatura interna entre 15°C e 30°C, perdas
energéticas de 8%, reserva de pouso de 10%. Nenhum desses números foi medido em
bancada, nem validado contra hardware real. São estimativas razoáveis, defensáveis
tecnicamente, mas ainda assim estimativas.

Isso define onde está a responsabilidade: **não é o algoritmo que autoriza a
decolagem, são as pessoas que definiram os limites**. O código apenas aplica, de
forma rápida e consistente, um julgamento que já havia sido feito antes. Um sistema
automatizado não transfere responsabilidade — ele a concentra no momento do projeto,
quando ninguém está sob pressão e todos os erros ainda são baratos.

Por isso documentar a origem de cada valor não é burocracia acadêmica: é a única
forma de alguém, no futuro, conseguir contestar um limite mal calibrado.

### 1.2 O risco da confiança automática

Durante os testes, um cenário nos ensinou mais do que todos os outros. Informamos
energia de 105% e integridade estrutural igual a 3. As seis verificações de
segurança aprovaram tudo — afinal, 105 não é menor que 80, e 3 não é menor que 1.
O sistema teria autorizado a decolagem de uma nave cujos sensores estavam
claramente corrompidos.

A lição é desconfortável: **um sistema de verificação pode dar uma sensação de
segurança maior do que a segurança que efetivamente oferece**. Cada regra estava
correta isoladamente. O conjunto delas, ainda assim, falhava.

Esse fenômeno tem nome na literatura de fatores humanos: viés de automação. Quando
uma máquina exibe um veredito, as pessoas tendem a verificar menos, não mais. Um
"DECOLAGEM AUTORIZADA" na tela desestimula exatamente o olhar crítico que deveria
existir antes de um lançamento.

### 1.3 Decisões de projeto com conteúdo ético

Três escolhas nossas foram, no fundo, escolhas éticas — ainda que tenham parecido
apenas técnicas no momento:

**A classificação em três faixas.** O sistema poderia ter apenas "autorizada" ou
"abortada". Criamos uma terceira condição — decolagem autorizada *com ressalvas* —
justamente para que o operador humano não seja dispensado de pensar. Um veredito
binário empurra a decisão inteiramente para o algoritmo; um veredito que diz "está
liberado, mas observe estes três pontos" devolve a decisão para quem tem
responsabilidade sobre ela.

**A explicação junto com o veredito.** O sistema não diz apenas que barrou; ele
lista o que encontrou e por quê. Sistemas opacos não podem ser contestados, e o que
não pode ser contestado não pode ser corrigido. Em contextos de risco à vida, a
capacidade de questionar a máquina é um requisito, não um recurso extra.

**A falha para o lado seguro.** Na leitura dos módulos críticos, qualquer entrada
diferente de "S" é interpretada como sistema offline. Um simples erro de digitação
bloqueia a decolagem. Isso é intencional: quando a dúvida é entre atrasar um
lançamento e arriscar uma tripulação, o custo dos dois erros não é comparável.

### 1.4 O limite honesto do que construímos

Nosso sistema avalia um único instante. Não observa tendências, não detecta um
sensor que travou repetindo o mesmo valor, e não reverifica nada depois de dar a
autorização — um módulo crítico pode cair no segundo seguinte.

Reconhecer isso publicamente, no próprio relatório, é parte da postura ética.
Apresentar um trabalho acadêmico como se fosse um sistema pronto para voo seria
uma forma de desonestidade técnica, mesmo que involuntária.

---

## 2. Impacto Social da Exploração Espacial

### 2.1 O custo de oportunidade é real

Todo recurso aplicado em exploração espacial é um recurso que não foi aplicado em
saneamento, educação ou saúde. Esse argumento é legítimo e merece resposta honesta,
não desdém.

A resposta honesta é que a comparação raramente é direta. Boa parte da
infraestrutura que sustenta a vida contemporânea nasceu de programas espaciais:
previsão meteorológica, comunicações, geolocalização, e o monitoramento por satélite
que hoje detecta desmatamento, queimadas e derretimento de calotas polares. O
conhecimento sobre mudanças climáticas na Terra depende, em grande medida, de
instrumentos que estão fora dela.

Isso não encerra o debate — apenas o desloca. A pergunta útil não é "espaço ou
problemas terrestres", e sim **quem decide o que é lançado, com dinheiro de quem e
em benefício de quem**.

### 2.2 Concentração de decisão

A capacidade de lançamento está concentrada em poucos países e, cada vez mais, em
poucas empresas privadas. Quando uma corporação decide unilateralmente o que ocupa
a órbita terrestre, uma decisão de consequências globais passa a ser tomada sem
representação global.

Constelações com milhares de satélites já alteram observações astronômicas e
disputam faixas orbitais. A órbita é um bem comum, finito, e atualmente governado
por acordos frágeis.

### 2.3 Lixo espacial

Cada lançamento adiciona objetos a um ambiente que não se limpa sozinho. A
preocupação técnica com colisões em cascata — o cenário em que detritos geram mais
detritos até inviabilizar faixas orbitais inteiras — deixou de ser hipótese remota.

Um sistema que aborta lançamentos inseguros contribui diretamente para isso: um
veículo que falha em voo não representa apenas a perda da missão, mas detritos
permanentes em uma órbita compartilhada por todos.

### 2.4 Quem está embaixo da trajetória

Existe um aspecto do nosso projeto que costuma passar despercebido. O botão de
abortar não protege apenas a tripulação e o patrimônio: protege as comunidades
sobre as quais o veículo vai passar.

Bases de lançamento são frequentemente instaladas em regiões periféricas, próximas
a populações que não participaram da decisão de instalá-las e não se beneficiam
diretamente delas. Um critério de segurança rigoroso é, nesse sentido, uma forma
concreta de respeito a pessoas que não estão na sala de controle e nunca serão
consultadas.

---

## 3. Sustentabilidade Tecnológica

### 3.1 A escolha elétrica não é neutra

O AURORA opera com um banco de baterias de 1000 kWh. Propulsão elétrica elimina a
queima direta de combustível, mas a conta ambiental não termina aí.

A eletricidade que carrega a bateria tem uma origem — e um sistema alimentado por
matriz predominantemente fóssil apenas desloca a emissão para outro lugar. Além
disso, baterias de lítio dependem de mineração intensiva em água, frequentemente em
regiões áridas e habitadas por comunidades que arcam com o custo ambiental sem
participar do benefício.

Chamar a tecnologia de "limpa" sem examinar a cadeia inteira é uma simplificação
que atrapalha decisões melhores.

### 3.2 Vida útil e degradação

Uma das regras do nosso motor de análise trata da relação entre energia e
temperatura: baterias de lítio perdem capacidade utilizável no frio. Uma leitura de
80% a −10°C não entrega os mesmos kWh que 80% a 25°C.

Essa regra tem uma implicação de sustentabilidade que vai além da segurança:
**baterias não são componentes estáveis**. Elas degradam com ciclos, temperatura e
tempo. Um projeto responsável considera a substituição, a reciclagem e o destino
final desse material desde o início — e não como problema de outra equipe, anos
depois.

### 3.3 Eficiência como decisão ambiental

Assumimos 8% de perdas por conversão e aquecimento. Sobre um consumo de 300 kWh,
são 24 kWh desperdiçados a cada decolagem, transformados em calor.

Reduzir esse percentual é, ao mesmo tempo, ganho de autonomia e ganho ambiental.
Vale notar também o efeito oposto: superdimensionar a bateria para compensar
ineficiência aumenta a massa do veículo, que por sua vez aumenta o consumo e o
volume de material extraído. Eficiência e sustentabilidade, aqui, apontam na mesma
direção.

A reserva mínima de 10% que implementamos é justamente uma tentativa de equilíbrio:
grande o bastante para garantir manobra e pouso, pequena o bastante para não exigir
uma bateria superdimensionada em cada missão.

### 3.4 A sustentabilidade do próprio software

Existe uma dimensão de sustentabilidade que raramente aparece nesse debate: a do
código.

Sistemas críticos são mantidos por décadas, por equipes que mudam. Se as regras de
segurança estiverem espalhadas em números soltos pelo código, sem explicação de
origem, cada manutenção futura vira um risco. Foi por isso que concentramos os
limites em constantes nomeadas e registramos, no roadmap, a justificativa de cada
faixa.

Em software comum, débito técnico custa tempo. Em software que decide sobre vidas,
débito técnico custa segurança.

---

## 4. Conclusão

O aprendizado central deste projeto não foi programar condicionais, e sim perceber
que **um sistema de segurança é a formalização de um julgamento humano** — com todas
as limitações de quem o formulou.

Nosso algoritmo é tão bom quanto os limites que escolhemos, tão honesto quanto os
pressupostos que documentamos, e tão útil quanto a disposição do operador de
continuar pensando depois de ler o veredito na tela.

O cenário em que o sistema aprovou uma bateria com 105% de carga resume bem a
questão. A tecnologia fez exatamente o que mandamos fazer. O erro não estava na
execução — estava na nossa suposição de que os dados de entrada seriam confiáveis.

Nenhuma automação elimina esse tipo de erro. Ela apenas o desloca para mais cedo,
para o momento em que o sistema foi projetado, onde ainda havia tempo de perceber.
