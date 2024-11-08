from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CandidateProfile

class BulkCandidateRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    
    # Profile fields
    birth_date = serializers.DateField()
    gender = serializers.ChoiceField(choices=CandidateProfile.GENDER_CHOICES)
    about_me = serializers.CharField(required=False, allow_blank=True)
    specialization = serializers.CharField()
    experience = serializers.IntegerField()
    country = serializers.CharField()
    region = serializers.CharField()
    languages = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    hard_skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    soft_skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    desired_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    search_status = serializers.ChoiceField(choices=CandidateProfile.SEARCH_STATUS_CHOICES)
    relocation_status = serializers.ChoiceField(choices=CandidateProfile.RELOCATION_CHOICES)
    level = serializers.ChoiceField(choices=CandidateProfile.LEVEL_CHOICES)
    
    # Education fields
    education_institution = serializers.CharField()
    education_faculty = serializers.CharField()
    education_degree = serializers.CharField()
    graduation_year = serializers.IntegerField()