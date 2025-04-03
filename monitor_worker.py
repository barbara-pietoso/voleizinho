import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from twilio.rest import Client

# Configurações do Twilio


# Caminho do arquivo JSON
JSON_FILE_PATH = r'C:\Users\mateus\Documents\Projetos\voleizinho\volei_agenda.json'

# Função para enviar mensagens pelo Twilio
client = Client(ACCOUNT_SID, AUTH_TOKEN)

def enviar_mensagem_twilio(mensagem):
    content_message = json.dumps({"1": mensagem})
    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        content_sid='HX04f53b8e134d73751f8a4c55a36ec7e3',
        content_variables=content_message,
        # body=mensagem,
        to=DESTINATION_NUMBER
    )

def obter_lista_presenca():
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    mensagens = []
    for dia, info in data.items():
        confirmados = info.get("Titulares", [])
        if confirmados:
            mensagem = f"\n\n*{dia}*\nConfirmados:\n " + "\n ".join(confirmados)
            mensagens.append(mensagem)
    return "".join(mensagens)

class MonitorJSON(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("volei_agenda.json"):
            print("Arquivo JSON modificado! Atualizando presença...")
            mensagem = obter_lista_presenca()
            if mensagem:
                enviar_mensagem_twilio(mensagem)

if __name__ == "__main__":
    event_handler = MonitorJSON()
    observer = Observer()
    observer.schedule(event_handler, path=r'C:\Users\mateus\Documents\Projetos\voleizinho', recursive=False)
    observer.start()
    print("Monitorando alterações no JSON...")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()