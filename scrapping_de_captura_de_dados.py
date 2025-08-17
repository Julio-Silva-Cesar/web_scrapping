
#[01] - ***Definição das bibliotecas necessárias***

%pip install openpyxl google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client gspread drive pandas_gbq gspread_dataframe -q

dbutils.library.restartPython() -- Restart do Ambiente python no Databricks!

#[02] - ***Integração com o google Drive***

import pandas as pd
from datetime import datetime
from datetime import timedelta
import gspread
from google.oauth2.service_account import Credentials
import drive
from time import sleep

#[03] - Definir os escopos da API do Google Sheets e Google Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

#[3.1] - Caminho para o arquivo JSON da conta de serviço
SERVICE_ACCOUNT_FILE = 'service_account_drive'

#[3.2] - Autenticar usando as credenciais da conta de serviço
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

#[3.3] - Instanciamento do client do Drive
client = gspread.authorize(credentials)

#[04] - ***Integração com o sistema WEB - Requisição POST de login***

-- credenciais secrets sistema

login    = dbutils.secrets.get(scope='JCtiflux', key='logintiflux')
password = dbutils.secrets.get(scope='JCtiflux', key='senhatiflux')

# COMMAND ----------

##***Geração de Token tmp - token de início de seção [login 01]***

# COMMAND ----------

# Função de criação de tokens tmp e otp

import requests

def login_tiflux(email, password):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
    }

    json_data = {
        'user': {
            'email': login,
            'password': password,
            'remember_me': True,
        },
    }

    response = requests.post('url_de_post', headers=headers, json=json_data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro no login: {response.status_code}, {response.text}")
        return None

# Chamada da função 
response_data = login_tiflux(login, password)
cod_tmp = response_data['otp_tmp']

##***Captura de código otp via g-mail API [login 02]***
    # Encaminhamento de preenchimento automático para a planilha mestra de forma acionar o script
    # Captura do código otp via Java Script
    # Usar o ID da planilha em vez do nome

spreadsheet_id = 'id_planilha_google'
spreadsheet = client.open_by_key(spreadsheet_id)
worksheet = spreadsheet.worksheet("Emails")

###***Criação de gatilho de acionamento para o APP Script***

# COMMAND ----------

data = {'TAG':['gatilho de atualização, atualize aí'],'Nome':['Júlio']}
gatilho = pd.DataFrame(data)

# COMMAND ----------
from gspread_dataframe import set_with_dataframe
set_with_dataframe(worksheet, gatilho)

###***Integração com planilha no drive e captura do Código [otp]***

import time
sleep(15)
# Ler dados da worksheet
data = worksheet.get_all_values()
# Converter a lista de dicionários em um DataFrame
ss = pd.DataFrame(data[1:], columns=data[0])
codigo_otp = ss['Código de Segurança'].iloc[0]

# ***IMPLEMENTAÇÃO DOS CÓDIGOS NA API SECUNDÁRIA DE VERIFICAÇÃO***

sleep(15)
import requests

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'undefined',
    'content-type': 'application/json',
}

json_data = {
    'email': 'meu_email',
    'otp_tmp': f'{cod_tmp}',
    'otp': f'{codigo_otp}',
}

response1 = requests.post('requisição_de_post', headers=headers, json=json_data)

# COMMAND ----------

# ***CAPTURA DO TOKEN DE AUTHORIZATION***

# COMMAND ----------

token_relatorio = response1.headers['authorization']

# COMMAND ----------

###***EXTRAÇÃO DOS RELATÓRIOS***

#Criando o range de coleta

hoje = pd.to_datetime(datetime.now().date()) # Data de Hoje

# Calcular o range de coleta

abertura = hoje - timedelta(days=180)

# COMMAND ----------

hoje = hoje.strftime('%Y-%m-%d')
abertura = abertura.strftime('%Y-%m-%d')

###***REQUISIÇÃO DE CAPTURA DOS DADOS***

# COMMAND ----------

#***Criação de Captura do Token de Validação***

# Definição do cabeçalho
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': f'{token_relatorio}',
    'content-type': 'application/json',
}

