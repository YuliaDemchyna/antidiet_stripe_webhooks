import os

from sendgrid import GroupsToDisplay, GroupId, Asm, Mail, Personalization, Email, SendGridAPIClient

sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

#example code for use with template to send to multiple users
def send_bulk_email(users):

    message = Mail(
        from_email='example@anti.diet',
    )
    message.template_id = 'template_id_found_in_sendgrid'
    message.asm = Asm(
        group_id=GroupId(1), # unsubscribe groups
        groups_to_display=GroupsToDisplay([1, 1]) # all unsubscribe groups
    )

    for user in users: # sends to multitple users at once
        email, first_name = user
        if not email or not email.strip() or not first_name or not first_name.strip():
            continue
        personalization = Personalization()
        personalization.add_to(Email(email))
        personalization.dynamic_template_data = {
            'first_name': first_name,
            'subject': f"Hey {first_name}, thanks for joining Anti Diet"
        }
        message.add_personalization(personalization)

    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)