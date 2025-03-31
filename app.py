import streamlit as st
import datetime
import json
import os
from datetime import timedelta

# Caminho do arquivo JSON para armazenar os dados
data_file = "volei_agenda.json"

# Função para carregar ou inicializar os dados
def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            return json.load(f)
    else:
        return {}

# Função para salvar os dados no arquivo JSON
def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

# Função corrigida para obter os dias da semana atual
def get_current_week_days():
    today = datetime.date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Segunda-feira da semana atual
    
    days_order = [
        "Segunda",
        "Terça",
        "Quarta",
        "Quinta",
        "Sexta",
        "Sábado",
        "Domingo"
    ]
    
    days = []
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        day_name = days_order[i]
        day_date = current_day.strftime("%d/%m")  # Data formatada
        
        # Define os horários específicos para cada dia
        if day_name in ["Segunda", "Quarta", "Quinta", "Sábado"]:
            time_info = "19h - quadra 24" if day_name != "Sábado" else "18h - quadra 24"
        elif day_name == "Domingo":
            time_info = "18h"
        else:
            time_info = "19h"
        
        days.append(f"{day_name} {day_date} {time_info}")
    
    return days

# Função para inicializar os dados da semana
def initialize_week_data():
    week_days = get_current_week_days()
    if not st.session_state.volei_agenda or not any(day.split()[0] in str(st.session_state.volei_agenda.keys()) for day in week_days):
        st.session_state.volei_agenda = {
            day: {'Titulares': [], 'Reservas': [], 'Substitutos': []} for day in week_days
        }
        save_data(st.session_state.volei_agenda)

# Função para remover um nome e reorganizar listas
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

# Carregar os dados ao iniciar o app
if 'volei_agenda' not in st.session_state:
    st.session_state.volei_agenda = load_data()
    initialize_week_data()

# Layout com abas
tab1, tab2 = st.tabs(["Início", "Listas da Semana"])

with tab1:
    st.title("Bem-vindo ao Voleizinho da Semana 🏐")
    st.write("""
    Este aplicativo ajuda a organizar as listas de jogadores para os dias de vôlei da semana.
    
    **Como usar:**
    1. Na aba 'Listas da Semana', selecione os dias que deseja jogar
    2. Digite seu nome e clique em 'Entrar na Lista'
    3. Para sair de uma lista, clique no botão ❌ ao lado do seu nome
    
    **Regras:**
    - Máximo de 15 titulares por dia
    - Máximo de 3 reservas por dia
    - Substitutos ilimitados
    - Quando um titular sai, o primeiro reserva é promovido
    - Quando um reserva sai, o primeiro substituto é promovido
    """)

with tab2:
    st.title("Listas da Semana 🏐")
    
    # Seleção de múltiplos dias
    days_selected = st.multiselect("Escolha os dias da semana:", list(st.session_state.volei_agenda.keys()))

    # Entrada para adicionar jogador
    name = st.text_input("Seu nome:")
    if st.button("Entrar na Lista") and name:
        for selected_day in days_selected:
            day_data = st.session_state.volei_agenda[selected_day]
            if name in day_data['Titulares'] or name in day_data['Reservas'] or name in day_data['Substitutos']:
                st.warning(f"Você já está na lista de {selected_day}!")
            else:
                if len(day_data['Titulares']) < 15:
                    day_data['Titulares'].append(name)
                elif len(day_data['Reservas']) < 3:
                    day_data['Reservas'].append(name)
                else:
                    day_data['Substitutos'].append(name)
                st.success(f"{name} adicionado à lista de {selected_day}!")
        
        save_data(st.session_state.volei_agenda)
        st.rerun()

    # Exibição de todas as listas
    tabs = st.tabs([f"{i}. {day}" for i, day in enumerate(st.session_state.volei_agenda.keys(), start=1)])
    for tab, (day, data) in zip(tabs, st.session_state.volei_agenda.items()):
        with tab:
            st.text(f"Titulares ({len(data['Titulares'])}/15):")
            for i, name in enumerate(data['Titulares']):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write(f"{i+1}. {name}")
                with col2:
                    if st.button(f"❌", key=f"remove_{day}_Titulares_{name}"):
                        remove_name(day, name, 'Titulares')

            st.text(f"Reservas ({len(data['Reservas'])}/3):")
            for i, name in enumerate(data['Reservas']):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write(f"{i+1}. {name}")
                with col2:
                    if st.button(f"❌", key=f"remove_{day}_Reservas_{name}"):
                        remove_name(day, name, 'Reservas')

            st.text(f"Substitutos:")
            for i, name in enumerate(data['Substitutos']):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.write(f"{i+1}. {name}")
                with col2:
                    if st.button(f"❌", key=f"remove_{day}_Substitutos_{name}"):
                        remove_name(day, name, 'Substitutos')

    # Botão de reset
    if st.button("Resetar Semana (Apenas Admin)"):
        st.session_state.volei_agenda = {}
        initialize_week_data()
        save_data(st.session_state.volei_agenda)
        st.success("Listas resetadas!")
        st.rerun()






