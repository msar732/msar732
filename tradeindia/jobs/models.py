from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model

User = get_user_model()

class Company(models.Model):
    """Company profiles for job listings"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='companies/', blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    size = models.CharField(
        max_length=20,
        choices=[
            ('startup', '1-10 employees'),
            ('small', '11-50 employees'),
            ('medium', '51-200 employees'),
            ('large', '201-1000 employees'),
            ('enterprise', '1000+ employees')
        ]
    )
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=200)
    
    # Company verification
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.name

class JobCategory(models.Model):
    CATEGORY_CHOICES = [
        ('it_software', 'IT & Software'),
        ('marketing_sales', 'Marketing & Sales'),
        ('finance_accounting', 'Finance & Accounting'),
        ('engineering', 'Engineering'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education & Training'),
        ('hospitality', 'Hospitality & Tourism'),
        ('construction', 'Construction'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('government', 'Government Jobs'),
        ('freelance', 'Freelance & Part-time'),
        ('other', 'Other Jobs')
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.display_name

class JobListing(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('temporary', 'Temporary')
    ]
    
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('0_1', '0-1 years'),
        ('1_3', '1-3 years'),
        ('3_5', '3-5 years'),
        ('5_10', '5-10 years'),
        ('10_plus', '10+ years')
    ]
    
    SALARY_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('annually', 'Annually'),
        ('hourly', 'Hourly'),
        ('project', 'Per Project'),
        ('negotiable', 'Negotiable')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    
    # Job Details
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    job_description = models.TextField()
    requirements = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    
    # Experience & Education
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    education_required = models.TextField(blank=True)
    skills_required = models.JSONField(default=list, blank=True)
    
    # Salary
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES, default='monthly')
    
    # Location
    location = gis_models.PointField()
    address = models.TextField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)
    
    # Application Details
    application_deadline = models.DateField(null=True, blank=True)
    positions_available = models.PositiveIntegerField(default=1)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('filled', 'Position Filled'),
            ('expired', 'Expired'),
            ('paused', 'Paused')
        ],
        default='active'
    )
    
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['salary_min', 'salary_max']),
        ]
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class JobApplication(models.Model):
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    
    class Meta:
        unique_together = ['job', 'applicant']

class JobAlert(models.Model):
    """Job alerts for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_name = models.CharField(max_length=100)
    keywords = models.CharField(max_length=500)
    categories = models.ManyToManyField(JobCategory)
    location = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    experience_level = models.CharField(max_length=20, choices=JobListing.EXPERIENCE_CHOICES, blank=True)
    job_type = models.CharField(max_length=20, choices=JobListing.JOB_TYPE_CHOICES, blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediately'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly')
        ],
        default='daily'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.alert_name}"