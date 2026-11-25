"""Event consumer handler."""
import os

import boto3

# Initialize the SNS client to send notifications
sns = boto3.client('sns', region_name='eu-north-1')

TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

def lambda_handler(event, context):
    event_type = event.get("detail-type") or event.get("DetailType")
    order = event.get("detail")
    if not isinstance(order, dict):
        raise ValueError("Event must contain an order object in 'detail'")

    order_id = order["orderId"]
    book = order["book"]

    if event_type == "OrderPlaced":
        notification = (
            f"Hej bästa {order['customerId']}! \n\n"
            f"Din beställning med order id {order['orderId']} har mottagits. \n\n"
            f"Du har beställt {book} för {order['price']} kr. \n"
            f"Beställningen lades {order['time']}. \n\n"
            f"Tack för din beställning!"
        )
        subject = "Orderbekräftelse - tack för din beställning!"
    elif event_type == "OrderCancelled":
        notification = (
            f"Hej {order['customerId']}! Din beställning {order_id} av {book} har avbokats."
        )
        subject = "Din beställning har avbokats"
    else:
        raise ValueError(f"Unsupported event type: {event_type!r}")

    print(f"Received {event_type} event for order {order_id}")

    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=notification,
        Subject=subject,
    )

    print(f"SNS notification sent for {event_type} event")
    
    return {"success": True, "eventType": event_type}