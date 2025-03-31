# Função para a página de jogos
def jogos():
    # Carregar dados e limpar dias passados
    st.session_state.volei_agenda = load_data()
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

        # Salva as informações após a alteração
        save_data(st.session_state.volei_agenda)
        st.rerun()

    # Exibição de todas as listas abaixo numeradas
    tabs = st.tabs([f"{i}. {day}" for i, day in enumerate(st.session_state.volei_agenda.keys(), start=1)])
    for tab, (day, data) in zip(tabs, st.session_state.volei_agenda.items()):
        with tab:
            st.text(f"**Titulares** ({len(data['Titulares'])}/15):")
            for i, name in enumerate(data['Titulares']):
                st.write(f"{i+1}. {name}")
                if st.button(f"Remover {name}", key=f"remove_titulares_{day}_{i}"):  # Modificado para garantir chave única
                    remove_name(day, name, 'Titulares')

            st.text(f"**Reservas** ({len(data['Reservas'])}/3):")
            for i, name in enumerate(data['Reservas']):
                st.write(f"{i+1}. {name}")
                if st.button(f"Remover {name}", key=f"remove_reservas_{day}_{i}"):  # Modificado para garantir chave única
                    remove_name(day, name, 'Reservas')

            st.text(f"**Substitutos**:")
            for i, name in enumerate(data['Substitutos']):
                st.write(f"{i+1}. {name}")
                if st.button(f"Remover {name}", key=f"remove_substitutos_{day}_{i}"):  # Modificado para garantir chave única
                    remove_name(day, name, 'Substitutos')

    # Botão de reset (visível só para o administrador)
    if st.button("Resetar Semana (Apenas Admin)"):
        st.session_state.volei_agenda = load_data()  # Carrega os dados iniciais
        save_data(st.session_state.volei_agenda)
        st.success("Listas resetadas!")
        st.rerun()



