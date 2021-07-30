import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, Email, Content

def send_email(recipient_address, universe_key):
    from_email = Email('therealsoccersim@gmail.com')
    to_email = To(recipient_address)
    subject = 'Simulation {} complete!'.format(universe_key)
    content = Content('text/html', 'Your simulation has just completed!\n\nCheck it out <a href="soccer-sim.herokuapp.com/simulation/{}">here</a>\n\nYours, Soccer Sim'.format(universe_key))
    message = Mail(from_email, to_email, subject, content)
    try:
        sg = SendGridAPIClient(api_key = os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
