from datetime import timedelta
import secrets
import string

from django.utils import timezone
from user.models import OTPCodeModel


class OTPService:
    def __init__(self, phone_number, purpose):
        self.phone_number = phone_number
        self.purpose = purpose

    def generate_code(self):
        code = "".join(secrets.choice(string.digits) for _ in range(6))
        otp_user = OTPCodeModel.objects.filter(
            phone_number=self.phone_number, purpose=self.purpose
        ).first()

        if otp_user and (
            otp_user.otp_validation()
            or timezone.now() < otp_user.last_sent_at + timedelta(minutes=3)
        ):
            return False, "Please wait before requesting a new code"

        OTPCodeModel.objects.update_or_create(
            phone_number=self.phone_number,
            purpose=self.purpose,
            defaults={
                "code_hash": code,
                "attempts": 0,
                "is_used": False,
                "last_sent_at": timezone.now(),
            },
        )
        return True, code

    def verify_code(self, code):

        otp = OTPCodeModel.objects.filter(
            phone_number=self.phone_number, purpose=self.purpose
        ).first()

        if not otp:
            return False, "Invalid code"

        if not otp.otp_validation():
            return False, "OTP expired or too many attempts"

        if code != otp.code_hash: 
            otp.attempts += 1
            otp.save(update_fields=["attempts"])

            return False, "Invalid code"

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        return True, "OTP verified"
