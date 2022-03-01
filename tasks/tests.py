from datetime import datetime
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase


from .models import Task, TaskHistory, EmailPreferences
from .views import GenericTaskView
from .tasks import check_email_preferences


class TestSetupManager(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )


class AuthenticationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )

    def test_unauthenticated_user(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/tasks/")

    def test_authenticated_user(self):
        request = self.factory.get("/tasks")
        request.user = self.user
        response = GenericTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class GenericViewsTests(TestSetupManager):
    def test_priority_cascading(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        self.client.post(
            "/create-task/",
            {
                "title": "Test task four",
                "description": "test",
                "priority": 1,
                "status": "PENDING",
                "completed": False,
            },
        )
        self.client.post(
            "/create-task/",
            {
                "title": "Test task three",
                "description": "test",
                "priority": 1,
                "status": "PENDING",
                "completed": False,
            },
        )
        self.client.post(
            "/create-task/",
            {
                "title": "Test task two",
                "description": "test",
                "priority": 1,
                "status": "PENDING",
                "completed": False,
            },
        )
        self.client.post(
            "/create-task/",
            {
                "title": "Test task one",
                "description": "test",
                "priority": 1,
                "status": "PENDING",
                "completed": False,
            },
        )

        self.assertEqual(Task.objects.get(priority=4).title, "TEST TASK FOUR")

        self.client.post(
            f"/update-task/4/",
            {
                "title": "TEST TASK ONE",
                "description": "test",
                "priority": 3,
                "status": "PENDING",
                "completed": False,
            },
        )

        self.assertEqual(Task.objects.get(priority=2).title, "TEST TASK TWO")
        self.assertEqual(Task.objects.get(priority=3).title, "TEST TASK ONE")
        self.assertEqual(Task.objects.get(priority=4).title, "TEST TASK THREE")
        self.assertEqual(Task.objects.get(priority=5).title, "TEST TASK FOUR")


class EmailPreferencesTests(TestSetupManager):
    def test_update_email_pref_valid_hour(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        self.client.post(
            f"/update-email-pref/{self.user.id}",
            {"selected_email_hour": "10"},
        )
        self.assertEqual(
            EmailPreferences.objects.get(user=self.user).selected_email_hour,
            10,
        )

    def test_update_email_pref_invalid_hour(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        self.client.post(
            f"/update-email-pref/{self.user.id}",
            {"selected_email_hour": "-12"},
        )
        self.assertEqual(
            EmailPreferences.objects.filter(user=self.user).first().selected_email_hour,
            0,
        )


class ApiViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User.objects.create_user(
            username="bruce_wayne", email="bruce@wayne.org", password="i_am_batman"
        )
        User.objects.create_user(
            username="test_user", email="test@user.org", password="i_am_batman"
        )

    def test_tasks_api(self):
        self.client.login(username="bruce_wayne", password="i_am_batman")
        self.client.post(
            "/create-task/",
            {
                "title": "Test task one",
                "description": "test",
                "priority": 1,
                "status": "PENDING",
                "completed": False,
            },
        )
        response = self.client.get("/api/task/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'[{"id":1,"title":"TEST TASK ONE","description":"test","completed":false,"status":"PENDING","user":{"first_name":"","last_name":"","username":"bruce_wayne"}}]',
        )

        self.client.logout()

        self.client.login(username="test_user", password="i_am_batman")
        self.client.post(
            "/create-task/",
            {
                "title": "Test user task two",
                "description": "test user task",
                "priority": 1,
                "status": "IN_PROGRESS",
                "completed": False,
            },
        )
        response = self.client.get("/api/task/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            b'[{"id":2,"title":"TEST USER TASK TWO","description":"test user task","completed":false,"status":"IN_PROGRESS","user":{"first_name":"","last_name":"","username":"test_user"}}]',
        )

    def test_task_history_api(self):
        new_task = Task.objects.create(
            title="test task one",
            description="test task",
            priority=1,
            user=User.objects.get(username="bruce_wayne"),
        )

        new_task.status = "IN_PROGRESS"
        new_task.save()
        new_task.status = "COMPLETED"
        new_task.save()
        self.assertEqual(TaskHistory.objects.filter(task=new_task.id).count(), 2)


class SendEmailTests(TestSetupManager):
    def test_check_email_pref(self):
        check_email_preferences()
        current_day = datetime.now().day
        self.assertEqual(
            EmailPreferences.objects.get(user=self.user).previous_report_day,
            current_day,
        )
