import json
import boto3
from botocore.exceptions import ClientError
from string import Template

REQUEST_RECIPIENT = "prabhav@parashar.dev"

def read_template(template_path):
    with open(template_path) as template:
        return template.read()

def render(template_path, **kwargs):
    return Template(
        read_template(template_path)
    ).substitute(**kwargs)

def send_email_SES(companyName, html):
    client = boto3.client('ses', region_name="us-east-1")
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    REQUEST_RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': html,
                    }
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': f"New RFQ submitted to web portal | Company: {companyName}",
                },
            },
            Source="RFQ Sender <prabhav@parashar.dev>",
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        return True

def lambda_handler(event, context):
    template_data = {
        'emailAddress': event['emailAddress'],
        'fullname': event['fullname'],
        'phoneNumber': event['phoneNumber'],
        'companyName': event['companyName'],
        'commentSection': event['commentSection']
    }

    render_result = render('email_template.html', **template_data)

    email_result = send_email_SES(template_data['companyName'], render_result)

    if email_result is True:
        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'body': json.dumps({
                        'status': 'success',
                        'message': 'A Developer will be in contact with you shortly'
                    })
        }
    else:
        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'body': json.dumps({
                        'status': 'failed',
                        'message': 'Request for Quote failed to send, try again later'
                    })
        }
