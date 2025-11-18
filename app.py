import streamlit as st
import sqlite3
import os
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Pokedex",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("POKEDEX COMPLETA")
st.subheader("Daniel Costa, Matheus Willian e Kauã Guedes 2°D")
st.markdown("---")

def init_database():
    """Inicializa o banco de dados SQLite com as tabelas necessárias"""
    conn = sqlite3.connect('pokedex.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS treinadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pokemons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo1 TEXT NOT NULL,
            tipo2 TEXT,
            treinador_id INTEGER NOT NULL,
            imagem_path TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (treinador_id) REFERENCES treinadores (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_upload_folder():
    """Cria o diretório para armazenar as imagens"""
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

def get_connection():
    """Retorna uma conexão com o banco de dados"""
    return sqlite3.connect('pokedex.db')

def get_all_treinadores():
    """Retorna todos os treinadores cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cidade FROM treinadores ORDER BY nome")
    treinadores = cursor.fetchall()
    conn.close()
    return treinadores

def get_treinadores_dict():
    """Retorna dicionário de treinadores para selectbox"""
    treinadores = get_all_treinadores()
    return {f"{t[1]} - {t[2]}": t[0] for t in treinadores}

def insert_treinador(nome, cidade):
    """Insere um novo treinador no banco"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO treinadores (nome, cidade) VALUES (?, ?)",
            (nome, cidade)
        )
        conn.commit()
        return True, "Treinador cadastrado com sucesso!"
    except sqlite3.Error as e:
        return False, f"Erro ao cadastrar treinador: {e}"
    finally:
        conn.close()

def salvar_imagem(uploaded_file):
    """Salva a imagem no diretório uploads e retorna o caminho"""
    if uploaded_file is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}_{uploaded_file.name}"
        filepath = os.path.join("uploads", filename)
        
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filepath
    return None

def insert_pokemon(nome, tipo1, tipo2, treinador_id, imagem_path):
    """Insere um novo Pokémon no banco"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO pokemons 
            (nome, tipo1, tipo2, treinador_id, imagem_path) 
            VALUES (?, ?, ?, ?, ?)""",
            (nome, tipo1, tipo2, treinador_id, imagem_path)
        )
        conn.commit()
        return True, "Pokémon cadastrado com sucesso!"
    except sqlite3.Error as e:
        return False, f"Erro ao cadastrar Pokémon: {e}"
    finally:
        conn.close()

def get_all_pokemons():
    """Retorna todos os Pokémon com informações dos treinadores"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.nome, p.tipo1, p.tipo2, p.imagem_path,
               t.nome as treinador_nome, t.cidade as treinador_cidade,
               p.data_cadastro
        FROM pokemons p
        JOIN treinadores t ON p.treinador_id = t.id
        ORDER BY p.nome
    """)
    pokemons = cursor.fetchall()
    conn.close()
    return pokemons

def get_estatisticas():
    """Retorna estatísticas do sistema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM treinadores")
    total_treinadores = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pokemons")
    total_pokemons = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT t.nome, COUNT(p.id) as total 
        FROM treinadores t 
        LEFT JOIN pokemons p ON t.id = p.treinador_id 
        GROUP BY t.id 
        ORDER BY total DESC 
        LIMIT 1
    """)
    treinador_mais_pokemons = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_treinadores': total_treinadores,
        'total_pokemons': total_pokemons,
        'treinador_mais_pokemons': treinador_mais_pokemons
    }

init_database()
create_upload_folder()

st.sidebar.title("Navegação")
menu = st.sidebar.radio(
    "Selecione uma opção:",
    ["Página Inicial", "Gerenciar Treinadores", "Cadastrar Pokémon", "Visualizar Pokédex", "Estatísticas"]
)

st.sidebar.markdown("---")

