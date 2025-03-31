import streamlit as st
import datetime
import json
import os

# Caminho do arquivo JSON para armazenar os dados
data_file = "volei_agenda.json"

# Função para carregar ou inicializar os dados
def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            return json.load(f)
    else:
        return {
            day: {'Titulares': [], 'Reservas': [], 'Substitutos': []} for day in 
            ['Segunda 19h', 'Terça 19h', 'Quarta 19h', 'Quinta 19h', 'Sexta 19h', 'Sábado 18h', 'Domingo 18h']
        }

# Função para salvar os dados no arquivo JSON
def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

# Função para limpar dias passados
def clean_past_days():
    today = datetime.datetime.today().strftime('%A')
    days = list(st.session_state.volei_agenda.keys())
    if today in days:
        index = days.index(today)
        for past_day in days[:index]:
            st.session_state.volei_agenda.pop(past_day, None)

# Função para remover um nome e reorganizar listas
def remove_name(day, name, role):
    day_data = st.session_state.volei_agenda[day]

    # Remover nome da lista correspondente
    if name in day_data[role]:
        day_data[role].remove(name)

        # Se for um Titular, promover um Reserva (se houver)
        if role == "Titulares" and day_data["Reservas"]:
            promoted = day_data["Reservas"].pop(0)
            day_data["Titulares"].append(promoted)

            # Se havia um Substituto, sobe para Reservas
            if day_data["Substitutos"]:
                new_reserva = day_data["Substitutos"].pop(0)
                day_data["Reservas"].append(new_reserva)

        # Se for um Reserva, promover um Substituto (se houver)
        elif role == "Reservas" and day_data["Substitutos"]:
            promoted = day_data["Substitutos"].pop(0)
            day_data["Reservas"].append(promoted)

        save_data(st.session_state.volei_agenda)
        st.success(f"{name} removido e lista reorganizada para {day}!")
        st.rerun()

# Carregar os dados ao iniciar o app
if "volei_agenda" not in st.session_state:
    st.session_state.volei_agenda = load_data()

if "selected_day" not in st.session_state:
    st.session_state.selected_day = None  # Para manter a aba ativa

clean_past_days()

st.title("Voleizinho da Semana 🏐")

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
            st.session_state.selected_day = selected_day  # Mantém a aba ativa
    
    save_data(st.session_state.volei_agenda)
    st.rerun()

# Exibição de todas as listas abaixo numeradas
tabs = list(st.session_state.volei_agenda.keys())
selected_tab = st.session_state.selected_day or tabs[0]  # Mantém a aba ativa

selected_tab_index = tabs.index(selected_tab)
tab_selection = st.radio("Escolha um dia:", tabs, index=selected_tab_index)

day_data = st.session_state.volei_agenda[tab_selection]

st.subheader(f"Lista para {tab_selection}")

st.text(f"Titulares ({len(day_data['Titulares'])}/15):")
for i, name in enumerate(day_data['Titulares']):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(f"{i+1}. {name}")
    with col2:
        if st.button(f"❌", key=f"remove_{tab_selection}_Titulares_{name}"):
            remove_name(tab_selection, name, 'Titulares')

st.text(f"Reservas ({len(day_data['Reservas'])}/3):")
for i, name in enumerate(day_data['Reservas']):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(f"{i+1}. {name}")
    with col2:
        if st.button(f"❌", key=f"remove_{tab_selection}_Reservas_{name}"):
            remove_name(tab_selection, name, 'Reservas')

st.text(f"Substitutos:")
for i, name in enumerate(day_data['Substitutos']):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(f"{i+1}. {name}")
    with col2:
        if st.button(f"❌", key=f"remove_{tab_selection}_Substitutos_{name}"):
            remove_name(tab_selection, name, 'Substitutos')

# Botão de reset (visível só para o administrador)
if st.button("Resetar Semana (Apenas Admin)"):
    st.session_state.volei_agenda = load_data()
    save_data(st.session_state.volei_agenda)
    st.success("Listas resetadas!")
    st.rerun()






