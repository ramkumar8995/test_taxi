from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Trip(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    trip_time = models.DateTimeField(default=now)
    from_place = models.CharField(max_length=255)
    to_place = models.CharField(max_length=255)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_type = models.CharField(
        max_length=50,
        choices=[
            ("Cash", "Cash"),
            ("Card", "Card"),
            ("Paid to Company", "Paid to Company")
        ]
    )
    tip = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.driver.username}: {self.from_place} to {self.to_place} - £{self.fare}"
