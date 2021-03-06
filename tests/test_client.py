import re
import unittest
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('陌生人' in response.get_data(as_text=True))

    def test_register_and_login(self):
        # register a new account
        response = self.client.post('/auth/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'catcatcat',
            'password2': 'catcatcat'
        })
        self.assertEqual(response.status_code, 302)

        # login with the new account
        response = self.client.post('/auth/login', data={
            'email': 'john@example.com',
            'password': 'catcatcat'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(', john',
                                  response.get_data(as_text=True)))
        self.assertTrue(
            '你的帐号还未经过系统邮件确认' in response.get_data(
                as_text=True))

        # send a confirmation token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/{}'.format(token),
                                   follow_redirects=True)
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            '您的账户已经被认证' in response.get_data(
                as_text=True))

        # log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('您现在已经退出登录' in response.get_data(
            as_text=True))

    def test_funpic_page(self):
        pass

    def test_updown_page(self):
        pass