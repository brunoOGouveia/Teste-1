import streamlit as st
import sqlite3
import datetime

# --- Funções para o Banco de Dados ---
def inicializar_banco_de_dados():
    conexao = sqlite3.connect('fornecedores.db')
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            nome TEXT NOT NULL UNIQUE,
            dados_pagamento TEXT NOT NULL
        )
    """)
    conexao.commit()
    conexao.close()

def buscar_fornecedores(termo_busca=""):
    conexao = sqlite3.connect('fornecedores.db')
    cursor = conexao.cursor()
    if termo_busca:
        cursor.execute("SELECT nome, dados_pagamento FROM fornecedores WHERE nome LIKE ? ORDER BY nome", (f"%{termo_busca}%",))
    else:
        cursor.execute("SELECT nome, dados_pagamento FROM fornecedores ORDER BY nome")
    fornecedores = cursor.fetchall()
    conexao.close()
    return fornecedores

def adicionar_fornecedor(nome, dados_pagamento):
    conexao = sqlite3.connect('fornecedores.db')
    cursor = conexao.cursor()
    try:
        cursor.execute("INSERT INTO fornecedores (nome, dados_pagamento) VALUES (?, ?)", (nome, dados_pagamento))
        conexao.commit()
        st.success(f"Fornecedor '{nome}' adicionado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        st.error(f"O fornecedor '{nome}' já existe.")
        return False
    finally:
        conexao.close()

def atualizar_fornecedor(nome_antigo, nome_novo, dados_pagamento):
    conexao = sqlite3.connect('fornecedores.db')
    cursor = conexao.cursor()
    try:
        cursor.execute("UPDATE fornecedores SET nome = ?, dados_pagamento = ? WHERE nome = ?", (nome_novo, dados_pagamento, nome_antigo))
        conexao.commit()
        st.success(f"Fornecedor '{nome_novo}' atualizado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        st.error(f"O nome '{nome_novo}' já existe.")
        return False
    finally:
        conexao.close()

def remover_fornecedor(nome):
    conexao = sqlite3.connect('fornecedores.db')
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM fornecedores WHERE nome = ?", (nome,))
    conexao.commit()
    conexao.close()
    st.success(f"Fornecedor '{nome}' removido com sucesso!")


# --- Lógica da Aplicação ---
def gerar_mensagem(tipo_despesa, nome_fornecedor, data_pagamento, valor, centro_custos, dados_pagamento):
    # Correção: A formatação do valor e da data agora é feita corretamente aqui
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
    inicializar_banco_de_dados()
    
    st.info("Você está rodando a versão final e corrigida do aplicativo.")
    st.title("App de Solicitação de Pagamento")
    st.write("Preencha o formulário para gerar a sua solicitação.")

    if 'mensagem_gerada' not in st.session_state:
        st.session_state['mensagem_gerada'] = ""
    
    aba_formulario, aba_gerenciar = st.tabs(["Gerar Solicitação", "Gerenciar Fornecedores"])

    with aba_formulario:
        st.subheader("Formulário de Solicitação")

        centros_de_custos = ["Obra Alphaville II", "Obra Terras Alphaville II", "Fabrica"]

        tipo_despesa = st.text_input("Tipo de despesa:")
        
        fornecedores_nomes = [f[0] for f in buscar_fornecedores()]
        nome_fornecedor = st.selectbox("Fornecedor:", fornecedores_nomes)
        
        # O widget de data já é exibido corretamente no Streamlit
        data_pagamento = st.date_input("Data de pagamento:", datetime.date.today())
        
        valor = st.number_input("Valor:", min_value=0.00, format="%.2f")
        
        centro_custos = st.selectbox("Centro de custos:", centros_de_custos)

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
        
        # Correção: Adiciona um campo de pesquisa para filtrar a lista de fornecedores
        termo_busca = st.text_input("Pesquisar fornecedor:", key="search_input")
        
        if st.button("Pesquisar"):
            fornecedores_filtrados = buscar_fornecedores(termo_busca)
            st.session_state['fornecedores_list'] = fornecedores_filtrados
        else:
            if 'fornecedores_list' not in st.session_state:
                st.session_state['fornecedores_list'] = buscar_fornecedores()

        st.write("---")
        st.write("Fornecedores Cadastrados:")
        # Correção: Exibe a lista de fornecedores filtrada ou completa
        for nome, dados in st.session_state['fornecedores_list']:
            st.write(f"**{nome}** | Dados: {dados}")
        st.write("---")

        st.subheader("Adicionar, Editar ou Excluir Fornecedor")
        
        # Correção: Usamos um seletor para permitir que o usuário escolha um fornecedor para editar/excluir
        fornecedores_nomes = [f[0] for f in buscar_fornecedores()]
        fornecedor_selecionado = st.selectbox("Selecione um fornecedor:", [""] + fornecedores_nomes, key="select_supplier")
        
        dados_salvos = [f[1] for f in buscar_fornecedores() if f[0] == fornecedor_selecionado]
        dados_salvos = dados_salvos[0] if dados_salvos else ""
        
        nome_novo = st.text_input("Nome:", value=fornecedor_selecionado, key="edit_name")
        dados_pagamento = st.text_input("Dados de Pagamento:", value=dados_salvos, key="edit_data")

        col_botoes1, col_botoes2, col_botoes3 = st.columns(3)
        with col_botoes1:
            if st.button("Adicionar"):
                if nome_novo and dados_pagamento:
                    adicionar_fornecedor(nome_novo, dados_pagamento)
                else:
                    st.error("Nome e dados de pagamento são obrigatórios!")
        
        with col_botoes2:
            if st.button("Salvar Alterações"):
                if fornecedor_selecionado and nome_novo and dados_pagamento:
                    atualizar_fornecedor(fornecedor_selecionado, nome_novo, dados_pagamento)
                else:
                    st.error("Nenhum fornecedor selecionado ou campos estão vazios!")

        with col_botoes3:
            if st.button("Remover"):
                if fornecedor_selecionado:
                    remover_fornecedor(fornecedor_selecionado)
                else:
                    st.error("Selecione um fornecedor para remover.")

if __name__ == '__main__':
    main()