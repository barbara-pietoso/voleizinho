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
        # Caso o arquivo não exista, inicializa com dados padrão
        return {
            day: {'Titulares': [], 'Reservas': [], 'Substitutos': []} for day in ['Segunda 19h', 'Terça 19h', 'Quarta 19h', 'Quinta 19h', 'Sexta 19h', 'Sábado 18h', 'Domingo 18h']
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

# Carregar os dados ao iniciar o app
st.session_state.volei_agenda = load_data()
clean_past_days()

st.title("Lista de Jogos de Vôlei 🏐")

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
    
    # Salva as informações após a alteração
    save_data(st.session_state.volei_agenda)
    st.rerun()

# Exibição de todas as listas abaixo numeradas
tabs = st.tabs([f"{i}. {day}" for i, day in enumerate(st.session_state.volei_agenda.keys(), start=1)])
for tab, (day, data) in zip(tabs, st.session_state.volei_agenda.items()):
    with tab:
        st.text(f"Titulares ({len(data['Titulares'])}/15):")
        st.write([f"{i+1}. {name}" for i, name in enumerate(data['Titulares'])])
        st.text(f"Reservas ({len(data['Reservas'])}/3):")
        st.write([f"{i+1}. {name}" for i, name in enumerate(data['Reservas'])])
        st.text(f"Substitutos:")
        st.write([f"{i+1}. {name}" for i, name in enumerate(data['Substitutos'])])

# Botão de reset (visível só para o administrador)
if st.button("Resetar Semana (Apenas Admin)"):
    st.session_state.volei_agenda = load_data()  # Carrega os dados iniciais
    save_data(st.session_state.volei_agenda)
    st.success("Listas resetadas!")
    st.rerun()


