# Restaurant Recommendation Chatbot

In this project, I've developed a serverless, microservice-driven web application.

Specifically, a Restaurant Recommendation chatbot that sends the user restaurant suggestions given a set of preferences that are provided to the chatbot through conversation.

AWS was used in the development of this project and the specific resources used are outlined below:

    - S3
    - API Gateway
    - Lambda
    - Lex
    - SQS
    - SES
    - Elastic Search
    - DynamoDB
    - Yelp API for data sourcing

# Components and Flow

    S3 is used to host the frontend of the web application.
    
    API Gateway is used to connect the frontend with the chatbot. The swagger.yaml file was used to initialize the api.
    
    There are several Lambda functions used in this project. The first is LF1 which acts as an interface between the user and Lex.
    
    The second Lambda function (LF2) validates input from Lex and sends the information to an SQS queue.
    
    Every minute through CloudWatch events the Lambda function LF2 is triggered.
    
    Data from the SQS queue is pulled in order to search for relevant results using Elastic Search.
    
    Detailed information about the restaurants is fetched from DynamoDB.
    
    Finally, an email is constructed with the restaurant recommendations and sent to the user through the SES service.

Data is obtained through the Yelp API and then stored in DynamoDB for quick access. It is then indexed in Elastic Search for searching. The helper functions directory contains the scripts used to accomplish this.
