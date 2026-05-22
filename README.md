# pipeline-susep-resseguradoras

Pipeline de automacao operacional para monitoramento regulatorio de resseguradoras cadastradas na SUSEP.

O projeto coleta a base publica da SUSEP, padroniza os registros, compara a base atual com o ultimo historico disponivel e gera evidencias de alteracoes. A proposta e reduzir trabalho manual, aumentar rastreabilidade e demonstrar a evolucao de um MVP local para uma execucao automatizada em nuvem com GitHub Actions.

## Contexto

Em rotinas de resseguro, acompanhar alteracoes em cadastros regulatorios ajuda a manter controles internos atualizados e reduz o risco de usar informacoes defasadas. Sem automacao, a verificacao tende a depender de consultas manuais, planilhas avulsas e comparacoes pouco rastreaveis.

Este pipeline transforma essa rotina em um fluxo reproduzivel:

1. coleta os dados na fonte publica da SUSEP;
2. padroniza os campos relevantes;
3. compara a base atual com o ultimo snapshot historico;
4. registra novos, removidos e alterados;
5. salva logs, historico e relatorios para consulta posterior.

## Resultado esperado

Ao final de cada execucao, o projeto entrega:

- base bruta coletada em `data/raw`;
- base padronizada atual em `data/processed`;
- snapshot historico em `data/history`;
- log da execucao em `outputs/logs`;
- relatorio de alteracoes em `outputs/reports`.

Na primeira execucao, o pipeline cria um baseline historico. Nas execucoes seguintes, passa a comparar a nova coleta com a ultima base historica.

## Arquitetura

```text
pipeline-susep-resseguradoras/
|-- src/
|   |-- main.py
|   |-- coleta_susep.py
|   |-- tratamento.py
|   |-- comparacao.py
|   `-- utils.py
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- history/
|-- outputs/
|   |-- logs/
|   `-- reports/
|-- .github/
|   `-- workflows/
|       `-- monitoramento-susep.yml
|-- requirements.txt
|-- README.md
`-- .gitignore
```

## Componentes

- `src/main.py`: ponto de entrada e orquestracao do pipeline.
- `src/coleta_susep.py`: coleta os dados de resseguradoras locais, admitidas e eventuais na pagina publica da SUSEP.
- `src/tratamento.py`: limpa valores, padroniza colunas e cria a chave de monitoramento.
- `src/comparacao.py`: identifica registros novos, removidos e alterados.
- `src/utils.py`: centraliza caminhos do projeto, criacao de diretorios e configuracao de logs.
- `.github/workflows/monitoramento-susep.yml`: executa o pipeline em ambiente Linux no GitHub Actions.

## Como rodar localmente

Requisito: Python 3.10 ou superior.

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

Execute:

```powershell
python -m src.main
```

Todos os caminhos sao relativos ao repositorio. O projeto nao depende de pastas locais especificas, rede corporativa, Outlook ou planilhas abertas manualmente.

## Execucao em nuvem

O workflow do GitHub Actions permite duas formas de execucao:

- manual, por `workflow_dispatch`;
- agendada, em dias uteis, pelo cron configurado.

Durante a execucao em nuvem, o Actions instala Python, instala as dependencias, prepara o Chromium usado pelo Playwright, roda `python -m src.main` e publica `data/` e `outputs/` como artefatos por 30 dias.

Esse desenho mostra a evolucao natural do MVP:

- fase 1: execucao local controlada;
- fase 2: historico e relatorios versionaveis como artefatos;
- fase 3: automacao recorrente em nuvem;
- fase 4: notificacoes e persistencia externa.

## Rastreabilidade

A rastreabilidade e sustentada por tres elementos:

- snapshots historicos em CSV, um por execucao;
- logs com horario, etapa e arquivos gerados;
- relatorios com contagem de alteracoes e detalhamento dos campos modificados.

Essa estrutura facilita explicar quando a base foi consultada, qual foi a fonte usada e o que mudou entre duas execucoes.

## Limites do MVP

- A coleta depende da estrutura atual da pagina publica da SUSEP.
- No GitHub Actions, os artefatos ficam disponiveis pelo periodo de retencao configurado.
- Ainda nao ha notificacao automatica para e-mail, Teams ou Slack.
- Os relatorios foram mantidos em CSV e Markdown para priorizar portabilidade.

## Proximas evolucoes

- Persistir historico em storage externo ou branch dedicada.
- Criar testes automatizados para tratamento e comparacao.
- Gerar relatorio Excel multiplataforma com `openpyxl`.
- Adicionar notificacoes usando secrets do GitHub.
- Criar painel simples para consulta historica das alteracoes.

## Roteiro sugerido para apresentacao

1. Problema: acompanhamento manual de cadastros regulatorios consome tempo e gera pouca rastreabilidade.
2. Solucao: pipeline coleta, trata, compara e gera evidencias.
3. Arquitetura: separar coleta, tratamento, comparacao, logs e relatorios.
4. Demonstracao: rodar `python -m src.main` e mostrar as pastas `data/` e `outputs/`.
5. Evolucao: GitHub Actions permite transformar o MVP local em monitoramento recorrente em nuvem.
