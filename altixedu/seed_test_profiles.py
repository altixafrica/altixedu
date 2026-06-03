"""
Seed test data for E2E tests - creates student and parent profiles
"""
import os
import sys
import django
from datetime import datetime, date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.students.models import Student, StudentParent
from apps.schools.models import School
from apps.academics.models import AcademicYear, Classroom

User = get_user_model()

# Get the test school
school = School.objects.get(subdomain='atlascollege')
print(f"Using school: {school.name}")

# 1. Create Student Profile for student@atlascollege.test
student_user = User.objects.get(email='student@atlascollege.test')
print(f"\nStudent user: {student_user.email}")

# Update user name to match test expectation
student_user.first_name = 'Ada'
student_user.last_name = 'Okafor'
student_user.save()
print(f"✓ Updated user name to 'Ada Okafor'")

# Check if student profile exists
student_profile = Student.objects.filter(user=student_user).first()
if student_profile:
    print(f"✓ Student profile already exists")
    if student_profile.last_name != 'Okafor':
        student_profile.first_name = 'Ada'
        student_profile.last_name = 'Okafor'
        student_profile.save()
        print(f"✓ Updated student profile name to 'Ada Okafor'")
else:
    # Create student profile
    student_profile = Student.objects.create(
        school=school,
        user=student_user,
        first_name='Ada',  # Match test expectation "Progress overview for Ada"
        last_name='Okafor',
        admission_number=f'STU-{student_user.id}-2024',
        date_of_birth=date(2010, 5, 15),
        gender='female',
        enrollment_date=date(2024, 1, 15),
        status='active',
    )
    print(f"✓ Created student profile for {student_profile.first_name} {student_profile.last_name}")

# 2. Create Parent Profile for parent@atlascollege.test
parent_user = User.objects.get(email='parent@atlascollege.test')
print(f"\nParent user: {parent_user.email}")

# Link parent to student
link = StudentParent.objects.filter(parent=parent_user, student=student_profile).first()
if link:
    print(f"✓ Parent already linked to student")
else:
    StudentParent.objects.create(
        parent=parent_user,
        student=student_profile,
        relationship='mother'
    )
    print(f"✓ Linked parent to student")

# 3. Create some additional students for dashboard content
print("\n=== Creating additional test students ===")

additional_students_data = [
    {'first_name': 'Chioma', 'last_name': 'Okafor', 'admission_number': 'STU-002-2024'},
    {'first_name': 'Tunde', 'last_name': 'Adeyemi', 'admission_number': 'STU-003-2024'},
    {'first_name': 'Zainab', 'last_name': 'Mohammed', 'admission_number': 'STU-004-2024'},
]

for data in additional_students_data:
    existing = Student.objects.filter(admission_number=data['admission_number']).first()
    if existing:
        print(f"✓ {data['first_name']} already exists")
    else:
        student = Student.objects.create(
            school=school,
            first_name=data['first_name'],
            last_name=data['last_name'],
            admission_number=data['admission_number'],
            date_of_birth=date(2010, 1, 1),
            gender='female',
            enrollment_date=date(2024, 1, 15),
            status='active',
        )
        print(f"✓ Created student: {student.first_name} {student.last_name}")

# 4. Check teacher profile for teacher dashboard
teacher_user = User.objects.get(email='teacher@atlascollege.test')
print(f"\nTeacher user: {teacher_user.email}")

from apps.teachers.models import Teacher
teacher_profile = Teacher.objects.filter(user=teacher_user).first()
if teacher_profile:
    print(f"✓ Teacher profile exists")
else:
    print(f"⚠ Teacher profile doesn't exist - creating...")
    teacher_profile = Teacher.objects.create(
        school=school,
        user=teacher_user,
        employment_date=date(2024, 1, 1),
    )
    print(f"✓ Created teacher profile")

print("\n✅ Test data seeding complete!")
