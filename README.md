# pipeline-susep-resseguradoras

Pipeline de automação operacional para monitoramento regulatório de resseguradoras cadastradas na SUSEP.

O projeto coleta a base pública da SUSEP, padroniza os registros, compara a base atual com o último histórico disponível e gera evidências de alterações. A proposta é reduzir trabalho manual, aumentar rastreabilidade e demonstrar a evolução de um MVP local para uma execução automatizada em nuvem com GitHub Actions e visualização em Streamlit.

## Contexto

Em rotinas de resseguro, acompanhar alterações em cadastros regulatórios ajuda a manter controles internos atualizados e reduz o risco de usar informações defasadas. Sem automação, a verificação tende a depender de consultas manuais, planilhas avulsas e comparações pouco rastreáveis.

Este pipeline transforma essa rotina em um fluxo reproduzível:

1. coleta os dados na fonte pública da SUSEP;
2. padroniza os campos relevantes;
3. compara a base atual com o último snapshot histórico;
4. registra novos, removidos e alterados;
5. versiona histórico e relatórios no repositório;
6. disponibiliza uma visão gerencial em Streamlit.

## Resultado esperado

Ao final de cada execução, o projeto entrega:

- base bruta coletada em `data/raw`;
- base padronizada atual em `data/processed`;
- snapshot histórico versionável em `data/history`;
- log da execução em `outputs/logs`;
- relatório de alterações versionável em `outputs/reports`;
- dashboard em `app/dashboard.py` para acompanhar as análises.

Na primeira execução, o pipeline cria um baseline histórico. Nas execuções seguintes, passa a comparar a nova coleta com a última base histórica.

## Arquitetura

```text
pipeline-susep-resseguradoras/
|-- app/
|   `-- dashboard.py
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
- `app/dashboard.py`: dashboard Streamlit para consulta do histórico e dos relatórios.
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

Execute o pipeline:

```powershell
python -m src.main
```

Execute o dashboard:

```powershell
streamlit run app/dashboard.py
```

Todos os caminhos são relativos ao repositório. O projeto não depende de pastas locais específicas, rede corporativa, Outlook ou planilhas abertas manualmente.

## Execução em nuvem

O workflow do GitHub Actions permite duas formas de execução:

- manual, por `workflow_dispatch`;
- agendada, em dias úteis, pelo cron configurado.

Durante a execução em nuvem, o Actions instala Python, instala as dependências, prepara o Chromium usado pelo Playwright, roda `python -m src.main`, publica `data/` e `outputs/` como artefatos por 30 dias e commita os arquivos de `data/history` e `outputs/reports` no repositório.

Esse desenho mostra a evolução natural do MVP:

- fase 1: execução local controlada;
- fase 2: histórico e relatórios versionáveis;
- fase 3: automação recorrente em nuvem;
- fase 4: dashboard em Streamlit para acompanhamento diário.

## Dashboard Streamlit

O dashboard lê os arquivos versionados pelo GitHub Actions e apresenta:

- total de registros monitorados;
- quantidade de registros novos, removidos e alterados na última execução;
- distribuição da base atual por tipo de resseguradora;
- tabela filtrável de alterações;
- histórico de snapshots;
- download do relatório CSV.

Para publicar no Streamlit Community Cloud, use:

- repositório: este projeto no GitHub;
- branch: `main` ou a branch principal do repositório;
- arquivo principal: `app/dashboard.py`.

Depois do deploy, cada commit feito pelo GitHub Actions com novos relatórios atualiza a base lida pelo dashboard.

## Rastreabilidade

A rastreabilidade é sustentada por três elementos:

- snapshots históricos em CSV, um por execução;
- relatórios de alterações em CSV e Markdown;
- logs com horário, etapa e arquivos gerados.

Essa estrutura facilita explicar quando a base foi consultada, qual foi a fonte usada e o que mudou entre duas execuções.

## Limites do MVP

- A coleta depende da estrutura atual da página pública da SUSEP.
- O histórico passa a ser versionado no próprio repositório, solução simples e adequada para MVP.
- Ainda não há notificação automática para e-mail, Teams ou Slack.
- O dashboard depende dos arquivos já gerados e versionados pelo pipeline.

## Próximas evoluções

- Persistir histórico em storage externo ou banco de dados.
- Criar testes automatizados para tratamento, comparação e dashboard.
- Gerar relatório Excel multiplataforma com `openpyxl`.
- Adicionar notificações usando secrets do GitHub.
- Criar indicadores de tendência e tempo desde a última alteração por entidade.

## Roteiro sugerido para apresentação

1. Problema: acompanhamento manual de cadastros regulatórios consome tempo e gera pouca rastreabilidade.
2. Solução: pipeline coleta, trata, compara, gera evidências e versiona histórico.
3. Arquitetura: separar coleta, tratamento, comparação, logs, relatórios e dashboard.
4. Demonstração: rodar `python -m src.main` e abrir `streamlit run app/dashboard.py`.
5. Evolução: GitHub Actions e Streamlit transformam o MVP local em monitoramento recorrente e acompanhável em nuvem.
