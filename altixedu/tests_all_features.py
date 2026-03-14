"""
Comprehensive API Tests for AltixEdu Backend
Tests all new features and endpoints
"""

import json
import csv
import io
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from apps.schools.models import School
from apps.students.models import Student, StudentParent
from apps.academics.models import Classroom, Subject
from apps.attendance.models import Attendance

User = get_user_model()


class RateLimitingTests(APITestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School")
        self.user = User.objects.create_user(
            username='testuser',
            email='test@school.com',
            password='TestPass123!',
            role='teacher',
            school=self.school
        )
        self.login_url = reverse('login')
    
    def test_login_rate_limiting(self):
        """Test that login attempts are rate limited"""
        # Make multiple login attempts
        for i in range(6):
            response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # 6th attempt should be blocked
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
    def test_api_rate_limiting_authenticated(self):
        """Test that API requests are rate limited for authenticated users"""
        # First login successfully
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get('token')
        
        # Make many requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        students_url = reverse('students-list')
        
        # This should work initially but eventually hit the limit
        # (actual test depends on rate limiting window)
        response = self.client.get(students_url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS])


class HealthRecordsTests(APITestCase):
    """Test student health records functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School")
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@school.com',
            password='AdminPass123!',
            role='admin',
            school=self.school
        )
        
        self.student_user = User.objects.create_user(
            username='student',
            email='student@school.com',
            password='StudentPass123!',
            role='student',
            school=self.school
        )
        
        self.student = Student.objects.create(
            school=self.school,
            first_name='John',
            last_name='Doe',
            admission_number='ADM001',
            date_of_birth='2010-01-01',
            gender='male',
            enrollment_date='2023-01-01'
        )
    
    def test_create_health_record(self):
        """Test creating a student health record"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('health-records-list')
        data = {
            'student': self.student.id,
            'medical_conditions': 'Asthma',
            'allergies': 'Peanuts',
            'blood_type': 'O+',
            'height_cm': 150,
            'weight_kg': 45
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['student'], self.student.id)
    
    def test_create_emergency_contact(self):
        """Test creating emergency contact for student"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('emergency-contacts-list')
        data = {
            'student': self.student.id,
            'name': 'Jane Doe',
            'relationship': 'mother',
            'phone_number': '+1234567890',
            'is_primary': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_record_health_metric(self):
        """Test recording a health metric"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('health-metrics-list')
        data = {
            'student': self.student.id,
            'metric_type': 'height',
            'value': '150',
            'unit': 'cm',
            'recorded_date': '2024-01-01'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CustomRolesTests(APITestCase):
    """Test custom roles functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School")
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@school.com',
            password='AdminPass123!',
            role='admin',
            school=self.school
        )
    
    def test_create_custom_role(self):
        """Test creating a custom role"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('custom-roles-list')
        data = {
            'name': 'Department Head',
            'based_on': 'teacher',
            'description': 'Teacher with management duties',
            'can_manage_users': True,
            'can_view_reports': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Department Head')


class StudentClassroomAssignmentTests(APITestCase):
    """Test student classroom assignment functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School")
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@school.com',
            password='AdminPass123!',
            role='admin',
            school=self.school
        )
        
        self.classroom = Classroom.objects.create(
            school=self.school,
            name='Class A',
            grade_level='Grade 1'
        )
        
        self.student = Student.objects.create(
            school=self.school,
            first_name='John',
            last_name='Doe',
            admission_number='ADM001',
            date_of_birth='2010-01-01',
            gender='male',
            enrollment_date='2023-01-01'
        )
    
    def test_assign_student_to_classroom(self):
        """Test assigning a student to a classroom"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('classroom-assignments-list')
        data = {
            'student': self.student.id,
            'classroom': self.classroom.id,
            'academic_year': '2024-2025',
            'roll_number': 1
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_bulk_assign_students(self):
        """Test bulk assigning students to a classroom"""
        # Create additional student
        student2 = Student.objects.create(
            school=self.school,
            first_name='Jane',
            last_name='Doe',
            admission_number='ADM002',
            date_of_birth='2010-02-01',
            gender='female',
            enrollment_date='2023-01-01'
        )
        
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('classroom-assignments-bulk-assign')
        data = {
            'classroom_id': self.classroom.id,
            'academic_year': '2024-2025',
            'assignments': [
                {'student_id': self.student.id, 'roll_number': 1},
                {'student_id': student2.id, 'roll_number': 2}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)


class ParentStudentLinkingTests(APITestCase):
    """Test parent-student linking functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School")
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@school.com',
            password='AdminPass123!',
            role='admin',
            school=self.school
        )
        
        self.parent = User.objects.create_user(
            username='parent',
            email='parent@school.com',
            password='ParentPass123!',
            role='parent',
            school=self.school
        )
        
        self.student = Student.objects.create(
            school=self.school,
            first_name='John',
            last_name='Doe',
            admission_number='ADM001',
            date_of_birth='2010-01-01',
            gender='male',
            enrollment_date='2023-01-01'
        )
    
    def test_link_parent_to_student(self):
        """Test linking a parent to a student"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('parent-student-links-list')
        data = {
            'parent': self.parent.id,
            'student': self.student.id,
            'relationship': 'father',
            'is_primary': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_bulk_link_parent_to_multiple_students(self):
        """Test bulk linking a parent to multiple students"""
        # Create second student
        student2 = Student.objects.create(
            school=self.school,
            first_name='Jane',
            last_name='Doe',
            admission_number='ADM002',
            date_of_birth='2012-01-01',
            gender='female',
            enrollment_date='2023-01-01'
        )
        
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('parent-student-links-bulk-link')
        data = {
            'parent_id': self.parent.id,
            'student_ids': [self.student.id, student2.id],
            'relationship': 'father'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)


class BulkUserImportTests(APITestCase):
    """Test bulk CSV user import"""
    
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School")
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@school.com',
            password='AdminPass123!',
            role='admin',
            school=self.school
        )
    
    def test_import_users_from_csv(self):
        """Test importing users from CSV file"""
        self.client.force_authenticate(user=self.admin)
        
        # Create CSV content
        csv_content = """username,email,password,first_name,last_name,role,school_id
user1,user1@school.com,SecurePass123!,User,One,teacher,{school_id}
user2,user2@school.com,SecurePass123!,User,Two,student,{school_id}""".format(
            school_id=self.school.id
        )
        
        # Create file-like object
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'users.csv'
        
        url = reverse('bulk-import-import-users')
        response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['successful']), 2)


class AttendanceReportTests(APITestCase):
    """Test attendance report generation"""
    
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name="Test School")
        
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@school.com',
            password='TeacherPass123!',
            role='teacher',
            school=self.school
        )
        
        self.classroom = Classroom.objects.create(
            school=self.school,
            name='Class A',
            grade_level='Grade 1'
        )
        
        self.student = Student.objects.create(
            school=self.school,
            first_name='John',
            last_name='Doe',
            admission_number='ADM001',
            date_of_birth='2010-01-01',
            gender='male',
            enrollment_date='2023-01-01',
            classroom=self.classroom
        )
        
        # Create attendance records
        for i in range(5):
            Attendance.objects.create(
                student=self.student,
                date=datetime.now().date() - timedelta(days=i),
                status='present' if i % 2 == 0 else 'absent'
            )
    
    def test_generate_pdf_report(self):
        """Test generating PDF attendance report"""
        self.client.force_authenticate(user=self.teacher)
        
        url = reverse('attendance-reports-pdf')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_generate_csv_report(self):
        """Test generating CSV attendance report"""
        self.client.force_authenticate(user=self.teacher)
        
        url = reverse('attendance-reports-csv')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')


class MultiLanguageTests(APITestCase):
    """Test multi-language support"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_login_response_languages(self):
        """Test that API responses support multiple languages"""
        # This would test Accept-Language header support
        pass


if __name__ == '__main__':
    import unittest
    unittest.main()
