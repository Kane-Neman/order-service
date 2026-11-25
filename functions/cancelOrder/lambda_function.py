import json
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
from functions.utils.responses import response

# Initialize the EventBridge client
client = boto3.client('events', region_name='eu-north-1')

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


def lambda_handler(event, context):
    path_parameters = event.get("pathParameters") or {}
    customer_id = path_parameters.get("customerId")
    order_id = path_parameters.get("orderId")

    if not customer_id or not order_id:
        return response(
            400,
            {"message": "Both customerId and orderId path parameters are required"},
        )

    try:
        result = table.update_item(
            Key={
                "customerId": customer_id,
                "orderId": order_id,
            },
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": "cancelled"},
            ConditionExpression="attribute_exists(customerId) AND attribute_exists(orderId)",
            ReturnValues="ALL_NEW",
        )
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return response(404, {"message": "Order not found"})
        raise

    cancelled_order = result["Attributes"]
    event_to_send = [
        {
            "Source": "orders.service",
            "DetailType": "OrderCancelled",
            "Detail": json.dumps(cancelled_order, cls=DecimalEncoder),
            "EventBusName": "default",
        }
    ]

    event_result = client.put_events(Entries=event_to_send)
    
    if event_result.get("FailedEntryCount", 0) > 0:
        failed_entries = [
            entry for entry in event_result.get("Entries", [])
            if entry.get("ErrorCode")
        ]
        print("Failed to publish order cancellation event:", failed_entries)
        return response(
            502,
            {
                "message": "Order was cancelled, but its event could not be published",
                "order": cancelled_order,
            },
        )

    print("Order cancellation event sent to EventBridge", event_to_send)

    return response(
        200,
        {
            "success": True,
            "message": "Order cancelled",
            "order": cancelled_order,
        },
    )

# Hantera Decimal från DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)