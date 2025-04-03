# Projeto Voleizinho

## Descrição
Este projeto é uma aplicação para gerenciar listas de presença para jogos de vôlei, utilizando Streamlit para a interface e Twilio para enviar notificações via WhatsApp.

## Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes do Python)

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/voleizinho.git
cd voleizinho
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
```
### 3. Ative o ambiente virtual
```bash 
.\venv\Scripts\activate
```
### 4. Instale as dependências
```bash 
pip install -r requirements.txt
```

## Execução

### 1. Execute o monitoramento de alterações no JSON
```bash
python monitor_twilio.py
``` 

### 2. Execute a aplicação Streamlit
```bash
streamlit run app.py
```

## Observações 
* Certifique-se de que o arquivo JSON (volei_agenda.json) está no caminho seu caminho local correto e com as permissões adequadas para teste.