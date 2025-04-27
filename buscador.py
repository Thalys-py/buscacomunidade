import os
import json
import pandas as pd
import gspread
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Função para carregar os dados da planilha
def carregar_dados():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]

        credenciais_dict = json.loads(os.environ['GOOGLE_CREDENTIALS_JSON'])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciais_dict, scope)
        client = gspread.authorize(creds)

        # Conectar-se à planilha pelo ID
        sheet_id = "1CLyIY19Lkc5i_5nOz1Z5FRTvhqt-Z-kJcvZaxPs_2Lw"
        sheet = client.open_by_key(sheet_id)
        
        # Pega a aba correta
        aba = sheet.worksheet("Respostas ao formulário 1")

        # Carregar os dados para um DataFrame
        dados = aba.get_all_records()
        df = pd.DataFrame(dados)

        # Exibir colunas para depuração
        print("Colunas no DataFrame:", df.columns.tolist())

        # Corrige possíveis espaços nos nomes das colunas
        df.columns = df.columns.str.strip()

        # Renomear colunas, se necessário (ajuste conforme o nome real na planilha)
        column_mapping = {
            'Categoria': 'Categoria do Negócio',  # Substitua pelo nome real, se diferente
            # Adicione outras renomeações, se necessário
        }
        df = df.rename(columns=column_mapping)

        # Garantir que 'Categoria do Negócio' e 'Nome do Negócio' existam
        if 'Categoria do Negócio' not in df.columns:
            print("Aviso: Coluna 'Categoria do Negócio' não encontrada. Criando com valor padrão.")
            df['Categoria do Negócio'] = 'Sem Categoria'
        if 'Nome do Negócio' not in df.columns:
            print("Aviso: Coluna 'Nome do Negócio' não encontrada. Criando com valor padrão.")
            df['Nome do Negócio'] = 'Sem Nome'

        # Preencher valores nulos
        df['Categoria do Negócio'] = df['Categoria do Negócio'].fillna('Sem Categoria')
        df['Nome do Negócio'] = df['Nome do Negócio'].fillna('Sem Nome')

        return df
    except Exception as e:
        print(f"Erro ao carregar dados>Erro ao carregar dados da planilha: {e}")
        return pd.DataFrame()

@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    filtro_categoria = request.args.get('categoria', '')

    df = carregar_dados()

    # Calcular o número total de negócios cadastrados antes dos filtros
    total_registros = len(df)

    # Obter categorias únicas para o dropdown
    categorias = sorted(df['Categoria do Negócio'].dropna().unique()) if not df.empty else []

    # Filtragem
    if not df.empty:
        if query:
            df = df[df.apply(lambda row: query in str(row).lower(), axis=1)]
        if filtro_categoria:
            df = df[df['Categoria do Negócio'] == filtro_categoria]

    # Exibir número de resultados filtrados
    quantidade_resultados = len(df)
    print(f"Registros enviados ao template: {quantidade_resultados}")

    return render_template(
        'index.html',
        tabela=df.to_dict(orient='records'),
        consulta=query,
        categorias=categorias,
        categoria_selecionada=filtro_categoria,
        quantidade_resultados=quantidade_resultados,
        total_registros=total_registros  # Passando o total de registros para o template
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