# Inicializa a variável para armazenar os resultados
todos_os_tickets = []

# Página inicial
pagina_atual = 1  

while True:  # Loop infinito até que os dados retornem vazios
    # Monta o JSON da requisição
    json_data = {
        'filter': {
            'ticket_title': '',
            'ticket_number': '',
            'start_date': f'{abertura}T00:00:00-03:00',
            'end_date': f'{hoje}T24:59:59-03:00',
            'requestor_name': '',
            'stage_ids': '',
            'client_ids': '1232815,1236071,1261709,1286374,17803',
            'date_type': 'opened_between',
            'mail_header': '',
        },
        'page': pagina_atual,
        'order_by': '',
    }

    # Faz a requisição
    response = requests.post(
        'requisição_de_post_payload',
        headers=headers,
        json=json_data,
    )

    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        
        # Captura os tickets retornados nesta página
        tickets_pagina = data.get('tickets', [])

        # Se não houver mais tickets, paramos a iteração
        if not tickets_pagina:
            print(f'Nenhum dado encontrado na página {pagina_atual}, encerrando extração.')
            break  

        # Adiciona os tickets extraídos à lista geral
        todos_os_tickets.extend(tickets_pagina)

        print(f'Página {pagina_atual} extraída com sucesso!')

        # Passa para a próxima página
        pagina_atual += 1
    else:
        print(f'Erro na requisição da página {pagina_atual}: {response.status_code}')
        break  # Para a execução em caso de erro

# Converte a lista para um DataFrame
if todos_os_tickets:
    df_tickets = pd.json_normalize(todos_os_tickets)
    print(f'Total de {len(df_tickets)} registros extraídos!')
else:
    print('Nenhum registro encontrado!')

# ***ENCAMINHAMENTO E TRANSFORMAÇÃO DOS DADOS***

# COMMAND ----------

from datetime import datetime
import pytz

# COMMAND ----------

if df_tickets.empty:
    print('Nenhum registro encontrado!')
else:
    df_tickets.rename(columns={'id': 'ID', 'ticket_number': 'Numero_Ticket', 'title':'Titulo_Ticket','requestor_email':'Email_Solicitante' ,'requestor_name':'Solicitante', 'stage_name': 'Etapa', 
                               'created_at': 'Data_Abertura', 'solved_in_time': 'Data_Fechamento', 'desk_name':'Mesa', 'client_name':'Cliente','responsible_name':'Nome_Responsavel','status_name':'status_atual',
                               'stage_name':'Estagio'}, inplace=True)


    df_tickets['Estagio'] = df_tickets['Estagio'].str.strip()

    dictionari_status1 = {'first_status_name':'Aberta',
                          'canceled_status_name':'Cancelada',
                          'last_status_name':'Fechado'}
    
    dictionari_status2 = {'first_stage_name':'Aberta',
                          'last_stage_name':'Fechado'}
    
    df_tickets['status_atual'] = df_tickets['status_atual'].map(dictionari_status1).fillna(df_tickets['status_atual'])
    df_tickets['Estagio'] = df_tickets['Estagio'].map(dictionari_status2).fillna(df_tickets['Estagio'])

    tz = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz) 
    agora_formatado = agora.strftime('%Y-%m-%d %H:%M:%S') 
    df_tickets['atualizacao'] = agora_formatado

    
    # Encaminhando a Tabela ao Bigquery
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account"
    table_id = 'tabela_bigquery' 
    project_id = 'projeto_bigquery'

    df_tickets.to_gbq(destination_table=table_id, project_id=project_id, if_exists='replace')

    print(f'{table_id} enviada com Sucesso!')

# MAGIC ***REALIZAÇÃO DO LOGOUT***

# COMMAND ----------

import requests
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': f'{token_relatorio}',
}

params = {
    'id': '670842',
}

response4 = requests.delete('requisição_delete_sesion', params=params, headers=headers)

# COMMAND ----------

if response4.status_code == 204:
    print('Logout realizado com sucesso!')
else:
    print('Erro no logout:', response4.status_code)
