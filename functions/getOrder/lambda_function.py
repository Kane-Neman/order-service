import boto3
from boto3.dynamodb.conditions import Key

from functions.utils.responses import response

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


def lambda_handler(event, context):
    customer_id = f"CUSTOMER#{event['pathParameters']['customerId']}"

    print("Customer ID:", customer_id)

    result = table.query(
        KeyConditionExpression=Key("customerId").eq(customer_id)
    )

    orders = result.get("Items", [])
    
    print(orders)

    if not orders:
        return response(404, {"message": "No orders found"})

    return response(200, orders)

