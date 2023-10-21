import os
from flask import render_template, request, send_file
import pandas as pd

from app import app

UPLOAD_FOLDER = 'arquivos/uploads'  # Diretório para salvar os arquivos
CAMINHO_ARQUIVO_MODELO = "arquivos/padrao.xlsx"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    # Verifica se um arquivo foi enviado no formulário
    if 'arquivo' not in request.files:
        return "Nenhum arquivo foi enviado."

    file = request.files['arquivo']

    # Verifica se o nome do arquivo está vazio
    if file.filename == '':
        return render_template('index.html', erro="Nome do arquivo vazio.")

    # Verifica se o arquivo é um arquivo permitido (xlsx, xls ou csv)
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        return render_template('index.html', erro="Tipo de arquivo não permitido.")

    # Salva o arquivo no diretório de upload
    arquivo_enviado = os.path.join(UPLOAD_FOLDER, file.filename)
    
    file.save(arquivo_enviado)

    mensagem = "Arquivo '{}' foi enviado com sucesso!".format(file.filename)

    # Lê o arquivo modelo
    try:
        df_modelo = pd.read_excel(CAMINHO_ARQUIVO_MODELO)
    except Exception as e:
        return render_template('index.html', erro="Erro ao ler o arquivo modelo: " + str(e))

    # Lê o arquivo enviado pelo usuário
    try:
        if file.filename.endswith('.csv'):
            df_enviado = pd.read_csv(arquivo_enviado)
        else:
            df_enviado = pd.read_excel(arquivo_enviado)
    except Exception as e:
        return render_template('index.html', erro="Erro ao ler o arquivo enviado: " + str(e))

    # Obtém as colunas dos dois dataframes
    colunas_arquivo_modelo = df_modelo.columns.tolist()
    colunas_arquivo_enviado = df_enviado.columns.tolist()

    return render_template('upload.html', mensagem=mensagem, colunas_arquivo_modelo=colunas_arquivo_modelo, colunas_arquivo_enviado=colunas_arquivo_enviado, arquivo_enviado=arquivo_enviado)

@app.route('/arquivo-mesclado', methods=['POST'])
def arquivo_mesclado():
    # Receba os dados do formulário
    formulario = request.form

    # Lê o arquivo modelo
    try:
        df_modelo = pd.read_excel(CAMINHO_ARQUIVO_MODELO)
    except Exception as e:
        return render_template('index.html', erro="Erro ao ler o arquivo modelo: " + str(e))

    colunas_arquivo_modelo = df_modelo.columns.tolist()

    arquivo_enviado = formulario.get("arquivo_enviado")

    if not arquivo_enviado:
        return render_template('index.html', erro="Nenhum arquivo enviado.")

    # Lê o arquivo enviado pelo usuário
    try:
        if arquivo_enviado.endswith('.csv'):
            df_enviado = pd.read_csv(arquivo_enviado)
        else:
            df_enviado = pd.read_excel(arquivo_enviado)
    except Exception as e:
        return render_template('index.html', erro="Erro ao ler o arquivo enviado: " + str(e))

    # Crie um novo DataFrame para armazenar os dados mesclados
    df_mesclado = pd.DataFrame()

    # Crie um DataFrame separado para as colunas extras
    df_extras = pd.DataFrame()

    # Itera pelas colunas do arquivo modelo
    for coluna_modelo in colunas_arquivo_modelo:
        # Obtém a seleção feita pelo usuário para esta coluna
        selecao_usuario = formulario.get(coluna_modelo)

        # Verifica se a seleção não está vazia
        if selecao_usuario:
            # Adicione os dados da coluna do arquivo enviado à nova coluna
            df_mesclado[coluna_modelo] = df_enviado[selecao_usuario]
        else:
            df_mesclado[coluna_modelo] = ""

    # Verifica se há colunas extras no arquivo enviado pelo usuário
    colunas_extras = [coluna for coluna in df_enviado.columns if coluna not in colunas_arquivo_modelo]

    if colunas_extras:
        # Se houver colunas extras, adicione-as ao DataFrame de extras
        for coluna_extra in colunas_extras:
            df_extras[coluna_extra] = df_enviado[coluna_extra]

        # Salve o arquivo de colunas extras
        caminho_arquivo_extras = "arquivos/transformados/extras.xlsx"
        df_extras.to_excel(caminho_arquivo_extras, index=False)
    else:
        caminho_arquivo_extras = None

    # Salve o arquivo mesclado
    caminho_arquivo_mesclado = "arquivos/transformados/mesclado.xlsx"
    df_mesclado.to_excel(caminho_arquivo_mesclado, index=False)

    mensagem = "Arquivo mesclado foi criado com sucesso!"

    return render_template('sucesso.html', mensagem=mensagem, caminho_arquivo_mesclado=caminho_arquivo_mesclado, caminho_arquivo_extras=caminho_arquivo_extras)

@app.route('/download', methods=['GET'])
def download():
    caminho_arquivo_mesclado = request.args.get('caminho_arquivo_mesclado')
    caminho_arquivo_extras = request.args.get('caminho_arquivo_extras')

    if caminho_arquivo_mesclado is not None:
        return send_file(caminho_arquivo_mesclado, as_attachment=True)
    elif caminho_arquivo_extras is not None:
        return send_file(caminho_arquivo_extras, as_attachment=True)
    else:
        return render_template('index.html', erro="Caminho do arquivo não especificado.")