if menu == "Página Inicial":
    st.header("Bem-vindo à Pokédex Completa!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Sobre o Projeto
        
        Este sistema foi desenvolvido como parte da disciplina de **Desenvolvimento de Sistemas**
        e transforma uma Pokédex simples em um sistema robusto que:
        
        - **Gerencia Treinadores** 
        - **Cadastra Pokémon**   
        - **Associa Pokémon a Treinadores** 
        - **Armazena e exibe imagens** 
        - **Apresenta relatórios completos** 
        
        ### Funcionalidades Principais
        
        1. **Gerenciamento de Treinadores**
           - Cadastro de novos treinadores
           - Registro da cidade de origem
           - Listagem completa
        
        2. **Cadastro de Pokémon** 
           - Associação obrigatória com treinador
           - Upload de imagem
           - Registro de tipos (Tipo 1 e Tipo 2)
        
        3. **Visualização da Pokédex**
           - Listagem completa de Pokémon
           - Exibição de imagens
           - Informações do treinador responsável
        """)
    
    with col2:
        stats = get_estatisticas()
        
        st.success("### Dashboard Rápido")
        st.metric("Treinadores Cadastrados", stats['total_treinadores'])
        st.metric("Pokémon Registrados", stats['total_pokemons'])
        
        if stats['treinador_mais_pokemons']:
            st.info(f"**Treinador com mais Pokémon:**\n{stats['treinador_mais_pokemons'][0]} ({stats['treinador_mais_pokemons'][1]})")
        
        st.markdown("---")
        st.warning("""
        **Atenção**
        
        Para cadastrar Pokémon, é necessário ter pelo menos **um treinador** cadastrado no sistema.
        """)

elif menu == "Gerenciar Treinadores":
    st.header("Gerenciamento de Treinadores")
    
    tab1, tab2 = st.tabs(["Cadastrar Novo Treinador", "Lista de Treinadores Cadastrados"])
    
    with tab1:
        st.subheader("Cadastro de Treinador")
        
        with st.form("form_treinador", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input(
                    "**Nome do Treinador**",
                    placeholder="Ex: Ash Ketchum",
                    help="Digite o nome completo do treinador"
                )
            
            with col2:
                cidade = st.text_input(
                    "**Cidade de Origem**", 
                    placeholder="Ex: Cidade de Pallet",
                    help="Cidade natal do treinador"
                )
            
            submitted = st.form_submit_button("Cadastrar Treinador", use_container_width=True)
            
            if submitted:
                if nome.strip() and cidade.strip():
                    success, message = insert_treinador(nome.strip(), cidade.strip())
                    if success:
                        st.success(f"{message}")
                    else:
                        st.error(f"{message}")
                else:
                    st.warning("Preencha todos os campos obrigatórios!")
    
    with tab2:
        st.subheader("Treinadores Cadastrados")
        
        treinadores = get_all_treinadores()
        
        if treinadores:
            df_treinadores = pd.DataFrame(
                treinadores,
                columns=['ID', 'Nome', 'Cidade']
            )
            
            st.dataframe(
                df_treinadores,
                use_container_width=True,
                hide_index=True
            )
            
            st.subheader("Estatísticas por Treinador")
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.nome, t.cidade, COUNT(p.id) as total_pokemons
                FROM treinadores t
                LEFT JOIN pokemons p ON t.id = p.treinador_id
                GROUP BY t.id
                ORDER BY total_pokemons DESC
            """)
            stats_treinadores = cursor.fetchall()
            conn.close()
            
            for treinador in stats_treinadores:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{treinador[0]}**")
                with col2:
                    st.write(f"_{treinador[1]}_")
                with col3:
                    st.metric("Pokémon", treinador[2])
                
                st.progress(min(treinador[2] / 10, 1.0) if treinador[2] > 0 else 0)
        else:
            st.info("""
            ## Nenhum treinador cadastrado ainda!
            
            Use a aba **Cadastrar Novo Treinador** para adicionar o primeiro treinador ao sistema.
            """)

