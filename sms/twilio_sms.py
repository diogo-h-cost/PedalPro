from twilio.rest import Client

def send_sms(mensagem: str, number_dest: str):
    account = '#####'
    token = '#####'
    phone_twilio = '#####'
    client = Client(account, token)
    try:
        sms = client.messages.create(
            from_ = phone_twilio,
            body = mensagem,
            to = number_dest
        )
        print(f"Mensagem enviada com sucesso! SID: {sms.sid}")
    except Exception as e:
        print(f"Falha ao enviar SMS: {e}")