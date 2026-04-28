import resend
from app.workers.celery_app import celery
from app.core.config import settings

@celery.task(name="send_verification_email")
def send_verification_email(email_to: str, user_name: str, token: str):
    resend.api_key = settings.RESEND_API_KEY
    verify_link = f"http://localhost:4200/verify-email?token={token}"
    template_id = settings.VERIFY_EMAIL_TEMPLATE_ID
    
    try:
        params = {
            "from": "IDFLab <onboarding@resend.dev>",
            "to": [email_to],
            "subject": "Verifique seu e-mail - IDFLab",
            "template": {
                "id": template_id,
                "variables": {
                    "user_name": user_name,
                    "verification_link": verify_link,
                },
            },
        }
        
        response = resend.Emails.send(params)
        print(f"✅ Verification email sent to {email_to}. Response: {response}")
        return response
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        raise e