elif menu == "Cadastrar Pokémon":
    st.header("Cadastrar Novo Pokémon")
    
    treinadores_dict = get_treinadores_dict()
    
    if not treinadores_dict:
        st.error("""
        ## Atenção Necessária!
        
        **É necessário cadastrar pelo menos um treinador antes de registrar Pokémon!**
        
        ### Próximos passos:
        1. Vá para **Gerenciar Treinadores**
        2. Cadastre um treinador usando o formulário
        3. Volte para esta página para cadastrar Pokémon
        
        Sem treinadores cadastrados, não é possível associar Pokémon!
        """)
    else:
        with st.form("form_pokemon", clear_on_submit=True):
            st.subheader("Informações do Pokémon")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nome_pokemon = st.text_input(
                    "**Nome do Pokémon**",
                    placeholder="Ex: Pikachu",
                    help="Nome do Pokémon"
                )
                
                tipo1 = st.text_input(
                    "**Tipo Primário (Tipo 1)**",
                    placeholder="Ex: Elétrico",
                    help="Tipo principal do Pokémon"
                )
                
                tipo2 = st.text_input(
                    "**Tipo Secundário (Tipo 2)**",
                    placeholder="Ex: Aço (opcional)",
                    help="Tipo secundário (deixe em branco se não tiver)"
                )
            
            with col2:
                treinador_options = list(treinadores_dict.keys())
                treinador_selecionado = st.selectbox(
                    "**Treinador Responsável**",
                    options=treinador_options,
                    help="Selecione o treinador responsável por este Pokémon",
                    index=0
                )
                treinador_id = treinadores_dict[treinador_selecionado]
                
                uploaded_file = st.file_uploader(
                    "**Upload da Imagem do Pokémon**",
                    type=['png', 'jpg', 'jpeg', 'gif'],
                    help="Faça o upload de uma imagem do Pokémon (PNG, JPG, JPEG, GIF)"
                )
                
                if uploaded_file is not None:
                    st.image(uploaded_file, caption="Pré-visualização da Imagem", width=200)
            
            submitted = st.form_submit_button("Cadastrar Pokémon", use_container_width=True)
            
            if submitted:

                if not nome_pokemon.strip():
                    st.error("O nome do Pokémon é obrigatório!")
                elif not tipo1.strip():
                    st.error("O tipo primário é obrigatório!")
                elif not treinador_selecionado:
                    st.error("A seleção do treinador é obrigatória!")
                elif not uploaded_file:
                    st.error("O upload de imagem é obrigatório!")
                else:

                    imagem_path = salvar_imagem(uploaded_file)
                    
                    if imagem_path:
                        success, message = insert_pokemon(
                            nome_pokemon.strip(),
                            tipo1.strip(),
                            tipo2.strip() if tipo2.strip() else None,
                            treinador_id,
                            imagem_path
                        )
                        
                        if success:
                            st.success(f"{message}")
                            st.balloons()
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.info(f"""
                                **Resumo do Cadastro:**
                                - **Pokémon:** {nome_pokemon}
                                - **Tipo 1:** {tipo1}
                                - **Tipo 2:** {tipo2 if tipo2 else 'Nenhum'}
                                - **Treinador:** {treinador_selecionado}
                                """)
                            with col2:
                                if os.path.exists(imagem_path):
                                    st.image(imagem_path, caption=nome_pokemon, width=150)
                        else:
                            st.error(f"{message}")
                    else:
                        st.error("Erro ao salvar a imagem!")

