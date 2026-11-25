from decimal import Decimal
import json

def response(status_code, body):
    """Bygger ett HTTP-svar för API Gateway."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body, cls=DecimalEncoder)  # Använder DecimalEncoder för att hantera Decimal-objekt
    }

# Hantera Decimal från DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)