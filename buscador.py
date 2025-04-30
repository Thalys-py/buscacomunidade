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

        sheet_id = "1CLyIY19Lkc5i_5nOz1Z5FRTvhqt-Z-kJcvZaxPs_2Lw"
        sheet = client.open_by_key(sheet_id)
        aba = sheet.worksheet("Respostas ao formulário 1")

        dados = aba.get_all_records()
        df = pd.DataFrame(dados)

        print("Colunas no DataFrame:", df.columns.tolist())
        df.columns = df.columns.str.strip()

        column_mapping = {
            'Categoria': 'Categoria do Negócio',
        }
        df = df.rename(columns=column_mapping)

        if 'Categoria do Negócio' not in df.columns:
            print("Aviso: Coluna 'Categoria do Negócio' não encontrada. Criando com valor padrão.")
            df['Categoria do Negócio'] = 'Sem Categoria'
        if 'Nome do Negócio' not in df.columns:
            print("Aviso: Coluna 'Nome do Negócio' não encontrada. Criando com valor padrão.")
            df['Nome do Negócio'] = 'Sem Nome'

        df['Categoria do Negócio'] = df['Categoria do Negócio'].fillna('Sem Categoria')
        df['Nome do Negócio'] = df['Nome do Negócio'].fillna('Sem Nome')

        # ✅ Adicionando tratamento do campo "Verificado"
        if 'Verificado' in df.columns:
            df['Verificado'] = df['Verificado'].astype(str).str.strip().str.lower() == 'sim'
        else:
            df['Verificado'] = False

        return df
    except Exception as e:
        print(f"Erro ao carregar dados da planilha: {e}")
        return pd.DataFrame()
