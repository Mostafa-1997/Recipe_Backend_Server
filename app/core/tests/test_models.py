from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):

        email = 'test@example.com'
        username = 'testuser'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):

        test_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'test2@example.com'],
            ['TEST3@EXAMPLE.com', 'test3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            ['teSt5@exaMple.COM', 'test5@example.com'],
        ]

        for index, (email, expected) in enumerate(test_emails):
            user = get_user_model().objects.create_user(email,f'testuser{index}','test123')
            self.assertEqual(user.email, expected)
            self.assertEqual(user.username, f'testuser{index}')

    def test_new_user_without_email_raises_error(self):

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testuser', 'test123')

    def test_new_user_without_username_raises_error(self):

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('TesT@example.com', '', 'test123')

    def test_create_superuser(self):

        user = get_user_model().objects.create_superuser(
            'admin@example.com',
            'admin',
            'admin123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)