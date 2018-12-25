"""Send email with MailGun."""
import requests


def get_api_key():
    """Load API key."""
    api_key_file = open('mailgun_api_key.txt', 'r')
    api_key = api_key_file.read()
    api_key_file.close()

    return api_key.strip()


def send_simple_message(subject, body):
    """Send e-mail notification."""
    api_key = get_api_key()

    return requests.post(
        "https://api.mailgun.net/v3/sandboxa313a26c7b2844958ec9d2e253f4f306.mailgun.org/messages",
        auth=("api", api_key),
        data={"from": "Mailgun Sandbox <postmaster@sandboxa313a26c7b2844958ec9d2e253f4f306.mailgun.org>",
              "o:testmode": False,
              "to": "Fernando Serrano <nandosb@gmail.com>",
              "subject": subject,
              "text": body}
    )
