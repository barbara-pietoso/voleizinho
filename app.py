import streamlit as st
import datetime
import json
import os
import copy

# ================= Configurações =================
st.set_page_config(
    page_title="VOLEIZINHO PRA CURAR ONDE DÓI",
    page_icon=":volleyball:"
)

# Arquivos de dados
data_file = "volei_agenda.json"
quadras_file = "volei_quadras.json"
mensalistas_file = "mensalistas.json"

QUADRAS_DISPONIVEIS = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "24", "25", "26"]
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

DIA_ESTRUTURA = {
    'Titulares': [],
    'Reservas': [],
    'Substitutos': [],
    'Quadra': None
}

# ================= Funções utilitárias =================
def load_data():
    if os.path.exists(data_file):
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    for dia in DIAS_SEMANA:
        if dia not in data:
            data[dia] = copy.deepcopy(DIA_ESTRUTURA)
        else:
            for key in DIA_ESTRUTURA:
                if key not in data[dia]:
                    data[dia][key] = copy.deepcopy(DIA_ESTRUTURA[key])
    return data

def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_quadras():
    if os.path.exists(quadras_file):
        try:
            with open(quadras_file, "r") as f:
                quadras = json.load(f)
        except json.JSONDecodeError:
            quadras = {}
    else:
        quadras = {}
    for dia in DIAS_SEMANA:
        if dia not in quadras:
            quadras[dia] = None
    return quadras

def save_quadras(quadras):
    with open(quadras_file, "w") as f:
        json.dump(quadras, f, indent=4, ensure_ascii=False)

# ================= Mensalistas =================
def get_month_key(date):
    return date.strftime("%Y-%m")

def load_mensalistas():
    if os.path.exists(mensalistas_file):
        try:
            with open(mensalistas_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    hoje = datetime.date.today()
    atual = get_month_key(hoje)
    proximo = get_month_key((hoje.replace(day=1) + datetime.timedelta(days=32)).replace(day=1))

    def ensure_structure(data, mes):
        if mes not in data:
            data[mes] = {"mensalistas": [], "substitutos": {}}
        if isinstance(data[mes], list):  # compatibilidade com formato antigo
            data[mes] = {"mensalistas": data[mes], "substitutos": {}}
        if "mensalistas" not in data[mes]:
            data[mes]["mensalistas"] = []
        if "substitutos" not in data[mes]:
            data[mes]["substitutos"] = {}
        return data

    data = ensure_structure(data, atual)
    data = ensure_structure(data, proximo)
    return data, atual, proximo

def save_mensalistas(data):
    with open(mensalistas_file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ================= Reset Semanal =================
def should_reset():
    now = datetime.datetime.now()
    if now.weekday() == 6 and now.hour >= 19:  # domingo após 19h
        last_reset_file = "last_reset_date.txt"
        today_date = now.date().isoformat()
        if os.path.exists(last_reset_file):
            with open(last_reset_file, "r") as f:
                last_reset = f.read().strip()
            if last_reset == today_date:
                return False
        with open(last_reset_file, "w") as f:
            f.write(today_date)
        return True
    return False

def reset_week_data():
    data = {dia: copy.deepcopy(DIA_ESTRUTURA) for dia in DIAS_SEMANA}
    quadras = {dia: None for dia in DIAS_SEMANA}
    save_data(data)
    save_quadras(quadras)
    st.rerun()

# ================= Início do App =================
if should_reset():
    reset_week_data()

tab1, tab2, tab3, tab4 = st.tabs(["Início", "Listas da Semana", "Exportar Listas", "Mensalistas"])

# ---------------- Tab 1 ----------------
with tab1:
    st.title("VOLEIZINHO PRA CURAR ONDE DÓI 🏐🩹🌈")
    st.write("""
    **Como usar:**
    - Use a aba 'Listas da Semana' para organizar quem joga cada dia.
    - Use a aba 'Mensalistas' para registrar quem está ativo nos meses.
    - Titulares: até 15 jogadores, depois 3 reservas e os demais como substitutos.
    """)

# ---------------- Tab 2 ----------------
with tab2:
    st.title("Listas da Semana 🏐")
    st.write("⚙️ Aqui entra o mesmo código que você já tinha para adicionar jogadores, quadras e resetar (mantém igual).")

# ---------------- Tab 3 ----------------
with tab3:
    st.title("Exportar Listas")
    st.write("⚙️ Aqui também mantém o mesmo código de exportar listas (sem mudanças).")

# ---------------- Tab 4 - Mensalistas ----------------
with tab4:
    st.title("Mensalistas 📅")
    mensalistas, atual, proximo = load_mensalistas()

    def render_mes(mes):
        st.subheader(f"{mes}")
        for nome in mensalistas[mes]["mensalistas"]:
            cols = st.columns([3, 1, 1])
            cols[0].write(f"• {nome}")

            # Botão remover
            if cols[1].button("❌", key=f"rem_mensal_{mes}_{nome}"):
                mensalistas[mes]["mensalistas"].remove(nome)
                mensalistas[mes]["substitutos"].pop(nome, None)
                save_mensalistas(mensalistas)
                st.rerun()

            # Botão adicionar substituto
            if cols[2].button("➕ Subst.", key=f"sub_mensal_{mes}_{nome}"):
                semana = st.text_input(f"Semana de ausência para {nome} ({mes}):", key=f"semana_{mes}_{nome}")
                if semana:
                    if nome not in mensalistas[mes]["substitutos"]:
                        mensalistas[mes]["substitutos"][nome] = []
                    if semana not in mensalistas[mes]["substitutos"][nome]:
                        mensalistas[mes]["substitutos"][nome].append(semana)
                        save_mensalistas(mensalistas)
                        st.success(f"{nome} marcado com substituto na {semana}")
                        st.rerun()

    st.subheader(f"Mês atual ({atual})")
    render_mes(atual)

    st.subheader(f"Próximo mês ({proximo})")
    render_mes(proximo)

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
