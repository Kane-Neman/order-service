"""Event producer create order."""
import json
from random import randint
from unittest import result
import boto3
from datetime import datetime
from functions.utils.responses import response

# Initialize the EventBridge client
client = boto3.client('events', region_name='eu-north-1')

#Initialize the DynamoDB resource and specify the table name
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")

def lambda_handler(event, context):
    
    #{customerId: "CUSTOMER#1234", book: "Sagan om ringen", author: "J.R.R. Tolkien", price: 10.99}
    
    # Parse the incoming event
    order = json.loads(event["body"])
    customer_id = order["customerId"]
    order_id = generate_order_id()

    item = {
            "customerId": customer_id,
            "orderId": order_id,
            "book": order["book"],
            "author": order["author"],
            "price": order["price"],
            "time": str(datetime.now())
    }

    table.put_item(Item=item)
    

    
    # Create the event to be sent
    event_to_send = [
        {
            "Source": "orders.service",
            "DetailType": "OrderPlaced",
            "Detail": json.dumps(item),
            "EventBusName": "default"
        }
    ]
    
    # Put the event on the event bus
    result = client.put_events(Entries=event_to_send)
    print("EventBridge response:", result)

    if result["FailedEntryCount"] > 0:
        print("Failed to send event:", result["Entries"])

    body = {
        "Success": True,
        "Message": "Order placed"
    }

    print("Event sent to EventBridge", event_to_send)

    return response(200, body)  

# Generate a random order ID.
def generate_order_id():
    return f"ORDER#{randint(1000, 9999)}" 