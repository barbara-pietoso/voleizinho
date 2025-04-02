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

# [...] (mantenha todas as outras funções como load_data, save_data, etc.)

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

# Função para remover quadra (ação real)
def remove_quadra(day):
    st.session_state.quadras[day] = None
    st.session_state.volei_agenda[day]['Quadra'] = None
    save_quadras(st.session_state.quadras)
    save_data(st.session_state.volei_agenda)
    st.rerun()

# Função para mostrar confirmação de remoção
def show_confirmation(day, name=None, role=None, is_quadra=False):
    if is_quadra:
        st.session_state[f'confirming_quadra_{day}'] = True
    else:
        st.session_state[f'confirming_{day}_{name}_{role}'] = True
    st.rerun()

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
                        show_confirmation(day, name, 'Titulares')
                    
                    # Mostrar confirmação se necessário
                    if st.session_state.get(f'confirming_{day}_{name}_Titulares'):
                        with st.popover(f"Confirmar remoção de {name}", use_container_width=True):
                            st.write(f"Tem certeza que deseja remover {name} da lista de titulares de {day}?")
                            col1, col2 = st.columns(2)
                            if col1.button("Sim, remover", key=f"confirm_yes_{day}_{name}_Titulares"):
                                remove_name(day, name, 'Titulares')
                            if col2.button("Cancelar", key=f"confirm_no_{day}_{name}_Titulares"):
                                st.session_state[f'confirming_{day}_{name}_Titulares'] = False
                                st.rerun()
                
                st.write(f"**Reservas ({len(data['Reservas'])}/3):**")
                for i, name in enumerate(data['Reservas']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_res_{day_name}_{name}"):
                        show_confirmation(day, name, 'Reservas')
                    
                    if st.session_state.get(f'confirming_{day}_{name}_Reservas'):
                        with st.popover(f"Confirmar remoção de {name}", use_container_width=True):
                            st.write(f"Tem certeza que deseja remover {name} da lista de reservas de {day}?")
                            col1, col2 = st.columns(2)
                            if col1.button("Sim, remover", key=f"confirm_yes_{day}_{name}_Reservas"):
                                remove_name(day, name, 'Reservas')
                            if col2.button("Cancelar", key=f"confirm_no_{day}_{name}_Reservas"):
                                st.session_state[f'confirming_{day}_{name}_Reservas'] = False
                                st.rerun()
                
                st.write("**Substitutos:**")
                for i, name in enumerate(data['Substitutos']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_sub_{day_name}_{name}"):
                        show_confirmation(day, name, 'Substitutos')
                    
                    if st.session_state.get(f'confirming_{day}_{name}_Substitutos'):
                        with st.popover(f"Confirmar remoção de {name}", use_container_width=True):
                            st.write(f"Tem certeza que deseja remover {name} da lista de substitutos de {day}?")
                            col1, col2 = st.columns(2)
                            if col1.button("Sim, remover", key=f"confirm_yes_{day}_{name}_Substitutos"):
                                remove_name(day, name, 'Substitutos')
                            if col2.button("Cancelar", key=f"confirm_no_{day}_{name}_Substitutos"):
                                st.session_state[f'confirming_{day}_{name}_Substitutos'] = False
                                st.rerun()
            
            with col2:
                st.markdown("**Quadra**")
                quadra_container = st.container()
                
                if current_quadra:
                    quadra_container.write(f"Quadra selecionada: **{current_quadra}**")
                    if st.button("❌ Remover", key=f"remove_quadra_{day_name}"):
                        show_confirmation(day, is_quadra=True)
                    
                    if st.session_state.get(f'confirming_quadra_{day}'):
                        with st.popover("Confirmar remoção de quadra", use_container_width=True):
                            st.write(f"Tem certeza que deseja remover a quadra {current_quadra} de {day}?")
                            col1, col2 = st.columns(2)
                            if col1.button("Sim, remover", key=f"confirm_yes_quadra_{day}"):
                                remove_quadra(day)
                            if col2.button("Cancelar", key=f"confirm_no_quadra_{day}"):
                                st.session_state[f'confirming_quadra_{day}'] = False
                                st.rerun()
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
        st.session_state['confirming_reset'] = True
    
    if st.session_state.get('confirming_reset'):
        with st.popover("Confirmar reset", use_container_width=True):
            st.write("Tem certeza que deseja resetar TODAS as listas? Esta ação não pode ser desfeita!")
            col1, col2 = st.columns(2)
            if col1.button("Sim, resetar tudo"):
                reset_week_data()
                st.session_state['confirming_reset'] = False
                st.rerun()
            if col2.button("Cancelar"):
                st.session_state['confirming_reset'] = False
                st.rerun()



