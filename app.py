import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from calendar import monthrange

# =========================
# Funções auxiliares
# =========================

# Arquivos
ESCALAS_FILE = "escalas.json"
MENSALISTAS_FILE = "mensalistas.json"

def load_escalas():
    if os.path.exists(ESCALAS_FILE):
        with open(ESCALAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_escalas(data):
    with open(ESCALAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_mensalistas():
    if os.path.exists(MENSALISTAS_FILE):
        with open(MENSALISTAS_FILE, "r", encoding="utf-8") as f:
            mensalistas = json.load(f)
    else:
        mensalistas = {}

    hoje = datetime.today()
    atual = hoje.strftime("%Y-%m")
    proximo = (datetime(hoje.year + (hoje.month // 12), (hoje.month % 12) + 1, 1)).strftime("%Y-%m")

    if atual not in mensalistas:
        mensalistas[atual] = {"mensalistas": [], "substitutos": {}}
    if proximo not in mensalistas:
        mensalistas[proximo] = {"mensalistas": [], "substitutos": {}}

    return mensalistas, atual, proximo

def save_mensalistas(data):
    with open(MENSALISTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def semanas_do_mes(mes_str):
    ano, mes = map(int, mes_str.split("-"))
    semanas = []
    _, ultimo_dia = monthrange(ano, mes)
    for dia in range(1, ultimo_dia + 1, 7):
        semana = f"Semana {((dia - 1) // 7) + 1}"
        if semana not in semanas:
            semanas.append(semana)
    return semanas

# =========================
# App Streamlit
# =========================
st.set_page_config(page_title="Escala de Trabalho", layout="wide")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Escala", "Gerenciar Escala", "Resumo", "Mensalistas"])

# ---------------- Tab 1 - Escala ----------------
with tab1:
    st.title("Escala da Semana 📋")

    escalas = load_escalas()
    hoje = datetime.today().strftime("%Y-%m-%d")

    if hoje in escalas:
        st.subheader(f"Escala de hoje ({hoje})")
        for tarefa, pessoa in escalas[hoje].items():
            st.write(f"**{tarefa}:** {pessoa}")
    else:
        st.warning("Não há escala cadastrada para hoje.")

# ---------------- Tab 2 - Gerenciar Escala ----------------
with tab2:
    st.title("Gerenciar Escala 🛠️")

    escalas = load_escalas()
    data = st.date_input("Escolha a data:")
    data_str = data.strftime("%Y-%m-%d")

    if data_str not in escalas:
        escalas[data_str] = {}

    tarefa = st.text_input("Nome da tarefa:")
    pessoa = st.text_input("Pessoa responsável:")

    if st.button("Salvar"):
        if tarefa and pessoa:
            escalas[data_str][tarefa] = pessoa
            save_escalas(escalas)
            st.success("Tarefa adicionada à escala!")
        else:
            st.error("Preencha todos os campos.")

    if escalas[data_str]:
        st.subheader(f"Escala em {data_str}")
        for tarefa, pessoa in escalas[data_str].items():
            st.write(f"**{tarefa}:** {pessoa}")

# ---------------- Tab 3 - Resumo ----------------
with tab3:
    st.title("Resumo Geral 📊")

    escalas = load_escalas()
    dados = []
    for data, tarefas in escalas.items():
        for tarefa, pessoa in tarefas.items():
            dados.append([data, tarefa, pessoa])

    if dados:
        df = pd.DataFrame(dados, columns=["Data", "Tarefa", "Pessoa"])
        st.dataframe(df)
    else:
        st.info("Nenhuma escala cadastrada ainda.")

# ---------------- Tab 4 - Mensalistas ----------------
with tab4:
    st.title("Mensalistas 📅")
    mensalistas, atual, proximo = load_mensalistas()

    def ensure_structure(data, mes):
        if isinstance(data[mes], list):  
            data[mes] = {"mensalistas": data[mes], "substitutos": {}}
        if "mensalistas" not in data[mes]:
            data[mes]["mensalistas"] = []
        if "substitutos" not in data[mes]:
            data[mes]["substitutos"] = {}
        return data

    mensalistas = ensure_structure(mensalistas, atual)
    mensalistas = ensure_structure(mensalistas, proximo)

    # ---- Mostrar mês atual ----
    st.subheader(f"Mês atual ({atual})")
    for nome in mensalistas[atual]["mensalistas"]:
        cols = st.columns([3, 1, 1])
        cols[0].write(f"• {nome}")

        # Botão remover
        if cols[1].button("❌", key=f"rem_mensal_{atual}_{nome}"):
            mensalistas[atual]["mensalistas"].remove(nome)
            mensalistas[atual]["substitutos"].pop(nome, None)
            save_mensalistas(mensalistas)
            st.rerun()

        # Botão adicionar substituto
        if cols[2].button("➕ Subst.", key=f"sub_mensal_{atual}_{nome}"):
            semana = st.text_input(f"Semana de ausência para {nome}:", key=f"semana_{atual}_{nome}")
            if semana:
                if nome not in mensalistas[atual]["substitutos"]:
                    mensalistas[atual]["substitutos"][nome] = []
                if semana not in mensalistas[atual]["substitutos"][nome]:
                    mensalistas[atual]["substitutos"][nome].append(semana)
                    save_mensalistas(mensalistas)
                    st.success(f"{nome} marcado com substituto na {semana}")
                    st.rerun()

    # ---- Mostrar próximo mês ----
    st.subheader(f"Próximo mês ({proximo})")
    for nome in mensalistas[proximo]["mensalistas"]:
        cols = st.columns([3, 1, 1])
        cols[0].write(f"• {nome}")

        if cols[1].button("❌", key=f"rem_mensal_{proximo}_{nome}"):
            mensalistas[proximo]["mensalistas"].remove(nome)
            mensalistas[proximo]["substitutos"].pop(nome, None)
            save_mensalistas(mensalistas)
            st.rerun()

        if cols[2].button("➕ Subst.", key=f"sub_mensal_{proximo}_{nome}"):
            semana = st.text_input(f"Semana de ausência para {nome}:", key=f"semana_{proximo}_{nome}")
            if semana:
                if nome not in mensalistas[proximo]["substitutos"]:
                    mensalistas[proximo]["substitutos"][nome] = []
                if semana not in mensalistas[proximo]["substitutos"][nome]:
                    mensalistas[proximo]["substitutos"][nome].append(semana)
                    save_mensalistas(mensalistas)
                    st.success(f"{nome} marcado com substituto na {semana}")
                    st.rerun()

    # ---- Adicionar novo mensalista ----
    st.divider()
    nome = st.text_input("Nome do mensalista:")
    mes_escolhido = st.radio("Adicionar em:", [atual, proximo])

    if st.button("Adicionar Mensalista") and nome:
        if nome not in mensalistas[mes_escolhido]["mensalistas"]:
            mensalistas[mes_escolhido]["mensalistas"].append(nome)
            mensalistas[mes_escolhido]["substitutos"][nome] = []
            save_mensalistas(mensalistas)
            st.success(f"{nome} adicionado em {mes_escolhido}")
            st.rerun()
        else:
            st.warning("Esse nome já está cadastrado nesse mês.")

