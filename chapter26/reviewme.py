import json
import os
import sys, hashlib


def process_payment(event, context):
    # 1. String constants violation — inline strings not extracted
    status = "processing"
    error_msg = "Payment failed"

    # 2. Security — hardcoded secret
    api_key = "fakesecretkey"

    # 3. Security — eval with user input
    amount = eval(event.get("body", "0"))

    # 4. Error handling — bare except
    try:
        result = int(event.get("queryStringParameters", {}).get("amount"))
    except:
        result = 0

    # 5. Error handling — silenced exception
    try:
        data = json.loads(event.get("body", "{}"))
    except Exception:
        pass

    # 6. No type hints on function
    # 7. Missing CORS headers and proper response format
    return {"statusCode": 200, "body": "ok"}


def validate_user(name, email, age, role, department, level, team, org):
    # 8. Structure — deeply nested (>3 levels)
    if name:
        if email:
            if age:
                if role:
                    if department:
                        return True
    return False


def generate_report(event, context):
    # 9. Structure — function over 30 lines with inline strings
    title = "Monthly Report"
    subtitle = "Generated automatically"
    header = "Section 1"
    footer = "End of report"
    disclaimer = "This report is confidential"
    separator = "---"
    line1 = "Revenue increased by 10%"
    line2 = "Costs decreased by 5%"
    line3 = "Profit margin improved"
    line4 = "Customer satisfaction up"
    line5 = "Employee retention stable"
    line6 = "New markets explored"
    line7 = "Product launches successful"
    line8 = "Technical debt reduced"
    line9 = "Infrastructure costs optimized"
    line10 = "Security posture improved"
    line11 = "Compliance requirements met"
    line12 = "Training programs expanded"
    line13 = "Partnerships established"
    line14 = "Innovation pipeline growing"
    line15 = "Sustainability goals on track"
    line16 = "Brand awareness increased"
    line17 = "Market share expanded"
    line18 = "Customer churn reduced"
    line19 = "Operational efficiency up"
    line20 = "Quality metrics improved"

    body = json.dumps({
        "title": title,
        "lines": [line1, line2, line3, line4, line5, line6, line7, line8,
                  line9, line10, line11, line12, line13, line14, line15,
                  line16, line17, line18, line19, line20]
    })

    return {"statusCode": 200, "body": body}


# 10. Lambda-specific — wrong handler signature
def handle_request(req):
    msg = "Hello from handler"
    return {"statusCode": 200, "body": msg}
