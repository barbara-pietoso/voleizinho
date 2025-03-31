import streamlit as st
import datetime

# Função para carregar ou inicializar os dados
def init_session():d
    if 'volei_agenda' not in st.session_state:
        st.session_state.volei_agenda = {
            day: {'Titulares': [], 'Reservas': [], 'Substitutos': []} for day in ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        }

# Função para limpar dias passados
def clean_past_days():
    today = datetime.datetime.today().strftime('%A')
    days = list(st.session_state.volei_agenda.keys())
    if today in days:
        index = days.index(today)
        for past_day in days[:index]:
            st.session_state.volei_agenda.pop(past_day, None)

# Inicializa os dados e limpa dias passados
init_session()
clean_past_days()

st.title("Lista de Jogos de Vôlei 🏐")

# Seleção do dia
selected_day = st.selectbox("Escolha um dia da semana:", list(st.session_state.volei_agenda.keys()))

# Exibição da lista atual
day_data = st.session_state.volei_agenda[selected_day]

st.subheader(f"Lista de {selected_day}")
st.text(f"Titulares ({len(day_data['Titulares'])}/15):")
st.write(day_data['Titulares'])
st.text(f"Reservas ({len(day_data['Reservas'])}/3):")
st.write(day_data['Reservas'])
st.text(f"Substitutos:")
st.write(day_data['Substitutos'])

# Entrada para adicionar jogador
name = st.text_input("Seu nome:")
if st.button("Entrar na Lista") and name:
    if name in day_data['Titulares'] or name in day_data['Reservas'] or name in day_data['Substitutos']:
        st.warning("Você já está na lista!")
    else:
        if len(day_data['Titulares']) < 15:
            day_data['Titulares'].append(name)
        elif len(day_data['Reservas']) < 3:
            day_data['Reservas'].append(name)
        else:
            day_data['Substitutos'].append(name)
        st.success(f"{name} adicionado à lista de {selected_day}!")
        st.rerun()

# Botão de reset (visível só para o administrador)
if st.button("Resetar Semana (Apenas Admin)"):
    init_session()
    st.success("Listas resetadas!")
    st.rerun()
