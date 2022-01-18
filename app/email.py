from flask import render_template
from flask_mail import Message

from app import app, mail, celery


@celery.task(bind=True)
def send_email(self, recipient, subject, template, **kwargs):
    with app.app_context():
        msg = Message(
            app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
            sender=app.config['EMAIL_SENDER'],
            recipients=[recipient])
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        mail.send(msg)
