# Teste avaliativo para vaga de bolsista em engenharia/análise de dados

## Descrição geral

Os candidatos deverão extrair dados da API indicada, realizar tratamento (limpeza, normalização e tipagem), armazenar os dados em um banco de dados relacional e, em seguida, efetuar uma análise quantitativa e qualitativa. O objetivo é demonstrar:

- [ ] Capacidade de integração com APIs
- [ ] Habilidade de transformação e estruturação de dados
- [ ] Conhecimentos em bancos de dados
- [ ] Análise crítica dos resultados
- [ ] Clareza na comunicação das conclusões

## Instruções

### 1. Extração de Dados
Utilize a seguinte API: Consulta Cadastro Integrado de Projetos de Investimentos - ObrasGov.br

- https://www.gov.br/conecta/catalogo/apis/consulta-cadastro-integrado-de-projetos-de-investimentos-2013-obrasgov.br
    - https://api.obrasgov.gestao.gov.br/obrasgov/api/swagger-ui/index.html
        - https://api-obrasgov.dth.api.gov.br/obrasgov/api%20/projeto-investimento?idUnico=01.52-52&page=0&size=10
Endpoint a ser utilizado: /projeto-investimento


- Realize uma requisição filtrando os dados apenas para o Distrito Federal (DF).

2. Busca exploratória dos dados:
Visão geral dos dados: colunas, dimensões, tipos de variáveis, taxas de valores nulos.
Estatísticas descritivas
Qualidade dos dados



3. Tratamento dos Dados
Realize tipagem adequada (ex.: datas como datetime, valores numéricos como float ou int, strings normalizadas etc.).


Normalize os dados (ex.: padronização de nomes de colunas, remoção de duplicatas, tratamento de valores ausentes).


Caso encontre problemas de inconsistência ou anomalias, registre-os no relatório.


4. Armazenamento dos Dados
Escolha um banco de dados de sua preferência (ex.: SQLite, PostgreSQL, MySQL).


Carregue os dados tratados no banco.


Documente o processo de criação das tabelas/coleções e a inserção dos dados.

5. Análise Qualitativa
Crie visualizações apropriadas (histogramas, gráficos de barras, dispersão, etc.) para ilustrar as conclusões.
Explore os dados e identifique padrões ou inconsistências relevantes.


Apresente hipóteses ou insights sobre possíveis causas para os resultados obtidos.


Explique de forma clara e objetiva, como se fosse comunicar para alguém não técnico.


Formato de Entrega
Disponibilizar o código em um Jupyter Notebook no GitHub.


O notebook deve conter:


Código de extração da API,


Tratamento e carregamento dos dados,


Análises quantitativa e qualitativa,


Visualizações,


Conclusões finais.


Enviar o link do repositório no Telegram @davi_aguiar_vieira ou @mateus_castro3.





Prazo de Entrega
O prazo limite para entrega do desafio é até 17/10

Observações
Um exemplo simples de apoio (não restritivo) pode ser visto aqui: Exemplo de análise com Python e SQL.


O candidato pode utilizar bibliotecas de sua preferência (ex.: requests, pandas, sqlalchemy, matplotlib, seaborn, etc.).


Avaliaremos tanto a qualidade técnica do código quanto a clareza na comunicação dos resultados.
Qualquer dúvida entre em contato com @davi_aguiar_vieira ou @mateus_castro3 por meio do Telegram.

