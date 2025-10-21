import streamlit as st
import matplotlib.pyplot as plt
ARQUIVO_DADOS = "dados_alunos.txt"
def salvar_aluno(nome, serie, nota1, nota2, nota3):
    with open(ARQUIVO_DADOS, "a") as f:
        f.write(f"{nome},{serie},{nota1},{nota2},{nota3}\n")
def carregar_dados():
    alunos = []
    try:
        with open(ARQUIVO_DADOS, "r") as f:
            for linha in f:
                partes = linha.strip().split(",")
                if len(partes) == 5:
                    nome, serie, n1, n2, n3 = partes
                    alunos.append({
                        "nome": nome,
                        "serie": serie,
                        "notas": [float(n1), float(n2), float(n3)],
                        "media": (float(n1) + float(n2) + float(n3)) / 3
                    })
    except FileNotFoundError:
        pass
    return alunos
st.title("Sistema de Notas")
st.header("Cadastrar Aluno")

with st.form("form_cadastro"):
    nome = st.text_input("Nome do aluno")
    serie = st.text_input("Série")
    nota1 = st.number_input("Nota 1", min_value=0.0, max_value=10.0, step=0.1)
    nota2 = st.number_input("Nota 2", min_value=0.0, max_value=10.0, step=0.1)
    nota3 = st.number_input("Nota 3", min_value=0.0, max_value=10.0, step=0.1)
    submit = st.form_submit_button("Salvar")

    if submit:
        if nome and serie:
            salvar_aluno(nome, serie, nota1, nota2, nota3)
            st.success("Aluno cadastrado com sucesso!")
        else:
            st.error("Preencha todos os campos!")
alunos = carregar_dados()
if alunos:
    st.header("Relatórios")
    st.subheader("Média geral por série")
    series = {}
    for aluno in alunos:
        s = aluno["serie"]
        if s not in series:
            series[s] = []
        series[s].append(aluno["media"])

    for s, medias in series.items():
        media_geral = sum(medias) / len(medias)
        st.write(f"Série **{s}**: Média geral = **{media_geral:.2f}**")
    st.subheader("Gráfico de distribuição das médias por série")
    series_disponiveis = list(series.keys())
    serie_selecionada = st.selectbox("Escolha a série", series_disponiveis)

    if serie_selecionada:
        medias = series[serie_selecionada]
        nomes = [aluno["nome"] for aluno in alunos if aluno["serie"] == serie_selecionada]

        fig, ax = plt.subplots()
        ax.bar(nomes, medias, color="skyblue")
        ax.set_title(f"Médias Finais - Série {serie_selecionada}")
        ax.set_ylabel("Média")
        ax.set_xlabel("Aluno")
        plt.xticks(rotation=45)
        st.pyplot(fig)
else:
    st.info("Nenhum aluno cadastrado ainda.")