elif menu == "Visualizar Pokédex":
    st.header("Pokédex Completa")
    
    pokemons = get_all_pokemons()
    
    if pokemons:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Pokémon", len(pokemons))
        with col2:
            tipos_unicos = len(set([p[2] for p in pokemons] + [p[3] for p in pokemons if p[3]]))
            st.metric("Tipos Diferentes", tipos_unicos)
        with col3:
            treinadores_unicos = len(set([p[5] for p in pokemons]))
            st.metric("Treinadores", treinadores_unicos)
        with col4:
            with_second_type = len([p for p in pokemons if p[3]])
            st.metric("Com 2 Tipos", with_second_type)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_nome = st.text_input("Filtrar por nome:", placeholder="Digite o nome do Pokémon...")
        with col2:
            tipos = sorted(list(set([p[2] for p in pokemons] + [p[3] for p in pokemons if p[3]])))
            filter_tipo = st.selectbox("Filtrar por tipo:", ["Todos"] + tipos)
        with col3:
            treinadores = sorted(list(set([p[5] for p in pokemons])))
            filter_treinador = st.selectbox("Filtrar por treinador:", ["Todos"] + treinadores)
        
        pokemons_filtrados = pokemons
        if filter_nome:
            pokemons_filtrados = [p for p in pokemons_filtrados if filter_nome.lower() in p[1].lower()]
        if filter_tipo != "Todos":
            pokemons_filtrados = [p for p in pokemons_filtrados if p[2] == filter_tipo or p[3] == filter_tipo]
        if filter_treinador != "Todos":
            pokemons_filtrados = [p for p in pokemons_filtrados if p[5] == filter_treinador]
        
        st.write(f"**Mostrando {len(pokemons_filtrados)} de {len(pokemons)} Pokémon**")
        
        cols = st.columns(3)
        
        for idx, pokemon in enumerate(pokemons_filtrados):
            with cols[idx % 3]:
                with st.container():
                    st.markdown("---")
                    
                    st.subheader(f"#{pokemon[0]:03d} {pokemon[1]}")
                    
                    if pokemon[4] and os.path.exists(pokemon[4]):
                        st.image(pokemon[4], use_container_width=True)
                    else:
                        st.warning("Imagem não encontrada")

                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.success(f"**{pokemon[2]}**")
                    with col_t2:
                        if pokemon[3]:
                            st.info(f"**{pokemon[3]}**")
                    
                    st.write(f"**Treinador:** {pokemon[5]}")
                    st.write(f"**Cidade:** {pokemon[6]}")
                    st.caption(f"Cadastrado em: {pokemon[7][:10]}")
                    
                    st.markdown("")
    else:
        st.info("""
        ## Nenhum Pokémon cadastrado ainda!
        
        ### Para começar:
        1. Vá para **Gerenciar Treinadores** e cadastre um treinador
        2. Depois use **Cadastrar Pokémon** para adicionar seu primeiro Pokémon
        3. Volte aqui para visualizar toda a Pokédex!
        
        Lembre-se: É necessário ter treinadores cadastrados antes de adicionar Pokémon.
        """)

elif menu == "Estatísticas":
    st.header("Estatísticas do Sistema")
    
    stats = get_estatisticas()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Métricas Principais")
        st.metric("Total de Treinadores", stats['total_treinadores'])
        st.metric("Total de Pokémon", stats['total_pokemons'])
        
        if stats['treinador_mais_pokemons']:
            st.info(f"""
            **Treinador Destaque:**
            {stats['treinador_mais_pokemons'][0]}
            com {stats['treinador_mais_pokemons'][1]} Pokémon
            """)
    
    with col2:
        st.subheader("Distribuição")
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.nome, COUNT(p.id) as total
            FROM treinadores t
            LEFT JOIN pokemons p ON t.id = p.treinador_id
            GROUP BY t.id
            ORDER BY total DESC
        """)
        data_treinadores = cursor.fetchall()
        conn.close()
        
        if data_treinadores:
            df = pd.DataFrame(data_treinadores, columns=['Treinador', 'Pokémon'])
            st.bar_chart(df.set_index('Treinador'))
    
    st.subheader("Distribuição por Tipos")
    
    pokemons = get_all_pokemons()
    if pokemons:
        tipos = []
        for p in pokemons:
            tipos.append(p[2])
            if p[3]:
                tipos.append(p[3])
        
        from collections import Counter
        tipo_counts = Counter(tipos)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Frequência por Tipo:**")
            for tipo, count in tipo_counts.most_common():
                st.write(f"- {tipo}: {count}")
        with col2:
            df_tipos = pd.DataFrame(list(tipo_counts.items()), columns=['Tipo', 'Quantidade'])
            st.bar_chart(df_tipos.set_index('Tipo'))

st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.caption("**Pokemon Company**")
with footer_col2:
    st.caption("**Netendo nada**")
with footer_col3:
    st.caption("**Roblox é bom**")
if 'init_message' not in st.session_state:
    st.session_state.init_message = True
    st.toast("Sistema inicializado com sucesso!")
