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

st.title("Voleizinho da Semana 🏐")

# Botões para os dias da semana
days = list(st.session_state.volei_agenda.keys())

# Mantém a aba ativa no último dia selecionado
selected_day = st.session_state.selected_day or days[0]
cols = st.columns(len(days))

for i, day in enumerate(days):
    if cols[i].button(day):
        st.session_state.selected_day = day
        st.rerun()

# Exibir a lista do dia selecionado
day_data = st.session_state.volei_agenda[st.session_state.selected_day]

st.subheader(f"Lista para {st.session_state.selected_day}")

# Entrada para adicionar jogador
name = st.text_input("Seu nome:")
if st.button("Entrar na Lista") and name:
    if name in day_data['Titulares'] or name in day_data['Reservas'] or name in day_data['Substitutos']:
        st.warning(f"Você já está na lista de {st.session_state.selected_day}!")
    else:
        if len(day_data['Titulares']) < 15:
            day_data['Titulares'].append(name)
        elif len(day_data['Reservas']) < 3:
            day_data['Reservas'].append(name)
        else:
            day_data['Substitutos'].append(name)
        st.success(f"{name} adicionado à lista de {st.session_state.selected_day}!")
        save_data(st.session_state.volei_agenda)
        st.rerun()

# Exibição das listas com layout original
col1, col2, col3 = st.columns(3)

with col1:
    st.text(f"Titulares ({len(day_data['Titulares'])}/15):")
    for i, name in enumerate(day_data['Titulares']):
        st.write(f"{i+1}. {name}")
        if st.button(f"❌", key=f"remove_{st.session_state.selected_day}_Titulares_{name}"):
            remove_name(st.session_state.selected_day, name, 'Titulares')

with col2:
    st.text(f"Reservas ({len(day_data['Reservas'])}/3):")
    for i, name in enumerate(day_data['Reservas']):
        st.write(f"{i+1}. {name}")
        if st.button(f"❌", key=f"remove_{st.session_state.selected_day}_Reservas_{name}"):
            remove_name(st.session_state.selected_day, name, 'Reservas')

with col3:
    st.text(f"Substitutos:")
    for i, name in enumerate(day_data['Substitutos']):
        st.write(f"{i+1}. {name}")
        if st.button(f"❌", key=f"remove_{st.session_state.selected_day}_Substitutos_{name}"):
            remove_name(st.session_state.selected_day, name, 'Substitutos')

# Botão de reset (visível só para o administrador)
if st.button("Resetar Semana (Apenas Admin)"):
    st.session_state.volei_agenda = load_data()
    save_data(st.session_state.volei_agenda)
    st.success("Listas resetadas!")
    st.rerun()






