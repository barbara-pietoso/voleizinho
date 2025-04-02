import streamlit as st
import datetime
import json
import os
from datetime import timedelta

# Configurações da página
st.set_page_config(
    page_title="VOLEIZINHO PRA CURAR ONDE DÓI",
    page_icon=":volleyball:"
)

# Configurações iniciais
data_file = "volei_agenda.json"
quadras_file = "volei_quadras.json"
QUADRAS_DISPONIVEIS = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "24", "25", "26"]

# Funções de carregamento/salvamento
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

# Função para obter dias da semana
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

# Função para verificar se precisa resetar (domingo após 19h)
def should_reset():
    now = datetime.datetime.now()
    # Verifica se é domingo e após 19h
    if now.weekday() == 6 and now.hour >= 19:
        # Verifica se já resetamos hoje
        last_reset_file = "last_reset_date.txt"
        today_date = now.date().isoformat()
        
        if os.path.exists(last_reset_file):
            with open(last_reset_file, "r") as f:
                last_reset = f.read().strip()
            if last_reset == today_date:
                return False
        
        # Se chegou aqui, precisa resetar
        with open(last_reset_file, "w") as f:
            f.write(today_date)
        return True
    return False

# Função para resetar os dados
def reset_week_data():
    week_days = get_current_week_days()
    st.session_state.volei_agenda = {
        day: {'Titulares': [], 'Reservas': [], 'Substitutos': [], 'Quadra': None}
        for day in week_days
    }
    st.session_state.quadras = {day: None for day in week_days}
    save_data(st.session_state.volei_agenda)
    save_quadras(st.session_state.quadras)

# Inicialização dos dados
def initialize_data():
    # Verifica se precisa resetar antes de carregar
    if should_reset():
        reset_week_data()
    else:
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

# Função para remover jogador com confirmação
def confirm_remove_name(day, name, role):
    if f"confirm_remove_{day}_{name}" not in st.session_state:
        st.session_state[f"confirm_remove_{day}_{name}"] = False
    
    if not st.session_state[f"confirm_remove_{day}_{name}"]:
        st.session_state[f"confirm_remove_{day}_{name}"] = True
        st.rerun()
    else:
        # Mostra o modal de confirmação
        with st.popover(f"Confirmar remoção de {name}", use_container_width=True):
            st.write(f"Tem certeza que deseja remover {name} da lista de {role.lower()} de {day}?")
            col1, col2 = st.columns(2)
            if col1.button("Sim, remover", key=f"confirm_yes_{day}_{name}"):
                remove_name(day, name, role)
                st.session_state[f"confirm_remove_{day}_{name}"] = False
                st.rerun()
            if col2.button("Cancelar", key=f"confirm_no_{day}_{name}"):
                st.session_state[f"confirm_remove_{day}_{name}"] = False
                st.rerun()

# Função para remover jogador (ação real)
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

# Função para remover quadra com confirmação
def confirm_remove_quadra(day):
    if f"confirm_remove_quadra_{day}" not in st.session_state:
        st.session_state[f"confirm_remove_quadra_{day}"] = False
    
    if not st.session_state[f"confirm_remove_quadra_{day}"]:
        st.session_state[f"confirm_remove_quadra_{day}"] = True
        st.rerun()
    else:
        # Mostra o modal de confirmação
        with st.popover("Confirmar remoção de quadra", use_container_width=True):
            st.write(f"Tem certeza que deseja remover a quadra {st.session_state.quadras.get(day)} de {day}?")
            col1, col2 = st.columns(2)
            if col1.button("Sim, remover", key=f"confirm_yes_quadra_{day}"):
                remove_quadra(day)
                st.session_state[f"confirm_remove_quadra_{day}"] = False
                st.rerun()
            if col2.button("Cancelar", key=f"confirm_no_quadra_{day}"):
                st.session_state[f"confirm_remove_quadra_{day}"] = False
                st.rerun()

# Função para remover quadra (ação real)
def remove_quadra(day):
    st.session_state.quadras[day] = None
    st.session_state.volei_agenda[day]['Quadra'] = None
    save_quadras(st.session_state.quadras)
    save_data(st.session_state.volei_agenda)
    st.rerun()

# Inicializa os dados
initialize_data()

# Layout principal com abas
tab1, tab2 = st.tabs(["Início", "Listas da Semana"])

