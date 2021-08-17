import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, Email, Content

def send_email(recipient_address, universe_key):
    from_email = Email('therealsoccersim@gmail.com')
    to_email = To(recipient_address)
    subject = 'Your Soccer Simulation is complete!'.format(universe_key)
    content = Content('text/html', 'Dear {},<br>Your Soccer Simulation (universe key <b>{}</b>) is complete!<br>Check it out <a href="soccer-sim.herokuapp.com/simulation/{}">here</a><br>Yours, Soccer Sim'.format(recipient_address, universe_key, universe_key))
    message = Mail(from_email, to_email, subject, content)
    try:
        sg = SendGridAPIClient(api_key = os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
