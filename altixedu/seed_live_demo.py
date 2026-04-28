from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.academics.models import AcademicYear, Classroom, Exam, ExamResult, Subject, TeacherSubject
from apps.attendance.models import Attendance
from apps.billing.models import BillingAlert, Invoice, PaymentTransaction, Subscription, SubscriptionTier
from apps.finance.models import Fee, StudentFee
from apps.government.models import AuditLog, MinistryDashboardAggregation, MinistryDashboardAlert, RolePermissionGroup
from apps.notifications.models import Message, RoleSetting, SchoolSetting, StudentAIInsights
from apps.schools.models import Ministry, School
from apps.students.models import Parent, Student, StudentParent
from apps.teachers.models import Teacher


PASSWORD = "Password123!"


def create_user(User, *, username, email, role, school=None, ministry=None, first_name="", last_name="", is_staff=False, is_superuser=False):
    user, _created = User.objects.update_or_create(
        username=username,
        defaults={
            "email": email,
            "role": role,
            "school": school,
            "ministry": ministry,
            "first_name": first_name,
            "last_name": last_name,
            "is_staff": is_staff,
            "is_superuser": is_superuser,
        },
    )
    user.set_password(PASSWORD)
    user.save()
    return user


def run():
    User = get_user_model()

    User.objects.filter(username__in=["superadmin", "admin", "bursar", "teacher", "parent", "student", "ministry"]).delete()
    School.objects.filter(subdomain__in=["atlas", "cedar"]).delete()
    Ministry.objects.filter(name="Oyo State Ministry of Education", state_or_province="Oyo").delete()

    ministry = Ministry.objects.create(
        name="Oyo State Ministry of Education",
        country="Nigeria",
        state_or_province="Oyo",
        state="Oyo",
        contact_email="contact@oyo-edu.gov.ng",
        contact_phone="+2348000000001",
        address="Secretariat, Ibadan",
        currency_code="NGN",
        currency_symbol="NGN",
    )

    school = School.objects.create(
        name="Atlas College",
        subdomain="atlas",
        email="hello@atlascollege.edu",
        phone="+2348000000002",
        address="1 Atlas Way, Ibadan",
        city="Ibadan",
        state="Oyo",
        country="Nigeria",
        website="https://atlascollege.edu",
        timezone="Africa/Lagos",
        language="en",
        school_type="private",
        region="South West",
        ministry=ministry,
        primary_color="#0f172a",
        secondary_color="#1d4ed8",
        is_active=True,
    )

    school_two = School.objects.create(
        name="Cedar Heights College",
        subdomain="cedar",
        email="hello@cedarheights.edu",
        phone="+2348000000003",
        address="4 Heights Avenue, Ibadan",
        city="Ibadan",
        state="Oyo",
        country="Nigeria",
        website="https://cedarheights.edu",
        timezone="Africa/Lagos",
        language="en",
        school_type="public",
        region="South West",
        ministry=ministry,
        primary_color="#111827",
        secondary_color="#059669",
        is_active=True,
    )

    superadmin = create_user(
        User,
        username="superadmin",
        email="superadmin@altixedu.test",
        role="superadmin",
        first_name="Zainab",
        last_name="Cole",
        is_staff=True,
        is_superuser=True,
    )
    admin = create_user(
        User,
        username="admin",
        email="admin@atlascollege.test",
        role="admin",
        school=school,
        first_name="Tunde",
        last_name="Adebayo",
        is_staff=True,
    )
    bursar_user = create_user(
        User,
        username="bursar",
        email="bursar@atlascollege.test",
        role="bursar",
        school=school,
        first_name="Kunle",
        last_name="Ariyo",
    )
    teacher_user = create_user(
        User,
        username="teacher",
        email="teacher@atlascollege.test",
        role="teacher",
        school=school,
        first_name="Mary",
        last_name="Ojo",
    )
    parent_user = create_user(
        User,
        username="parent",
        email="parent@atlascollege.test",
        role="parent",
        school=school,
        first_name="Amina",
        last_name="Yusuf",
    )
    student_user = create_user(
        User,
        username="student",
        email="student@atlascollege.test",
        role="student",
        school=school,
        first_name="Ada",
        last_name="Okafor",
    )
    ministry_admin = create_user(
        User,
        username="ministry",
        email="ministry@oyo-edu.test",
        role="ministry_admin",
        ministry=ministry,
        first_name="Bisi",
        last_name="Adeyemi",
        is_staff=True,
    )

    SchoolSetting.objects.update_or_create(
        school=school,
        defaults={
            "logo_url": "",
            "primary_color": "#0f172a",
            "secondary_color": "#1d4ed8",
            "school_year": "2025-2026",
            "attendance_threshold": 75,
            "performance_threshold": 70.0,
            "enable_parent_portal": True,
            "enable_student_portal": True,
            "enable_teacher_portal": True,
            "notification_email": "ops@atlascollege.edu",
            "enable_email_alerts": True,
            "enable_sms_alerts": False,
            "default_fee_structure": [{"name": "Tuition", "amount": 150000}],
        },
    )

    for role, key, value in [
        ("admin", "dashboard_layout", {"mode": "executive"}),
        ("teacher", "marking_preferences", {"enter_grades": True}),
        ("parent", "communication", {"digest": True}),
        ("student", "study_mode", {"ai_recommendations": True}),
    ]:
        RoleSetting.objects.update_or_create(role=role, school=school, key=key, defaults={"value": value})

    academic_year = AcademicYear.objects.create(
        school=school,
        year="2025/2026",
        start_date=date(2025, 9, 1),
        end_date=date(2026, 7, 31),
        is_active=True,
    )
    classroom = Classroom.objects.create(
        school=school,
        academic_year=academic_year,
        name="SS 2 Gold",
        grade_level="SS2",
    )

    teacher = Teacher.objects.create(
        school=school,
        user=teacher_user,
        employment_date=date(2023, 9, 1),
        status="active",
    )
    classroom.class_teacher = teacher
    classroom.save(update_fields=["class_teacher"])

    Parent.objects.create(school=school, user=parent_user, phone="+2348000000004", address="Atlas Estate")

    subjects = [
        Subject.objects.create(school=school, name="Mathematics", code="ATLAS-MTH"),
        Subject.objects.create(school=school, name="English Language", code="ATLAS-ENG"),
        Subject.objects.create(school=school, name="Physics", code="ATLAS-PHY"),
    ]
    for subject in subjects:
        TeacherSubject.objects.create(school=school, teacher=teacher, subject=subject, classroom=classroom)

    student = Student.objects.create(
        school=school,
        user=student_user,
        first_name="Ada",
        last_name="Okafor",
        admission_number="ATLAS-2026-001",
        date_of_birth=date(2011, 4, 10),
        gender="female",
        enrollment_date=date(2025, 9, 5),
        status="active",
        classroom=classroom,
    )
    StudentParent.objects.create(student=student, parent=parent_user, relationship="Mother")

    exam = Exam.objects.create(
        school=school,
        name="Midterm Assessment",
        start_date=date.today() - timedelta(days=10),
        end_date=date.today() - timedelta(days=8),
    )
    ExamResult.objects.create(exam=exam, student=student, subject=subjects[0], score=86, created_by=teacher_user)
    ExamResult.objects.create(exam=exam, student=student, subject=subjects[1], score=74, created_by=teacher_user)
    ExamResult.objects.create(exam=exam, student=student, subject=subjects[2], score=68, created_by=teacher_user)

    for days_ago, status in [(1, "present"), (2, "present"), (3, "present"), (4, "absent"), (5, "present"), (6, "late")]:
        Attendance.objects.create(
            student=student,
            school=school,
            date=date.today() - timedelta(days=days_ago),
            status=status,
            recorded_by=teacher_user,
        )

    insight = StudentAIInsights.objects.create(
        student=student,
        school=school,
        attendance_risk=0.18,
        performance_risk=0.42,
        overall_risk=0.32,
        low_attendance=False,
        low_performance=True,
        flagged_subjects=["Physics"],
        attendance_percentage=91.0,
        average_grade=76.0,
        days_absent=1,
    )
    insight.save()

    tuition_fee = Fee.objects.create(school=school, name="Tuition", amount=150000)
    StudentFee.objects.create(
        student=student,
        fee=tuition_fee,
        amount_paid=100000,
        due_date=date.today() + timedelta(days=14),
        paid=False,
        recorded_by=bursar_user,
        history=[{"amount_added": 100000, "by": bursar_user.username, "date": str(timezone.now())}],
    )

    Message.objects.create(sender=teacher_user, receiver=parent_user, content="Please review Ada's Physics revision plan.", school=school, student=student)
    Message.objects.create(sender=parent_user, receiver=teacher_user, content="Thank you. We will support at home.", school=school, student=student)
    Message.objects.create(sender=admin, receiver=teacher_user, content="Submit weekly classroom summary.", school=school)

    tiers = {
        "growth": SubscriptionTier.objects.create(
            name="growth",
            display_name="Growth Plan",
            monthly_price=Decimal("250000.00"),
            annual_price=Decimal("2700000.00"),
            max_students=1000,
            max_teachers=80,
            max_classrooms=40,
            features=["attendance", "messaging", "billing", "analytics"],
            support_level="phone",
            trial_days=30,
        ),
        "govt": SubscriptionTier.objects.create(
            name="govt",
            display_name="Government Plan",
            monthly_price=Decimal("500000.00"),
            annual_price=Decimal("5400000.00"),
            max_students=999999,
            max_teachers=99999,
            max_classrooms=99999,
            features=["attendance", "messaging", "billing", "analytics", "government_reporting"],
            support_level="vip",
            trial_days=30,
        ),
    }

    sub_one = Subscription.objects.create(
        school=school,
        tier=tiers["growth"],
        monthly_price=Decimal("250000.00"),
        annual_price=Decimal("2700000.00"),
        payment_frequency="monthly",
        status="active",
        trial_started_at=timezone.now() - timedelta(days=40),
        trial_ends_at=timezone.now() - timedelta(days=10),
        is_trial_converted=True,
        renewal_date=timezone.now() + timedelta(days=12),
        discount_percentage=0,
    )
    sub_two = Subscription.objects.create(
        school=school_two,
        tier=tiers["govt"],
        monthly_price=Decimal("500000.00"),
        annual_price=Decimal("5400000.00"),
        payment_frequency="annual",
        status="past_due",
        trial_started_at=timezone.now() - timedelta(days=60),
        trial_ends_at=timezone.now() - timedelta(days=30),
        is_trial_converted=True,
        renewal_date=timezone.now() + timedelta(days=3),
        discount_percentage=15,
    )

    tx1 = PaymentTransaction.objects.create(
        subscription=sub_one,
        amount=Decimal("250000.00"),
        currency="NGN",
        payment_method="manual",
        status="completed",
        transaction_id="txn-atlas-001",
        completed_at=timezone.now() - timedelta(days=2),
    )
    PaymentTransaction.objects.create(
        subscription=sub_two,
        amount=Decimal("500000.00"),
        currency="NGN",
        payment_method="manual",
        status="failed",
        transaction_id="txn-cedar-001",
    )

    Invoice.objects.create(
        subscription=sub_one,
        transaction=tx1,
        invoice_number="INV-ATLAS-001",
        amount=Decimal("250000.00"),
        due_at=timezone.now() + timedelta(days=12),
        paid_at=timezone.now() - timedelta(days=2),
        status="paid",
    )
    Invoice.objects.create(
        subscription=sub_two,
        invoice_number="INV-CEDAR-001",
        amount=Decimal("500000.00"),
        due_at=timezone.now() - timedelta(days=5),
        status="overdue",
    )

    BillingAlert.objects.create(
        subscription=sub_two,
        alert_type="payment_failed",
        message="Cedar Heights is past due and needs billing follow-up.",
        is_resolved=False,
    )

    aggregation = MinistryDashboardAggregation.objects.create(
        state="Oyo",
        ministry=ministry,
        total_schools=2,
        schools_live=2,
        schools_pending=0,
        avg_deployment_days=5,
        total_students=420,
        total_fees_collected=Decimal("18200000.00"),
        total_fees_outstanding=Decimal("2300000.00"),
        collection_rate_percentage=88.8,
        avg_fee_per_student=Decimal("43333.00"),
        total_teachers=41,
        teachers_active_system=37,
        teachers_last_7_days=35,
        avg_teacher_weekly_hours=18.5,
        total_admin_hours_saved_weekly=52.0,
        avg_attendance_rate=89.4,
        schools_below_attendance_threshold=0,
        overall_pass_rate=76.2,
        students_at_risk_count=13,
    )
    MinistryDashboardAlert.objects.create(
        dashboard=aggregation,
        level="warning",
        title="Payment risk in one school",
        description="One provisioned school is near renewal with an unresolved billing issue.",
        school=school_two,
        metric_type="collection",
        metric_value=71.0,
        threshold=80.0,
        action_url="/dashboard",
    )

    RolePermissionGroup.objects.create(
        school=school,
        role="school_admin",
        can_access_dashboard=True,
        can_view_students=True,
        can_edit_students=True,
        can_view_grades=True,
        can_edit_grades=True,
        can_view_attendance=True,
        can_edit_attendance=True,
        can_view_finances=True,
        can_edit_finances=True,
        can_approve_payments=True,
        can_view_audit_logs=True,
        can_export_reports=True,
        can_manage_users=True,
        can_view_school_profile=True,
        can_edit_school_profile=True,
        can_edit_school_settings=True,
        can_manage_teachers=True,
        can_manage_bursars=True,
        can_manage_staff=True,
        can_manage_classrooms=True,
        can_assign_teachers_to_class=True,
        can_assign_students_to_class=True,
        can_link_parent_student=True,
        can_manage_parent_records=True,
        can_see_all_students=True,
        can_see_all_teachers=True,
    )

    AuditLog.objects.create(
        user=admin,
        user_email=admin.email,
        user_role=admin.role,
        user_school=school,
        action_type="school_settings_update",
        action_description="Updated branding and notification settings.",
        content_type="SchoolSetting",
        object_id=school.id,
        object_name=school.name,
        before_value={"primary_color": "#0066CC"},
        after_value={"primary_color": "#0f172a"},
        changed_fields=["primary_color", "secondary_color"],
    )

    print("Live demo data seeded.")
    print("Credentials:")
    for username, role in [
        ("superadmin", "superadmin"),
        ("ministry", "ministry_admin"),
        ("admin", "admin"),
        ("teacher", "teacher"),
        ("student", "student"),
        ("parent", "parent"),
        ("bursar", "bursar"),
    ]:
        print(f" - {username} ({role}) / {PASSWORD}")
