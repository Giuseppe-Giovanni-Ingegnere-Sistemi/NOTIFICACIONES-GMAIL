import os.path
import time
import base64
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Si modificas estos alcances, borra el archivo token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Autentica con la API de Gmail."""
    creds = None
    # El archivo token.pickle almacena las credenciales de usuario.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si no existen credenciales válidas, inicia el flujo de autenticación
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def check_emails(service, query='subject:invitation'):
    """Chequea los correos que coincidan con la query dada."""
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No se encontraron correos.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            msg_snippet = msg['snippet']
            print(f"Nuevo correo encontrado: {msg_snippet[:100]}...")
            # Aquí podrías agregar la lógica de alarma, por ejemplo, enviando una notificación

def main():
    service = authenticate_gmail()
    
    while True:
        print('Chequeando correos...')
        check_emails(service)
        time.sleep(60)  # Cada minuto revisa el correo

if __name__ == '__main__':
    main()
