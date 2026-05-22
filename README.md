# pipeline-susep-resseguradoras

Pipeline de automação operacional para monitoramento regulatório de resseguradoras cadastradas na SUSEP.

O projeto coleta a base pública da SUSEP, padroniza os registros, compara a base atual com o último histórico disponível e gera evidências de alterações. A proposta é reduzir trabalho manual, aumentar rastreabilidade e demonstrar a evolução de um MVP local para uma execução automatizada em nuvem com GitHub Actions.

## Contexto

Em rotinas de resseguro, acompanhar alterações em cadastros regulatórios ajuda a manter controles internos atualizados e reduz o risco de usar informações defasadas. Sem automação, a verificação tende a depender de consultas manuais, planilhas avulsas e comparações pouco rastreáveis.

Este pipeline transforma essa rotina em um fluxo reproduzível:

1. coleta os dados na fonte pública da SUSEP;
2. padroniza os campos relevantes;
3. compara a base atual com o último snapshot histórico;
4. registra novos, removidos e alterados;
5. salva logs, histórico e relatórios para consulta posterior.

## Resultado esperado

Ao final de cada execução, o projeto entrega:

- base bruta coletada em `data/raw`;
- base padronizada atual em `data/processed`;
- snapshot histórico em `data/history`;
- log da execução em `outputs/logs`;
- relatório de alterações em `outputs/reports`.

Na primeira execução, o pipeline cria um baseline histórico. Nas execuções seguintes, passa a comparar a nova coleta com a última base histórica.

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

- `src/main.py`: ponto de entrada e orquestração do pipeline.
- `src/coleta_susep.py`: coleta os dados de resseguradoras locais, admitidas e eventuais na página pública da SUSEP.
- `src/tratamento.py`: limpa valores, padroniza colunas e cria a chave de monitoramento.
- `src/comparacao.py`: identifica registros novos, removidos e alterados.
- `src/utils.py`: centraliza caminhos do projeto, criação de diretórios e configuração de logs.
- `.github/workflows/monitoramento-susep.yml`: executa o pipeline em ambiente Linux no GitHub Actions.

## Como rodar localmente

Requisito: Python 3.10 ou superior.

No Windows, crie o ambiente virtual usando o launcher `py`:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

Execute:

```powershell
python -m src.main
```

Todos os caminhos são relativos ao repositório. O projeto não depende de pastas locais específicas, rede corporativa, Outlook ou planilhas abertas manualmente.

## Execução em nuvem

O workflow do GitHub Actions permite duas formas de execução:

- manual, por `workflow_dispatch`;
- agendada, em dias úteis, pelo cron configurado.

Durante a execução em nuvem, o Actions instala Python, instala as dependências, prepara o Chromium usado pelo Playwright, roda `python -m src.main` e publica `data/` e `outputs/` como artefatos por 30 dias.

Esse desenho mostra a evolução natural do MVP:

- fase 1: execução local controlada;
- fase 2: histórico e relatórios versionáveis como artefatos;
- fase 3: automação recorrente em nuvem;
- fase 4: notificações e persistência externa.

## Rastreabilidade

A rastreabilidade é sustentada por três elementos:

- snapshots históricos em CSV, um por execução;
- logs com horário, etapa e arquivos gerados;
- relatórios com contagem de alterações e detalhamento dos campos modificados.

Essa estrutura facilita explicar quando a base foi consultada, qual foi a fonte usada e o que mudou entre duas execuções.

## Limites do MVP

- A coleta depende da estrutura atual da página pública da SUSEP.
- No GitHub Actions, os artefatos ficam disponíveis pelo período de retenção configurado.
- Ainda não há notificação automática para e-mail, Teams ou Slack.
- Os relatórios foram mantidos em CSV e Markdown para priorizar portabilidade.

## Próximas evoluções

- Persistir histórico em storage externo ou branch dedicada.
- Criar testes automatizados para tratamento e comparação.
- Gerar relatório Excel multiplataforma com `openpyxl`.
- Adicionar notificações usando secrets do GitHub.
- Criar painel simples para consulta histórica das alterações.

## Roteiro sugerido para apresentação

1. Problema: acompanhamento manual de cadastros regulatórios consome tempo e gera pouca rastreabilidade.
2. Solução: pipeline coleta, trata, compara e gera evidências.
3. Arquitetura: separar coleta, tratamento, comparação, logs e relatórios.
4. Demonstração: rodar `python -m src.main` e mostrar as pastas `data/` e `outputs/`.
5. Evolução: GitHub Actions permite transformar o MVP local em monitoramento recorrente em nuvem.
