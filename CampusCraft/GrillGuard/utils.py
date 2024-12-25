import random
from django.core.mail import send_mail
import string
from .models import Bill

def otp_generator():
    return random.randint(1000, 9999)

def sending_mail(email, otp):
    send_mail(
        'OTP for password reset',
        f'''
        ......GrillGuard......
        ...Your OTP is {otp} . 
        Warning: 
        Do not share this OTP with anyone. 
        If you did not request this OTP, 
        please ignore this email.
        ''',
        'campuscrafts.apps@gmail.com',
        [email],
        fail_silently=False,
    )
    
def generate_unique_bill_number():
    while True:
        bill_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        if len(bill_number) == 8:
            if not Bill.objects.filter(bill_number=bill_number).exists():
                return bill_number