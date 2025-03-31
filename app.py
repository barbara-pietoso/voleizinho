import streamlit as st
import datetime
import json
import os
from datetime import timedelta

# Configurações iniciais (mantenha igual)
data_file = "volei_agenda.json"
quadras_file = "volei_quadras.json"
QUADRAS_DISPONIVEIS = ["NÃO RESERVADA", "11", "12", "13", "14", "15", "16", "17", "18", "19", "24", "25", "26"]

# Funções de carregamento/salvamento (mantenha igual)
def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

def load_quadras():
    if os.path.exists(quadras_file):
        with open(quadras_file, "r") as f:
            return json.load(f)
    return {}

def save_quadras(data):
    with open(quadras_file, "w") as f:
        json.dump(data, f, indent=4)

# Função para obter dias da semana (mantenha igual)
def get_current_week_days():
    today = datetime.date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    days_order = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    days = []
    
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        day_name = days_order[i]
        day_date = current_day.strftime("%d/%m")
        time_info = "18h" if day_name in ["Sábado", "Domingo"] else "19h"
        days.append(f"{day_name} {day_date} {time_info}")
    
    return days

# Inicialização dos dados (mantenha igual)
def initialize_data():
    week_days = get_current_week_days()
    
    if 'volei_agenda' not in st.session_state:
        st.session_state.volei_agenda = load_data()
        if not st.session_state.volei_agenda:
            st.session_state.volei_agenda = {
                day: {'Titulares': [], 'Reservas': [], 'Substitutos': [], 'Quadra': None}
                for day in week_days
            }
            save_data(st.session_state.volei_agenda)
    
    if 'quadras' not in st.session_state:
        st.session_state.quadras = load_quadras()
        if not st.session_state.quadras:
            st.session_state.quadras = {day: None for day in week_days}
            save_quadras(st.session_state.quadras)

# Função para remover jogador (mantenha igual)
def remove_name(day, name, role):
    day_data = st.session_state.volei_agenda[day]
    
    if name in day_data[role]:
        day_data[role].remove(name)
        
        if role == "Titulares" and day_data["Reservas"]:
            promoted = day_data["Reservas"].pop(0)
            day_data["Titulares"].append(promoted)
            if day_data["Substitutos"]:
                new_reserva = day_data["Substitutos"].pop(0)
                day_data["Reservas"].append(new_reserva)
        elif role == "Reservas" and day_data["Substitutos"]:
            promoted = day_data["Substitutos"].pop(0)
            day_data["Reservas"].append(promoted)
        
        save_data(st.session_state.volei_agenda)
        st.success(f"{name} removido e lista reorganizada para {day}!")
        st.rerun()

# Inicializa os dados
initialize_data()

# Layout principal com abas
tab1, tab2 = st.tabs(["Início", "Listas da Semana"])

with tab1:
    st.title("Bem-vindo ao Voleizinho da Semana 🏐")
    st.write("""
    **Como usar:**
    - Na aba 'Listas da Semana', selecione os dias que deseja jogar
    - Digite seu nome e clique em 'Entrar na Lista'
    - Atribua uma quadra para cada dia dentro da aba do dia
    - Para sair de uma lista, clique no ❌ ao lado do seu nome
    """)

with tab2:
    st.title("Listas da Semana 🏐")
    
    # Seção para adicionar jogadores (mantida no topo)
    st.subheader("Adicionar Jogador")
    days_selected = st.multiselect(
        "Escolha os dias para jogar:",
        options=list(st.session_state.volei_agenda.keys())
    )
    
    name = st.text_input("Seu nome:")
    if st.button("Entrar na Lista") and name:
        for day in days_selected:
            day_data = st.session_state.volei_agenda[day]
            if name in day_data['Titulares'] + day_data['Reservas'] + day_data['Substitutos']:
                st.warning(f"Você já está na lista de {day}!")
            else:
                if len(day_data['Titulares']) < 15:
                    day_data['Titulares'].append(name)
                elif len(day_data['Reservas']) < 3:
                    day_data['Reservas'].append(name)
                else:
                    day_data['Substitutos'].append(name)
                st.success(f"{name} adicionado à lista de {day}!")
        
        save_data(st.session_state.volei_agenda)
        st.rerun()
    
    # Exibição das listas por dia com seção de quadra DENTRO de cada aba
    tabs = st.tabs([f"{day.split()[0]}" for day in st.session_state.volei_agenda.keys()])
    
    for tab, (day, data) in zip(tabs, st.session_state.volei_agenda.items()):
        with tab:
            # Seção para selecionar quadra DENTRO da aba do dia
            current_quadra = st.session_state.quadras.get(day)
            quadra = st.selectbox(
                "Selecione a quadra:",
                options=["Selecione"] + QUADRAS_DISPONIVEIS,
                index=0 if current_quadra is None else QUADRAS_DISPONIVEIS.index(current_quadra) + 1,
                key=f"quadra_select_{day}"
            )
            
            if quadra != "Selecione" and quadra != current_quadra:
                st.session_state.quadras[day] = quadra
                st.session_state.volei_agenda[day]['Quadra'] = quadra
                save_quadras(st.session_state.quadras)
                save_data(st.session_state.volei_agenda)
                st.rerun()
            
            st.markdown(f"**{day} - Quadra: {st.session_state.quadras.get(day, 'Não definida')}**")
            
            # Listas de jogadores (mantido igual)
            st.write(f"**Titulares ({len(data['Titulares'])}/15):**")
            for i, name in enumerate(data['Titulares']):
                cols = st.columns([4, 1])
                cols[0].write(f"{i+1}. {name}")
                if cols[1].button("❌", key=f"rem_tit_{day}_{name}"):
                    remove_name(day, name, 'Titulares')
            
            st.write(f"**Reservas ({len(data['Reservas'])}/3):**")
            for i, name in enumerate(data['Reservas']):
                cols = st.columns([4, 1])
                cols[0].write(f"{i+1}. {name}")
                if cols[1].button("❌", key=f"rem_res_{day}_{name}"):
                    remove_name(day, name, 'Reservas')
            
            st.write("**Substitutos:**")
            for i, name in enumerate(data['Substitutos']):
                cols = st.columns([4, 1])
                cols[0].write(f"{i+1}. {name}")
                if cols[1].button("❌", key=f"rem_sub_{day}_{name}"):
                    remove_name(day, name, 'Substitutos')

    # Botão de reset (mantido igual)
    if st.button("Resetar Todas as Listas (Apenas Admin)"):
        st.session_state.volei_agenda = {}
        st.session_state.quadras = {}
        initialize_data()
        st.success("Todas as listas foram resetadas!")
        st.rerun()





