<!---
README do Projeto: Integração e Extração de Dados - Tiflux + Google Drive
-->

# Integração e Extração de Dados - Databricks + SISTEMA_WEB + Google Drive + Apps Script + Bigquery

## 📑 Índice

- [Resumo](#-resumo)
- [Fluxo do processo](#-Fluxo-do-Processo)
- [Bibliotecas Necessárias](#-bibliotecas-necessárias)
- [Autenticação no Sistema WEB](#-Autenticação-no-sistema-WEB)
- [Captura do Código OTP via Google Sheets e Apps Script](#-Captura-do-Código-OTP-via-Google-Sheets-e-Apps-Script)
- [Obtenção do Código OTP](#-Obtenção-do-Código-OTP)
- [Login final e obtenção do token de seção](#-Login-final-e-obtenção-do-token-de-seção)
- [Extração de relatórios do sistema](#-Extração-de-relatórios-do-sistema)
- [Tratamento dos Dados](#-Tratamento-dos-Dados)
- [Envio para o bigquery e logout](#-Envio-para-o-bigquery-e-logout)
- [Contato](#-Contato)

---

## 📄 Resumo

- Este projeto implementa uma solução de integração de dados com um sistema web. O fluxo automatizado inicia com o login automático no sistema, utilizando a interceptação da API e requisições POST para autenticação. Para sistemas com autenticação de dois fatores, o projeto captura o código mais recente enviado ao Gmail através da integração da API Gmail com Apps Script. Uma vez autenticado, os dados relevantes são extraídos do sistema web, transformados (ETL) e carregados para o BigQuery. Ao término da coleta de dados, o script realiza logout automático do sistema.
---

## 🔄 Fluxo do Processo

```mermaid
flowchart TD
    subgraph Login e Autenticação
        A[Requisição POST de Login Inicial] -->|Captura de código tmp| B(Gera código tmp);
        A -->|Dispara envio de token OTP| C(Integração Google Drive/Sheets);
        C -->|Grava mensagem| D[Apps Script: Leitura de Email e Extração de OTP];
        D -->|Captura OTP| E[Google Sheets];
        E -->|Lê código OTP| F[Requisição POST de Login Final];
        F -->|Parâmetros: tmp e OTP| G[Obtém Token de Autorização];
    end

    subgraph Extração e Tratamento
        G --> H[API de Extração de Dados];
        H --> I(Varredura e Captura de Informações);
        I --> J[Tratamento e Transformação dos Dados];
    end
    
    subgraph Carregamento e Logout
        J --> K[Envio para BigQuery];
        K --> L[Atualização do Banco de Dados];
        L --> M[Requisição POST de Logout];
    end
```

## 📚 Bibliotecas Necessárias

```bash
%pip install openpyxl google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client gspread drive pandas_gbq gspread_dataframe -q

````
### 🔐 Autenticação no Sistema WEB

**📂 Passos:**

O processo inicia com uma requisição POST para o sistema web. Nesta etapa, são capturados dois elementos cruciais:
*  O **código temporário (`tmp`)**, um código alfanumérico necessário para a segunda parte do login.
*  É realizado pelo sistema o disparo automático de um **código OTP** (token de acesso de uso único) para o e-mail do usuário.
---
### 🔐 Captura do Código OTP via Google Sheets e Apps Script

**🔄 Fluxo:**
Uma integração com o Google Drive e Google Sheets é ativada. Ao receber uma notificação, um App Script é acionado para:
*  Integrar com o e-mail do usuário.
*  Ler o e-mail mais recente da notificação do token.
*  Extrair o **código OTP** contido na mensagem.
*  Gravar o código na planilha do Google Sheets para uso posterior.
---
### 🛡️ Obtenção do Código OTP

- Aguarda atualização da planilha.
- Lê o código OTP de uma célula no Google Sheets via integração com o drive.
---

### ✅ Login final e obtenção do token de seção

Nesta etapa, fazemos uma requisição de login, utilizando os códigos capturados nas etapas anteriores como parâmetros via f-string:
1.  O **código `tmp`**.
2.  O **código OTP**.
3.  A requisição retorna o **token de autorização de sessão ativa**, que será utilizado para todas as interações futuras com a API do sistema.
* O capturamos através dos headers da API, fazendo um response.headers['authorization], ação a qual exibirá o token da seção, assim o armazenamos em uma variável deixando-o dinâmico.
```bash
token = response.headers['authorization]
````
---

### 🗃️ Extração de relatórios do sistema

**🕒 Detalhes:**

- Com o token de autorização em mãos, o processo realiza chamadas à API do sistema para capturar os dados priorizados.
- Define o período dos últimos 180 dias
- Pagina os resultados de tickets (controle de `offset`)
- Converte os dados para `DataFrame` com `pandas`
---

### 🛠️ Tratamento dos Dados

- Renomeia colunas
- Mapeia status de tickets
- Ajusta datas e horários para timezone `America/Sao_Paulo`

---

### 📝 Envio para o bigquery e logout

- Os dados tratados então são enviados para o BigQuery, atualizando o banco de dados.
- Em seguida para garantir a segurança e liberar a sessão, uma requisição POST de logout é realizada automaticamente, encerrando o processo de execução do script e finalizando a automação.
---

### 👨‍💻 Contato

- **Nome:** Júlio Silva | Analista de Dados
- **E-mail:** Para qualquer dúvida ou colaboração, sinta-se à vontade para me enviar um e-mail em: <strong><a href="mailto:juliocss044@gmail.com.br">juliocss044@gmail.com.br</a></strong>



