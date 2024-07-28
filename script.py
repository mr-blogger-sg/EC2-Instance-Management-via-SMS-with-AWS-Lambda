import json
import boto3

ec2_client = boto3.client('ec2')
sns_client = boto3.client('sns')

INSTANCE_ID = 'i-1234567890abcdef0'  # Replace with your EC2 instance ID

def lambda_handler(event, context):
    try:
        # Parse incoming SMS message from SNS
        message = event['Records'][0]['Sns']['Message']
        action = message.strip().lower()  # Get the action from the SMS message
        
        # Determine the current state of the EC2 instance
        response = ec2_client.describe_instances(InstanceIds=[INSTANCE_ID])
        instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
        
        if action == 'start':
            if instance_state == 'stopped':
                # Start the instance if it is stopped
                ec2_client.start_instances(InstanceIds=[INSTANCE_ID])
                response_message = f'EC2 instance {INSTANCE_ID} is starting.'
            else:
                response_message = f'EC2 instance {INSTANCE_ID} is already running.'
        
        elif action == 'stop':
            if instance_state == 'running':
                # Stop the instance if it is running
                ec2_client.stop_instances(InstanceIds=[INSTANCE_ID])
                response_message = f'EC2 instance {INSTANCE_ID} is stopping.'
            else:
                response_message = f'EC2 instance {INSTANCE_ID} is already stopped.'
        
        else:
            response_message = 'Invalid command. Please send "start" or "stop".'
        
        # Send a response back to SNS
        sns_client.publish(
            TopicArn='arn:aws:sns:your-region:your-account-id:start-ec2-sms',  # Replace with your SNS Topic ARN
            Message=response_message,
            Subject='EC2 Instance Status'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_message)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error')
        }
