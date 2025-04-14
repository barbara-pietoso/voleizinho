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

# Dias da semana fixos
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

# Estrutura padrão para cada dia
DIA_ESTRUTURA = {
    'Titulares': [],
    'Reservas': [],
    'Substitutos': [],
    'Quadra': None
}

# Funções de carregamento/salvamento
def load_data():
    try:
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                data = json.load(f)
                # Garante que todos os dias estão presentes com a estrutura correta
                for dia in DIAS_SEMANA:
                    if dia not in data:
                        data[dia] = DIA_ESTRUTURA.copy()
                    else:
                        # Garante que todas as chaves existem
                        for key in DIA_ESTRUTURA:
                            if key not in data[dia]:
                                data[dia][key] = DIA_ESTRUTURA[key]
                return data
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    # Retorna estrutura vazia se arquivo não existir ou estiver corrompido
    return {dia: DIA_ESTRUTURA.copy() for dia in DIAS_SEMANA}

def save_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

def load_quadras():
    try:
        if os.path.exists(quadras_file):
            with open(quadras_file, "r") as f:
                quadras = json.load(f)
                # Garante que todos os dias estão presentes
                for dia in DIAS_SEMANA:
                    if dia not in quadras:
                        quadras[dia] = None
                return quadras
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    # Retorna estrutura vazia se arquivo não existir ou estiver corrompido
    return {dia: None for dia in DIAS_SEMANA}

def save_quadras(data):
    with open(quadras_file, "w") as f:
        json.dump(data, f, indent=4)

# Função para verificar se precisa resetar (domingo após 19h)
def should_reset():
    now = datetime.datetime.now()
    if now.weekday() == 6 and now.hour >= 19:
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

# Função para resetar os dados
def reset_week_data():
    data = {dia: DIA_ESTRUTURA.copy() for dia in DIAS_SEMANA}
    quadras = {dia: None for dia in DIAS_SEMANA}
    save_data(data)
    save_quadras(quadras)
    st.rerun()

# Carrega os dados atuais
def get_current_data():
    return load_data(), load_quadras()

# Função para remover jogador
def remove_name(day, name, role):
    data, quadras = get_current_data()
    day_data = data[day]
    
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
        
        save_data(data)
        st.rerun()

# Função para remover quadra
def remove_quadra(day):
    data, quadras = get_current_data()
    quadras[day] = None
    data[day]['Quadra'] = None
    save_quadras(quadras)
    save_data(data)
    st.rerun()

# Função para exportar resumo de um dia específico
def exportar_resumo_dia(dia):
    data, quadras = get_current_data()
    dia_data = data[dia]
    quadra = quadras.get(dia, "Não definida")
    
    if not dia_data['Titulares'] and not dia_data['Reservas'] and not dia_data['Substitutos']:
        return f"Não há jogadores cadastrados para {dia}"
    
    texto = f"🏐 *LISTA PARA {dia.upper()}* 🏐\n"
    texto += f"📍 *Quadra:* {quadra}\n\n"
    
    if dia_data['Titulares']:
        texto += "🌟 *TITULARES* (15):\n"
        texto += "\n".join([f"➡️ {i+1}. {nome}" for i, nome in enumerate(dia_data['Titulares'])]) + "\n\n"
    
    if dia_data['Reservas']:
        texto += "🔄 *RESERVAS* (3):\n"
        texto += "\n".join([f"⏳ {i+1}. {nome}" for i, nome in enumerate(dia_data['Reservas'])]) + "\n\n"
    
    if dia_data['Substitutos']:
        texto += "📋 *SUBSTITUTOS*:\n"
        texto += "\n".join([f"⚡ {i+1}. {nome}" for i, nome in enumerate(dia_data['Substitutos'])]) + "\n"
    
    texto += "\n_Atualizado em: " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M") + "_"
    return texto

# Função para exportar todas as listas
def exportar_todas_listas():
    data, quadras = get_current_data()
    texto = "🏐 *LISTA COMPLETA DO VOLEIZINHO* 🏐\n\n"
    
    for dia in DIAS_SEMANA:
        dia_data = data[dia]
        quadra = quadras.get(dia, "Não definida")
        
        if dia_data['Titulares'] or dia_data['Reservas'] or dia_data['Substitutos']:
            texto += f"*{dia.upper()}* (Quadra: {quadra})\n"
            
            if dia_data['Titulares']:
                texto += "👉 Titulares:\n" + "\n".join([f"• {nome}" for nome in dia_data['Titulares']]) + "\n"
            
            if dia_data['Reservas']:
                texto += "🔄 Reservas:\n" + "\n".join([f"• {nome}" for nome in dia_data['Reservas']]) + "\n"
            
            if dia_data['Substitutos']:
                texto += "⏳ Substitutos:\n" + "\n".join([f"• {nome}" for nome in dia_data['Substitutos']]) + "\n"
            
            texto += "\n" + "="*30 + "\n\n"
    
    return texto if texto != "🏐 *LISTA COMPLETA DO VOLEIZINHO* 🏐\n\n" else "Nenhum jogador cadastrado em nenhum dia."

