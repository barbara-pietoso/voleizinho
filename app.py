import streamlit as st
import datetime
import json
import os
from datetime import timedelta
import locale

# --- Configurações Iniciais e Arquivos ---

# Configurações da página
st.set_page_config(
    page_title="VOLEIZINHO PRA CURAR ONDE DÓI",
    page_icon=":volleyball:"
)

# Arquivos de dados
DATA_FILE = "volei_agenda.json"
QUADRAS_FILE = "volei_quadras.json"
MENSALISTAS_FILE = "volei_mensalistas.json"
RESET_FILE = "last_reset_date.txt"

# Constantes
QUADRAS_DISPONIVEIS = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "24", "25", "26"]
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
DIA_ESTRUTURA = {
    'Titulares': [],
    'Reservas': [],
    'Substitutos': [],
    'Quadra': None
}

# --- Funções de Carregamento e Salvamento de Dados ---

def load_data(file_path, default_data):
    """Carrega dados de um arquivo JSON, retornando a estrutura padrão se houver erro ou o arquivo não existir."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding='utf-8') as f:
                data = json.load(f)
                return data
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    return default_data

def save_data(data, file_path):
    """Salva dados em um arquivo JSON."""
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Funções para Mês e Mensalistas ---

def get_current_and_next_month():
    """Retorna os nomes do mês atual e do próximo mês em português."""
    # Tenta definir a localidade para português do Brasil
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
        except locale.Error:
            st.warning("Não foi possível definir a localidade para português. Os nomes dos meses podem não estar em português.")
            
    now = datetime.datetime.now()
    current_month_name = now.strftime("%B").capitalize()
    
    # Próximo mês
    next_month_date = now + timedelta(days=32)
    next_month_name = next_month_date.strftime("%B").capitalize()
    
    return current_month_name, next_month_name

def create_mensalistas_structure(current_month, next_month):
    """Cria a estrutura de dados para os mensalistas por dia da semana."""
    return {
        current_month: {dia: [] for dia in DIAS_SEMANA},
        next_month: {dia: [] for dia in DIAS_SEMANA}
    }

# --- Funções de Lógica da Aplicação ---

def should_reset():
    """Verifica se os dados devem ser resetados (domingo após 19h)."""
    now = datetime.datetime.now()
    if now.weekday() == 6 and now.hour >= 19:
        today_date = now.date().isoformat()
        last_reset = load_data(RESET_FILE, "")
        if last_reset == today_date:
            return False
        save_data(today_date, RESET_FILE)
        return True
    return False

def reset_week_data():
    """Reseta todos os dados das listas e quadras da semana."""
    default_data = {dia: DIA_ESTRUTURA.copy() for dia in DIAS_SEMANA}
    save_data(default_data, DATA_FILE)
    
    default_quadras = {dia: None for dia in DIAS_SEMANA}
    save_data(default_quadras, QUADRAS_FILE)
    
    st.session_state['data'] = default_data
    st.session_state['quadras'] = default_quadras
    st.success("Listas resetadas com sucesso!")
    st.rerun()

def add_name(day, name):
    """Adiciona um nome à lista de um dia específico."""
    day_data = st.session_state.data[day]
    if name in day_data['Titulares'] or name in day_data['Reservas'] or name in day_data['Substitutos']:
        st.warning(f"Você já está na lista de {day}!")
        return

    if len(day_data['Titulares']) < 15:
        day_data['Titulares'].append(name)
        papel = "Titulares"
    elif len(day_data['Reservas']) < 3:
        day_data['Reservas'].append(name)
        papel = "Reservas"
    else:
        day_data['Substitutos'].append(name)
        papel = "Substitutos"
    
    save_data(st.session_state.data, DATA_FILE)
    st.success(f"{name} adicionado como {papel} em {day}!")
    st.rerun()

def remove_name(day, name, role):
    """Remove um nome de uma lista, promovendo jogadores se necessário."""
    day_data = st.session_state.data[day]
    if name in day_data[role]:
        day_data[role].remove(name)
        
        # Lógica de promoção
        if role == "Titulares" and day_data["Reservas"]:
            promoted_reserva = day_data["Reservas"].pop(0)
            day_data["Titulares"].append(promoted_reserva)
            if day_data["Substitutos"]:
                promoted_substituto = day_data["Substitutos"].pop(0)
                day_data["Reservas"].append(promoted_substituto)
        elif role == "Reservas" and day_data["Substitutos"]:
            promoted_substituto = day_data["Substitutos"].pop(0)
            day_data["Reservas"].append(promoted_substituto)
            
    save_data(st.session_state.data, DATA_FILE)
    st.rerun()

def select_quadra(day, quadra):
    """Seleciona uma quadra para um dia específico."""
    st.session_state.quadras[day] = quadra
    save_data(st.session_state.quadras, QUADRAS_FILE)
    st.rerun()

def remove_quadra(day):
    """Remove a quadra de um dia específico."""
    st.session_state.quadras[day] = None
    save_data(st.session_state.quadras, QUADRAS_FILE)
    st.rerun()

def add_mensalista(month, day, name):
    """Adiciona um nome à lista de mensalistas de um mês e dia."""
    if name not in st.session_state.mensalistas[month].get(day, []):
        st.session_state.mensalistas[month][day].append(name)
        st.success(f"Mensalista {name} adicionado ao mês de {month}, dia {day}!")
        save_data(st.session_state.mensalistas, MENSALISTAS_FILE)
        st.rerun()
    else:
        st.warning(f"{name} já é mensalista para {day} de {month}!")

def remove_mensalista(month, day, name):
    """Remove um nome da lista de mensalistas de um mês e dia."""
    if name in st.session_state.mensalistas[month][day]:
        st.session_state.mensalistas[month][day].remove(name)
        save_data(st.session_state.mensalistas, MENSALISTAS_FILE)
        st.rerun()

def exportar_resumo_dia(dia):
    """Gera o texto de resumo de um dia para exportação."""
    dia_data = st.session_state.data[dia]
    quadra = st.session_state.quadras.get(dia, "Não definida")
    if not dia_data['Titulares'] and not dia_data['Reservas'] and not dia_data['Substitutos']:
        return f"Não há jogadores cadastrados para {dia}."
    
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
    texto += f"\n_Atualizado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}_"
    return texto

def exportar_todas_listas():
    """Gera o texto de resumo de todos os dias para exportação."""
    data = st.session_state.data
    quadras = st.session_state.quadras
    texto = "🏐 *LISTA COMPLETA DO VOLEIZINHO* 🏐\n\n"
    has_players = False
    for dia in DIAS_SEMANA:
        dia_data = data[dia]
        if dia_data['Titulares'] or dia_data['Reservas'] or dia_data['Substitutos']:
            has_players = True
            quadra = quadras.get(dia, "Não definida")
            texto += f"*{dia.upper()}* (Quadra: {quadra})\n"
            if dia_data['Titulares']:
                texto += "👉 Titulares:\n" + "\n".join([f"• {nome}" for nome in dia_data['Titulares']]) + "\n"
            if dia_data['Reservas']:
                texto += "🔄 Reservas:\n" + "\n".join([f"• {nome}" for nome in dia_data['Reservas']]) + "\n"
            if dia_data['Substitutos']:
                texto += "⏳ Substitutos:\n" + "\n".join([f"• {nome}" for nome in dia_data['Substitutos']]) + "\n"
            texto += "\n" + "="*30 + "\n\n"
    return texto if has_players else "Nenhum jogador cadastrado em nenhum dia."

# --- Inicialização da Aplicação ---

# Verifica se os dados devem ser resetados
if should_reset():
    reset_week_data()

# Inicializa o estado da sessão com os dados carregados
current_month, next_month = get_current_and_next_month()
default_mensalistas = create_mensalistas_structure(current_month, next_month)
# Carrega os dados de mensalistas e garante que a estrutura de dias da semana está correta
mensalistas_from_file = load_data(MENSALISTAS_FILE, default_mensalistas)
for month in [current_month, next_month]:
    if month not in mensalistas_from_file:
        mensalistas_from_file[month] = {dia: [] for dia in DIAS_SEMANA}
    for day in DIAS_SEMANA:
        if day not in mensalistas_from_file[month]:
            mensalistas_from_file[month][day] = []

if 'data' not in st.session_state:
    default_data = {dia: DIA_ESTRUTURA.copy() for dia in DIAS_SEMANA}
    st.session_state['data'] = load_data(DATA_FILE, default_data)
    
if 'quadras' not in st.session_state:
    default_quadras = {dia: None for dia in DIAS_SEMANA}
    st.session_state['quadras'] = load_data(QUADRAS_FILE, default_quadras)

if 'mensalistas' not in st.session_state:
    st.session_state['mensalistas'] = mensalistas_from_file

# --- Layout Principal com Abas ---

tab1, tab2, tab_mensalistas, tab3 = st.tabs(["Início", "Listas da Semana", "Mensalistas", "Exportar Listas"])

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
            add_name(day, name)
    
    st.divider()

    # Exibição das listas por dia
    tabs_dias = st.tabs(DIAS_SEMANA)
    for tab, day in zip(tabs_dias, DIAS_SEMANA):
        with tab:
            current_quadra = st.session_state.quadras.get(day)
            day_data = st.session_state.data[day]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{day}**")
                
                # Listas de jogadores
                st.write(f"**Titulares ({len(day_data['Titulares'])}/15):**")
                for i, name in enumerate(day_data['Titulares']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_tit_{day}_{name}"):
                        remove_name(day, name, 'Titulares')

                st.write(f"**Reservas ({len(day_data['Reservas'])}/3):**")
                for i, name in enumerate(day_data['Reservas']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_res_{day}_{name}"):
                        remove_name(day, name, 'Reservas')

                st.write("**Substitutos:**")
                for i, name in enumerate(day_data['Substitutos']):
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i+1}. {name}")
                    if cols[1].button("❌", key=f"rem_sub_{day}_{name}"):
                        remove_name(day, name, 'Substitutos')
            
            with col2:
                st.markdown("**Quadra**")
                if current_quadra:
                    st.write(f"Quadra selecionada: **{current_quadra}**")
                    if st.button("❌ Remover", key=f"remove_quadra_{day}"):
                        remove_quadra(day)
                else:
                    quadra_selecionada = st.selectbox(
                        "Selecione a quadra:",
                        options=[""] + QUADRAS_DISPONIVEIS,
                        index=0,
                        key=f"quadra_select_{day}"
                    )
                    if quadra_selecionada and st.button("Selecionar", key=f"select_quadra_{day}"):
                        select_quadra(day, quadra_selecionada)
    
    st.divider()
    # Botão de reset manual com confirmação
    if st.button("Resetar Todas as Listas (Apenas Admin)", key="botao_reset_admin"):
        reset_week_data()

with tab_mensalistas:
    st.title("Mensalistas 💰")
    st.write("Gerencie a lista de mensalistas para os meses atuais e próximos.")

    # Pega os nomes dos meses
    current_month, next_month = get_current_and_next_month()

    # Formulário para adicionar mensalistas
    st.subheader("Adicionar Mensalista")
    new_mensalista_name = st.text_input("Nome do mensalista:", key="new_mensalista_name")
    col_add1, col_add2 = st.columns(2)
    with col_add1:
        month_to_add = st.selectbox(
            "Adicionar para qual mês?",
            options=[current_month, next_month],
            key="month_add_select"
        )
    with col_add2:
        day_to_add = st.selectbox(
            "Adicionar para qual dia?",
            options=DIAS_SEMANA,
            key="day_add_select"
        )

    if st.button("Adicionar Mensalista", key="add_mensalista_button") and new_mensalista_name:
        add_mensalista(month_to_add, day_to_add, new_mensalista_name)

    st.divider()
    
    # Exibir mensalistas do mês atual por dia
    st.subheader(f"Lista de Mensalistas de {current_month}")
    for day in DIAS_SEMANA:
        if st.session_state.mensalistas.get(current_month) and st.session_state.mensalistas[current_month].get(day):
            st.markdown(f"**{day}:**")
            for name in st.session_state.mensalistas[current_month][day]:
                cols = st.columns([4, 1])
                cols[0].write(name)
                if cols[1].button("❌", key=f"rem_mensal_{current_month}_{day}_{name}"):
                    remove_mensalista(current_month, day, name)

    st.divider()
    
    # Exibir mensalistas do próximo mês por dia
    st.subheader(f"Lista de Mensalistas de {next_month}")
    for day in DIAS_SEMANA:
        if st.session_state.mensalistas.get(next_month) and st.session_state.mensalistas[next_month].get(day):
            st.markdown(f"**{day}:**")
            for name in st.session_state.mensalistas[next_month][day]:
                cols = st.columns([4, 1])
                cols[0].write(name)
                if cols[1].button("❌", key=f"rem_mensal_{next_month}_{day}_{name}"):
                    remove_mensalista(next_month, day, name)

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
        st.text_area("Resumo para WhatsApp:", value=resumo, height=300, key="texto_resumo_dia")

    st.divider()

    if st.button("Gerar Lista Completa", key="botao_gerar_completa"):
        lista_completa = exportar_todas_listas()
        st.text_area("Lista Completa para WhatsApp:", value=lista_completa, height=400, key="texto_lista_completa")

