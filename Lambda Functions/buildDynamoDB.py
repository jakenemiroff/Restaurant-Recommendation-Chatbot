from __future__ import print_function # Python 2/3 compatibility
import boto3
import csv
import time

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("yelp-restaurants")
# print(table.table_status)

# table = dynamodb.create_table(
#     TableName='yelp-restaurants',
#     KeySchema=[
#         {
#             'AttributeName': 'Business_ID',
#             'KeyType': 'HASH'
#         },
#         {
#             'AttributeName': 'insertedAtTimestamp',
#             'KeyType': 'RANGE'
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'Business_ID',
#             'AttributeType': 'S'
#         },
#         {
#             'AttributeName': 'insertedAtTimestamp',
#             'AttributeType': 'S'
#         },
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 5,
#         'WriteCapacityUnits': 5
#     }
# )

def lambda_handler(event, context):
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    print('bucket', bucket)
    csv_file_name = event['Records'][0]['s3']['object']['key']
    print('filename', csv_file_name)
    
    csv_object = s3.get_object(Bucket=bucket, Key=csv_file_name)
    
    print(csv_object)
    file_reader = csv_object['Body'].read().decode("utf-8")
    restaurants = file_reader.split("\n")
    restaurants = list(filter(None, restaurants))
    
    print(restaurants)
    
    for restaurant in restaurants:
        
        restaurant_data = restaurant.split(",")
        
        if restaurant_data[3] != 'Coordinates':
            split_lat_long = restaurant_data[3].split(':')
            restaurant_data[3] = split_lat_long[0] + ', ' + split_lat_long[1]
        
        # print('cuisine, ', restaurant_data[7])
        # print('Business_ID, ', restaurant_data[0])
        # print('Name, ', restaurant_data[1])
        # print('Address, ', restaurant_data[2])
        # print('Coordinates, ', restaurant_data[3])
        # print('Num_of_Reviews, ', restaurant_data[4])
        # print('Rating, ', restaurant_data[5])
        # print('Zip_Code, ', restaurant_data[6])
        
        table.put_item(Item={
            'insertedAtTimestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'cuisine': restaurant_data[7],
            'Business_ID': restaurant_data[0],
            'Name': restaurant_data[1],
            'Address': restaurant_data[2],
            'Coordinates': restaurant_data[3],
            'Num_of_Reviews':restaurant_data[4],
            'Rating':restaurant_data[5],
            'Zip_Code':restaurant_data[6]
        })
        
    return 'success'
