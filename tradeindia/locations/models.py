from django.db import models


class State(models.Model):
    """Model for Indian states and union territories"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  # State code like 'MH', 'DL'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return self.name


class District(models.Model):
    """Model for districts within states"""
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    code = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'state']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['state', 'name']),
        ]

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class City(models.Model):
    """Model for cities within districts"""
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='cities')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'district']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['district', 'name']),
            models.Index(fields=['state', 'name']),
            models.Index(fields=['pincode']),
        ]

    def __str__(self):
        return f"{self.name}, {self.district.name}, {self.state.name}"