with tab1:
    st.title("VOLEIZINHO PRA CURAR ONDE DÓI 🏐🩹🌈")
    st.write("""
    **Como usar:**
    - Na aba 'Listas da Semana', selecione os dias que deseja jogar
    - Digite seu nome e clique em 'Entrar na Lista'
    - Atribua uma quadra para cada dia dentro da aba do dia
    - Para sair de uma lista, clique no ❌ ao lado do seu nome

    **Regras do grupo**
     1) jogamos sempre a partir das listas criadas no grupo; 📝
 
     2) estabelecemos uma lista de 15 pessoas + 3 reservas para os jogos, mais a lista de substituições, por ordem de preenchimento. 
     primeiro entram para a lista os "reservas" e conforme for liberando vaga entram os "substitutos", de forma automática, no lugar de pessoas desistentes. 
     
     PORTANTO: 🔄
     - reserva: joga revezando
     - substituto: entra para a lista somente conforme as desistências 
     
     
     3) precisamos nos atentar para aqueles que colocam o nome na lista e não comparecem, já que isso prejudica aqueles que querem jogar e estão na lista de espera. lembrem de avisar com antecedência (tolerância de 2x, depois precisaremos tirar do grupo) 🔴
     
     4) jogadores de fora só podem entrar na lista caso esteja sobrando lugar NO DIA DO JOGO, dando prioridade aos participantes do grupo.
     
     5) com mais frequência será feita uma revisão no grupo, deixando apenas aqueles que estão comparecendo nos jogos com mais assiduidade 👀
     
     **OBS:** As listas são resetadas automaticamente todo domingo às 19h.
    """)

with tab2:
    st.title("Listas da Semana 🏐")
    
    # Seção para adicionar jogadores
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
    
    # Exibição das listas por dia
    tab_labels = [day.split()[0] for day in st.session_state.volei_agenda.keys()]
    tabs = st.tabs(tab_labels)
    
    for tab, (day, data) in zip(tabs, st.session_state.volei_agenda.items()):
        with tab:
            day_name = day.split()[0]
            current_quadra = st.session_state.quadras.get(day)
            
            # Layout com duas colunas: Listas e Quadra
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{day}**")
                
                # Listas de jogadores
                st.write(f"**Titulares ({len(data['Titulares'])}/15):**")
                for i, name in enumerate(data['Titulares']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_tit_{day_name}_{name}"):
                        confirm_remove_name(day, name, 'Titulares')
                
                st.write(f"**Reservas ({len(data['Reservas'])}/3):**")
                for i, name in enumerate(data['Reservas']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_res_{day_name}_{name}"):
                        confirm_remove_name(day, name, 'Reservas')
                
                st.write("**Substitutos:**")
                for i, name in enumerate(data['Substitutos']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_sub_{day_name}_{name}"):
                        confirm_remove_name(day, name, 'Substitutos')
            
            with col2:
                st.markdown("**Quadra**")
                quadra_container = st.container()
                
                if current_quadra:
                    quadra_container.write(f"Quadra selecionada: **{current_quadra}**")
                    if st.button("❌ Remover", key=f"remove_quadra_{day_name}"):
                        confirm_remove_quadra(day)
                else:
                    quadra_selecionada = st.selectbox(
                        "Selecione a quadra:",
                        options=[""] + QUADRAS_DISPONIVEIS,
                        index=0,
                        key=f"quadra_select_{day_name}"
                    )
                    
                    if quadra_selecionada and st.button("Selecionar", key=f"select_quadra_{day_name}"):
                        st.session_state.quadras[day] = quadra_selecionada
                        st.session_state.volei_agenda[day]['Quadra'] = quadra_selecionada
                        save_quadras(st.session_state.quadras)
                        save_data(st.session_state.volei_agenda)
                        st.rerun()

    # Botão de reset manual com confirmação
    if st.button("Resetar Todas as Listas (Apenas Admin)"):
        if "confirm_reset" not in st.session_state:
            st.session_state.confirm_reset = True
            st.rerun()
        else:
            with st.popover("Confirmar reset", use_container_width=True):
                st.write("Tem certeza que deseja resetar TODAS as listas? Esta ação não pode ser desfeita!")
                col1, col2 = st.columns(2)
                if col1.button("Sim, resetar tudo", key="confirm_reset_yes"):
                    reset_week_data()
                    st.session_state.confirm_reset = False
                    st.success("Todas as listas foram resetadas!")
                    st.rerun()
                if col2.button("Cancelar", key="confirm_reset_no"):
                    st.session_state.confirm_reset = False
                    st.rerun()




