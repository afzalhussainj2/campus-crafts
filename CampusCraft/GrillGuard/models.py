from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=11, default='', blank=True)

    is_student = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional required fields

    objects = UserManager()

    username = None

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.email
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    groups = None
    user_permissions = None


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name
    
class Waiter(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=11, default='', blank=True)
    tables = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    
class Bill(models.Model):
    waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE)
    table = models.IntegerField(blank=True)
    total = models.IntegerField()
    bill_number = models.CharField(max_length=8, unique=True)
    def __str__(self):
        return str(self.table)
    
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def __str__(self):
        return str(self.product)

class Complain(models.Model):
    against = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_seller': True},  # Restrict to users with is_seller=True
        related_name='complaints_against_seller'  # Unique reverse accessor for sellers
    )
    froom = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_student': True},  # Restrict to users with is_student=True
        related_name='complaints_from_student'  # Unique reverse accessor for students
    )
    complain = models.TextField()
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.complain