# Verifica se precisa resetar os dados
if should_reset():
    reset_week_data()

# Layout principal com abas
tab1, tab2, tab3 = st.tabs(["Início", "Listas da Semana", "Exportar Listas"])

with tab1:
    st.title("VOLEIZINHO PRA CURAR ONDE DÓI 🏐🩹🌈")
    st.write("""
    **Como usar:**
    - Na aba 'Listas da Semana', selecione os dias que deseja jogar
    - Digite seu nome e clique em 'Entrar na Lista'
    - Atribua uma quadra para cada dia dentro da aba do dia
    - Para sair de uma lista, clique no ❌ ao lado do seu nome
    - Na aba 'Exportar Listas', gere resumos diários para enviar no grupo

    **Regras das listas**
    1) Jogamos sempre a partir das listas criadas no grupo; 📝
    2) Lista de 15 titulares + 3 reservas + substitutos por ordem de chegada
    3) Respeitar as listas e avisar com antecedência em caso de desistência
    4) Jogadores externos só entram se houver vaga no dia
    5) Chegar no horário combinado
    """)

with tab2:
    st.title("Listas da Semana 🏐")
    data, quadras = get_current_data()
    
    # Seção para adicionar jogadores
    st.subheader("Adicionar Jogador")
    days_selected = st.multiselect(
        "Escolha os dias para jogar:",
        options=DIAS_SEMANA,
        key="multiselect_dias_jogar"
    )
    
    name = st.text_input("Seu nome:", key="input_nome_jogador")
    
    if st.button("Entrar na Lista", key="botao_entrar_lista") and name:
        for day in days_selected:
            day_data = data[day]
            if name in day_data['Titulares'] + day_data['Reservas'] + day_data['Substitutos']:
                st.warning(f"Você já está na lista de {day}!")
            else:
                if len(day_data['Titulares']) < 15:
                    day_data['Titulares'].append(name)
                    papel = "Titulares"
                elif len(day_data['Reservas']) < 3:
                    day_data['Reservas'].append(name)
                    papel = "Reservas"
                else:
                    day_data['Substitutos'].append(name)
                    papel = "Substitutos"
                
                st.success(f"{name} adicionado como {papel} em {day}!")
        
        save_data(data)
        st.rerun()
    
    # Exibição das listas por dia
    tabs_dias = st.tabs(DIAS_SEMANA)
    
    for tab, day in zip(tabs_dias, DIAS_SEMANA):
        with tab:
            current_quadra = quadras.get(day)
            day_data = data[day]
            
            # Layout com duas colunas: Listas e Quadra
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{day}**")
                
                # Listas de jogadores
                st.write(f"**Titulares ({len(day_data['Titulares'])}/15):**")
                for i, name in enumerate(day_data['Titulares']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_tit_{day}_{name}"):
                        st.session_state[f"show_confirm_tit_{day}_{name}"] = True
                
                # Popover de confirmação para titulares
                for i, name in enumerate(day_data['Titulares']):
                    if st.session_state.get(f"show_confirm_tit_{day}_{name}"):
                        with st.popover(f"Confirmar remoção de {name}"):
                            st.write(f"Tem certeza que deseja remover {name} dos titulares?")
                            if st.button("Sim", key=f"confirm_yes_tit_{day}_{name}"):
                                remove_name(day, name, 'Titulares')
                                del st.session_state[f"show_confirm_tit_{day}_{name}"]
                            if st.button("Cancelar", key=f"confirm_no_tit_{day}_{name}"):
                                del st.session_state[f"show_confirm_tit_{day}_{name}"]
                                st.rerun()
                
                st.write(f"**Reservas ({len(day_data['Reservas'])}/3):**")
                for i, name in enumerate(day_data['Reservas']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_res_{day}_{name}"):
                        st.session_state[f"show_confirm_res_{day}_{name}"] = True
                
                for i, name in enumerate(day_data['Reservas']):
                    if st.session_state.get(f"show_confirm_res_{day}_{name}"):
                        with st.popover(f"Confirmar remoção de {name}"):
                            st.write(f"Tem certeza que deseja remover {name} dos reservas?")
                            if st.button("Sim", key=f"confirm_yes_res_{day}_{name}"):
                                remove_name(day, name, 'Reservas')
                                del st.session_state[f"show_confirm_res_{day}_{name}"]
                            if st.button("Cancelar", key=f"confirm_no_res_{day}_{name}"):
                                del st.session_state[f"show_confirm_res_{day}_{name}"]
                                st.rerun()
                
                st.write("**Substitutos:**")
                for i, name in enumerate(day_data['Substitutos']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_sub_{day}_{name}"):
                        st.session_state[f"show_confirm_sub_{day}_{name}"] = True
                
                for i, name in enumerate(day_data['Substitutos']):
                    if st.session_state.get(f"show_confirm_sub_{day}_{name}"):
                        with st.popover(f"Confirmar remoção de {name}"):
                            st.write(f"Tem certeza que deseja remover {name} dos substitutos?")
                            if st.button("Sim", key=f"confirm_yes_sub_{day}_{name}"):
                                remove_name(day, name, 'Substitutos')
                                del st.session_state[f"show_confirm_sub_{day}_{name}"]
                            if st.button("Cancelar", key=f"confirm_no_sub_{day}_{name}"):
                                del st.session_state[f"show_confirm_sub_{day}_{name}"]
                                st.rerun()
            
            with col2:
                st.markdown("**Quadra**")
                
                if current_quadra:
                    st.write(f"Quadra selecionada: **{current_quadra}**")
                    if st.button("❌ Remover", key=f"remove_quadra_{day}"):
                        st.session_state[f"show_confirm_quadra_{day}"] = True
                    
                    if st.session_state.get(f"show_confirm_quadra_{day}"):
                        with st.popover(f"Confirmar remoção da quadra"):
                            st.write("Tem certeza que deseja remover esta quadra?")
                            if st.button("Sim", key=f"confirm_yes_quadra_{day}"):
                                remove_quadra(day)
                                del st.session_state[f"show_confirm_quadra_{day}"]
                            if st.button("Cancelar", key=f"confirm_no_quadra_{day}"):
                                del st.session_state[f"show_confirm_quadra_{day}"]
                                st.rerun()
                else:
                    quadra_selecionada = st.selectbox(
                        "Selecione a quadra:",
                        options=[""] + QUADRAS_DISPONIVEIS,
                        index=0,
                        key=f"quadra_select_{day}"
                    )
                    
                    if quadra_selecionada and st.button("Selecionar", key=f"select_quadra_{day}"):
                        quadras[day] = quadra_selecionada
                        data[day]['Quadra'] = quadra_selecionada
                        save_quadras(quadras)
                        save_data(data)
                        st.rerun()

    # Botão de reset manual com confirmação
    if st.button("Resetar Todas as Listas (Apenas Admin)", key="botao_reset_admin"):
        st.session_state['show_confirm_reset'] = True
    
    if st.session_state.get('show_confirm_reset'):
        with st.popover("Confirmar reset"):
            st.warning("Tem certeza que deseja resetar TODAS as listas?")
            if st.button("Sim, resetar tudo", key="confirm_reset_sim"):
                reset_week_data()
                st.session_state['show_confirm_reset'] = False
                st.rerun()
            if st.button("Cancelar", key="confirm_reset_nao"):
                st.session_state['show_confirm_reset'] = False
                st.rerun()

with tab3:
    st.title("Exportar Listas para WhatsApp")
    
    st.write("Selecione o dia para gerar o resumo pronto para enviar no grupo:")
    
    dia_selecionado = st.selectbox(
        "Dia da semana:",
        options=DIAS_SEMANA,
        index=0,
        key="select_dia_export"
    )
    
    if st.button("Gerar Resumo Diário", key="botao_gerar_resumo"):
        resumo = exportar_resumo_dia(dia_selecionado)
        st.text_area("Resumo para WhatsApp:", 
                    value=resumo, 
                    height=300,
                    key="texto_resumo_dia")
        
        # Botão para copiar automaticamente
        st.button("📋 Copiar Resumo", 
                 on_click=lambda: st.write(f'<script>navigator.clipboard.writeText(`{resumo}`)</script>', 
                                         unsafe_allow_html=True))
    
    st.divider()
    
    if st.button("Gerar Lista Completa", key="botao_gerar_completa"):
        lista_completa = exportar_todas_listas()
        st.text_area("Lista Completa para WhatsApp:", 
                    value=lista_completa, 
                    height=400,
                    key="texto_lista_completa")
        
        # Botão para copiar automaticamente
        st.button("📋 Copiar Lista Completa", 
                 on_click=lambda: st.write(f'<script>navigator.clipboard.writeText(`{lista_completa}`)</script>', 
                                         unsafe_allow_html=True))
