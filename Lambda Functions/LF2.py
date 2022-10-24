import json
import boto3
import os
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests
import sys
import subprocess

# pip install custom package to /tmp/ and add to path
subprocess.call('pip install opensearch-py -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sys.path.insert(1, '/tmp/')

from opensearchpy import OpenSearch, RequestsHttpConnection

# Initialize clients
session = boto3.Session(region_name="us-east-1")
ses_client = session.client('ses')
sqs = boto3.client('sqs')



def receive_message(sqs_queue_url):
    
    response = sqs.receive_message(
        
        QueueUrl=sqs_queue_url,
        
        MaxNumberOfMessages=1,
        
        WaitTimeSeconds=10,
    )
    
    message = response.get('Messages', [])[0]
    
    receipt_handle = response.get('Messages', [])[0]['ReceiptHandle']
    
    sqs.delete_message(QueueUrl=sqs_queue_url, ReceiptHandle=receipt_handle)
    
    return message



def send_email(email, text):
    
    from_email = 'jakenemiroff@gmail.com'
    
    body_html = f"""<html>
        <head></head>
        <body>
          <p>Hi There, here are your list of recommended restaurants:</p> 
        </body>
        </html>
                    """
    
    body_html = text

    email_message = {
        'Body': {
            'Html': {
                'Charset': 'utf-8',
                'Data': body_html,
            },
        },
        'Subject': {
            'Charset': 'utf-8',
            'Data': "Email From Concierge ChatBot",
        },
    }

    ses_response = ses_client.send_email(
        
        Destination={
        
            'ToAddresses': [email],
        },
        
        Message=email_message,
        
        Source=from_email
    )



def get_restaurant_details(business_id):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    table = dynamodb.Table('yelp-restaurants')
    
    response = table.query(KeyConditionExpression=Key('Business_ID').eq(business_id))
    
    items = response['Items']
    
    return items


def get_random_restaurant(cuisine, size):
    
    host = 'search-restaurants-ztrhgbms72vkxeodfbhyzfv5dm.us-east-1.es.amazonaws.com'
    auth = ('jrn8168', 'NQ7OOpet02sbFD3%GQ3zsI&MdorhFMS')
    
    client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
    )
    
    query = {
        "size": size,
        "query": {"match": {"Cuisine": cuisine}}
    }
    
    index = 'restaurants'
    
    response = client.search(
        body = query,
        index = index
    )
    
    
    restaurant_ids = []
    restaurants = response['hits']['hits']
    
    for restaurant in restaurants:
        restaurant_ids.append(restaurant['_source']['Business_ID'])
        
    return restaurant_ids


    
def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    # get all requests from the SQS queue
    sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/502659756548/Q1'

    msgs = receive_message(sqs_queue_url)

    # send sms
    if msgs:
        
        msg = json.loads(msgs['Body'])
        
        cuisine = msg['cuisine']
        numPeople = msg['numPeople']
        diningTime = msg['time']
        email = msg['email']

        text = 'Hello! Here are my ' + cuisine + ' restaurant suggestions for ' + str(numPeople) + ' people, for today at ' + diningTime
        
        restaurant_ids = get_random_restaurant(cuisine, 3)

        for i, restaurant_id in enumerate(restaurant_ids):
            
            restaurant = get_restaurant_details(restaurant_id)[0]
            
            name = restaurant['Name']
            
            address = restaurant['Address']
            
            text += '\n' + str(i + 1) + ': ' + name + ' located at ' + address
            
        text += '\nEnjoy your meal!'

        
        send_email(email, text)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    