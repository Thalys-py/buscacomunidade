
import os
print("Diretório atual:", os.getcwd())

from flask import Flask, render_template, request
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)


def carregar_dados():
    try:
        scope = ["https://spreadsheets.google.com/feeds", 
                 "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file", 
                 "https://www.googleapis.com/auth/drive"]

import json
import os

credenciais_dict = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciais_dict, scope)

        client = gspread.authorize(creds)

        # Aqui está o ID correto (não o link inteiro!)
        sheet_id = "1CLyIY19Lkc5i_5nOz1Z5FRTvhqt-Z-kJcvZaxPs_2Lw"
        sheet = client.open_by_key(sheet_id)

        # 🔍 Isso vai listar as abas disponíveis
        print([w.title for w in sheet.worksheets()])

        # Tente acessar sua aba (com nome correto depois de ver o print)
        aba = sheet.worksheet("Respostas ao formulário 1")

        dados = aba.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        print(f"Erro ao carregar dados da planilha: {e}")
        return pd.DataFrame()



@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    df = carregar_dados()

    if not df.empty and query:
        df_filtrado = df[df.apply(lambda row: query in str(row).lower(), axis=1)]
    else:
        df_filtrado = df

    return render_template('index.html', tabela=df_filtrado.to_dict(orient='records'), consulta=query)

if __name__ == '__main__':
    app.run(debug=True)

