import streamlit as st
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import pandas as pd
import datetime

# --- Conexão com o Google Sheets ---
try:
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = gc.open("Fornecedores")
    worksheet = sh.sheet1
except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")
    st.stop()

# --- Funções para o Banco de Dados (agora usando Google Sheets) ---
def buscar_fornecedores(termo_busca=""):
    df = get_as_dataframe(worksheet)
    if not termo_busca:
        return df.values.tolist()
    
    df_filtrado = df[df['nome'].str.contains(termo_busca, case=False, na=False)]
    return df_filtrado.values.tolist()

def adicionar_fornecedor(nome, dados_pagamento):
    df = get_as_dataframe(worksheet)
    if nome in df['nome'].values:
        st.error(f"O fornecedor '{nome}' já existe.")
        return False

    nova_linha = pd.DataFrame([{'nome': nome, 'dados_pagamento': dados_pagamento}])
    df = pd.concat([df, nova_linha], ignore_index=True)
    set_with_dataframe(worksheet, df)
    st.success(f"Fornecedor '{nome}' adicionado com sucesso!")
    return True

def atualizar_fornecedor(nome_antigo, nome_novo, dados_pagamento):
    df = get_as_dataframe(worksheet)
    if nome_novo != nome_antigo and nome_novo in df['nome'].values:
        st.error(f"O nome '{nome_novo}' já existe.")
        return False
    
    df.loc[df['nome'] == nome_antigo, 'nome'] = nome_novo
    df.loc[df['nome'] == nome_antigo, 'dados_pagamento'] = dados_pagamento
    set_with_dataframe(worksheet, df)
    st.success(f"Fornecedor '{nome_novo}' atualizado com sucesso!")
    return True

def remover_fornecedor(nome):
    df = get_as_dataframe(worksheet)
    df = df[df['nome'] != nome]
    set_with_dataframe(worksheet, df)
    st.success(f"Fornecedor '{nome}' removido com sucesso!")


# --- Lógica da Aplicação ---
def gerar_mensagem(tipo_despesa, nome_fornecedor, data_pagamento, valor, centro_custos, dados_pagamento):
    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    data_formatada = data_pagamento.strftime("%d / %m / %Y")

    mensagem_final = f"""
--- Solicitação de Pagamento ---

Tipo de despesa: {tipo_despesa}
Data de pagamento: {data_formatada}
Centro de custos: {centro_custos}
Valor: {valor_formatado}
Dados para pagamento: {dados_pagamento}
"""
    st.session_state['mensagem_gerada'] = mensagem_final

def main():
    st.title("App de Solicitação de Pagamento")
    st.write("Preencha o formulário para gerar a sua solicitação.")

    if 'mensagem_gerada' not in st.session_state:
        st.session_state['mensagem_gerada'] = ""
    
    aba_formulario, aba_gerenciar = st.tabs(["Gerar Solicitação", "Gerenciar Fornecedores"])

    with aba_formulario:
        st.subheader("Formulário de Solicitação")

        centros_de_custos = ["Obra Alphaville II", "Obra Terras Alphaville II", "Fabrica"]
        
        fornecedores_nomes = [f[0] for f in buscar_fornecedores()]
        nome_fornecedor = st.selectbox("Fornecedor:", fornecedores_nomes)
        
        data_pagamento = st.date_input("Data de pagamento:", datetime.date.today())
        
        valor = st.number_input("Valor:", min_value=0.00, format="%.2f")
        
        centro_custos = st.selectbox("Centro de custos:", centros_de_custos)

        tipo_despesa = st.text_input("Tipo de despesa:")
        
        if st.button("Gerar Mensagem"):
            if not tipo_despesa or not nome_fornecedor or not data_pagamento or not valor or not centro_custos:
                st.error("Todos os campos devem ser preenchidos!")
            else:
                dados_pagamento = [f[1] for f in buscar_fornecedores() if f[0] == nome_fornecedor][0]
                gerar_mensagem(tipo_despesa, nome_fornecedor, data_pagamento, valor, centro_custos, dados_pagamento)
        
        if st.session_state['mensagem_gerada']:
            st.subheader("Mensagem Pronta")
            st.code(st.session_state['mensagem_gerada'], language="text")
            st.info("Copie o texto acima.")

    with aba_gerenciar:
        st.subheader("Gerenciar Fornecedores")
        
        termo_busca = st.text_input("Pesquisar fornecedor:", key="search_input")
        
        if st.button("Pesquisar"):
            fornecedores_filtrados = buscar_fornecedores(termo_busca)
            st.session_state['fornecedores_list'] = fornecedores_filtrados
        else:
            if 'fornecedores_list' not in st.session_state:
                st.session_state['fornecedores_list'] = buscar_fornecedores()

        st.write("---")
        st.write("Fornecedores Cadastrados:")
        for nome, dados in st.session_state['fornecedores_list']:
            st.write(f"**{nome}** | Dados: {dados}")
        st.write("---")

        st.subheader("Adicionar, Editar ou Excluir Fornecedor")
        
        fornecedores_nomes = [f[0] for f in buscar_fornecedores()]
        fornecedor_selecionado = st.selectbox("Selecione um fornecedor:", [""] + fornecedores_nomes, key="select_supplier")
        
        dados_salvos_list = [f[1] for f in buscar_fornecedores() if f[0] == fornecedor_selecionado]
        dados_salvos = dados_salvos_list[0] if dados_salvos_list else ""
        
        nome_novo = st.text_input("Nome:", value=fornecedor_selecionado, key="edit_name")
        dados_pagamento = st.text_input("Dados de Pagamento:", value=dados_salvos, key="edit_data")

        col_botoes1, col_botoes2, col_botoes3 = st.columns(3)
        with col_botoes1:
            if st.button("Adicionar"):
                if nome_novo and dados_pagamento:
                    adicionar_
