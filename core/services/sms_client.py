import http.client
import json
from dataclasses import dataclass
from textwrap import dedent
from urllib.parse import urlencode

from django.conf import settings


class SMSMessages:
    WELCOME = text = dedent("""\
            به فراتابش خوش آمدید. 🤍

            از اینکه ما را برای انتخاب کیف خود انتخاب کرده‌اید، خوشحالیم.

            در فراتابش تلاش می‌کنیم کیفیت، طراحی و تجربه‌ای متفاوت را در اختیار شما قرار دهیم.

            ✨ انتخابی برای خاص‌ پسندان

            FARATABESH
        """)


@dataclass
class SmsParameters:
    name: str
    value: str


class SMSIRClient:
    def __init__(self):
        self.base_url = "api.sms.ir"

    def send_verification_code(
        self, phone_number: str, template_id: int, parameters: list[SmsParameters]
    ):
        payload = {
            "mobile": phone_number,
            "templateId": template_id,
            "parameters": [param for param in parameters],
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "X-API-KEY": settings.SMS_API_KEY,
        }

        payload_json = json.dumps(payload)

        try:
            conn = http.client.HTTPSConnection(self.base_url)
            conn.request("POST", "/v1/send/verify", payload_json, headers)
            response = conn.getresponse()
            data = response.read()
            print(data.decode("utf-8"))
            conn.close()
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    def send_sms(self, mobile: str, message_text: str):
        conn = http.client.HTTPSConnection(self.base_url)
        payload = ""
        headers = {"Accept": "text/plain"}
        params = {
            "username": settings.SMS_USERNAME,
            "password": settings.SMS_API_KEY,
            "mobile": mobile,
            "line": settings.SMS_LINE,
            "text": message_text,
        }
        query_string = urlencode(params)

        conn.request(
            "GET",
            f"/v1/send?{query_string}",
            payload,
            headers,
        )
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
