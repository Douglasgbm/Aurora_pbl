# Aurora_pbl

Projeto integrador (PBL) — sistema de verificação de telemetria e autorização de
decolagem. Consulte o [ROADMAP.MD](ROADMAP.MD) para a especificação completa e o
[analise_assistida_ia.md](analise_assistida_ia.md) para a análise de dados,
anomalias e riscos.

## Como executar

```bash
python scripts/usuario.py
```

O programa solicita os dados de telemetria, executa as seis verificações de
segurança, calcula a autonomia energética e emite o parecer da análise assistida
por IA antes do veredito final.

---

## Pendências desta documentação

> Anotações de trabalho — substituir pelo texto final antes da entrega.

EXPLICAR AS METRICAS IDEIAIS CONFORME PRE ESTABELECIDO
CONSIDERAR QUE O PROGRAMA REFLETE O USO REAL DO MESMO, LEVANDO EM CONSIDERAÇAO O QUE O USUARIO ESTARA COLETANDO
DE METRICAS.

Faltam ainda, conforme os entregáveis do roadmap:

- Explicação do projeto
- Prints da execução
- Instruções de execução detalhadas
- Notebook Python (.ipynb)



CENARIOS - OTIMO - MEDIO - HORRIVEL - 10x

| Temp. Interna | 20 a 25 °C | 15–20 ou 25–30 °C | < 15 ou > 30 °C |
| Temp. Externa | 0 a 35 °C | −10–0 ou 35–45 °C | < −10 ou > 45 °C |
| Pressão | 480 a 520 psi | 450–480 ou 520–550 psi | < 450 ou > 550 psi |
| Energia | ≥ 90 % | 80 a 90 % | < 80 % |

10 50 350 70 - PESSIMO
25 30 550 80 - MEDIO
25 30 480 100 - OTIMO 

DOCUMENTAR O PROJETO - FLUXOGRAMA 


FLUXO


