# EC2 Instance Management via SMS with AWS Lambda

## Overview

This project demonstrates how to automate the management of AWS EC2 instances using SMS messages. By leveraging AWS services, specifically Amazon Pinpoint, SNS (Simple Notification Service), and AWS Lambda, this solution allows you to start or stop EC2 instances simply by sending an SMS message.

<img width="1145" alt="Screenshot 2024-07-28 at 4 17 56 PM" src="https://github.com/user-attachments/assets/c8eb8ae6-2aad-4a4a-9dba-aa9a667717c5">


## Architecture

1. **Amazon Pinpoint**: Handles incoming SMS messages and routes them to an SNS topic.
2. **Amazon SNS**: Receives messages from Pinpoint and triggers an AWS Lambda function.
3. **AWS Lambda**: Processes the SMS messages to start or stop the EC2 instance based on the received command.

## Features

- Start and stop EC2 instances via SMS commands.
- Notify about the action taken through SNS.

## Getting Started

### Prerequisites

- AWS Account
- IAM Role with appropriate permissions
- EC2 Instance
- SMS-capable phone number (managed by Amazon Pinpoint)

### Setup Instructions

1. **Create an SNS Topic**

   Go to the [SNS Console](https://console.aws.amazon.com/sns) and create a new topic:
   - Choose "Standard" as the type.
   - Name the topic (e.g., `start-ec2-sms`).
   - Create the topic and note the ARN.

![start-ec2-sms-Topics-Simple-Notification-Service-us-east-2](https://github.com/user-attachments/assets/04003ff2-b9c6-4811-8873-404ce490441a)


2. **Create an IAM Role**

   Go to the [IAM Console](https://console.aws.amazon.com/iam) and create a new role:
   - Choose "Lambda" as the trusted entity type.
   - Attach the following policies:
     - `AmazonSNSReadOnlyAccess`
     - `AmazonEC2FullAccess`
     - `AWSLambdaBasicExecutionRole`
   - Name the role (e.g., `LambdaEC2SNSRole`) and create it.

![LambdaEC2SNSRole-IAM-Global](https://github.com/user-attachments/assets/c2370253-242a-4ca9-8de0-91ec5fda12a0)


3. **Create the Lambda Function**

   Go to the [Lambda Console](https://console.aws.amazon.com/lambda) and create a new function:
   - Author from scratch.
   - Name the function (e.g., `startEC2Instance`).
   - Choose Python 3.x as the runtime.
   - Attach the IAM role created earlier.
   - Add an SNS trigger and select the SNS topic created in Step 1.

![startEC2Instance-Functions-Lambda](https://github.com/user-attachments/assets/5f4442ff-a806-4140-9ab6-7608a9e86e0d)


4. **Set Up Amazon Pinpoint**

   Go to the [Pinpoint Console](https://console.aws.amazon.com/pinpoint) and create a new project:
   - Request a phone number for SMS.
   - Enable two-way SMS and configure it to route messages to the SNS topic.

5. **Deploy the Lambda Function Code**

   Use the following Python script in your Lambda function:

   ```python
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
   ```

6. **Test the Setup**

   - Send SMS commands like "start" or "stop" to the phone number provided by Amazon Pinpoint.
   - Check CloudWatch logs to verify the Lambda function's activity and the EC2 instance's state changes.

## Notes

- Replace `INSTANCE_ID` with your actual EC2 instance ID.
- Update `TopicArn` with your SNS topic ARN.
- Ensure your IAM role has the necessary permissions.
