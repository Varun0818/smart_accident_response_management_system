from django.db import models

class AccidentReport(models.Model):
    SEVERITY_CHOICES = [
        ('Minor', 'Minor'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('alerted', 'Alerted'),
        ('enroute', 'En Route'),
        ('resolved', 'Resolved'),
    ]
    
    reporter_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    image = models.ImageField(upload_to='accident_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='reported')
    timestamp = models.DateTimeField(auto_now_add=True)
    assigned_hospital = models.CharField(max_length=100, blank=True, null=True)
    live_distance_km = models.FloatField(blank=True, null=True)
    eta_min = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.reporter_name} - {self.severity} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"