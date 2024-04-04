import json
import os
import shutil
import unittest
from user_manager import UserManager
from user import User
from session import Session
from project_class import Project
from commit import Commit


class TestUserManager(unittest.TestCase):
    def test_sign_up(self):
        shutil.rmtree("users")
        os.mkdir("users")
        r = UserManager.create_user("new user", b"password123")
        self.assertTrue(r.success)
        r = UserManager.create_user("new user", b"password123")
        self.assertEqual(r, UserManager.E_USER_ALREADY_EXISTS)

    def test_login(self):
        user = User("new user", b"password123")
        user.create()
        user.end_session()
        r = UserManager.login("new user", b"password123")
        self.assertTrue(r.success)
        r = UserManager.login("new user", b"password123")
        self.assertEqual(r, UserManager.E_USER_ALREADY_HAS_VALID_SESSION)
        user = User("new user", b"password123")
        user.end_session()
        r = UserManager.login("new user", b"bad password")
        self.assertEqual(r, UserManager.E_BAD_LOGIN_CREDENTIALS)
        r = UserManager.login("new user", b"password123")
        self.assertTrue(r.success)

    def test_logout(self):
        user = User("user", b"password123")
        user.delete()
        user.create()
        session_id = user.session.id
        r = UserManager.logout(session_id)
        self.assertEqual(r, UserManager.S_LOGGED_OUT)
        r = UserManager.logout(session_id)
        self.assertEqual(r, UserManager.E_BAD_SESSION)

    def test_delete_user(self):
        user = User("my user", b"password123")
        user.delete()
        user.create()
        session_id = user.session.id
        r = UserManager.delete_user(session_id)
        self.assertEqual(r, UserManager.S_USER_DELETED)
        r = UserManager.delete_user(session_id)
        self.assertEqual(r, UserManager.E_BAD_SESSION)

    def test_session_expiration(self):
        user = User("exp user", b"password123")
        user.create()
        user.end_session()
        r = UserManager.login("exp user", password_hash=b"password123")
        session_id = int(r.response_message)
        Session.from_session_id(session_id).start_time = 0
        r = UserManager.logout(session_id)
        self.assertEqual(r, UserManager.E_BAD_SESSION)

    def test_project_creation(self):
        user = User("pro user", b"password123")
        user.delete()
        user.create()
        session_id = user.session.id
        r = UserManager.add_project(session_id, "new project", "description")
        self.assertEqual(r, UserManager.S_PROJECT_CREATED)
        user.session.start_time = 0
        r = UserManager.add_project(session_id, "project2", "description")
        self.assertEqual(r, UserManager.E_BAD_SESSION)

    def test_commit(self):
        user = User("com user", b"password123")
        user.delete()
        user.create()
        session_id = user.session.id
        UserManager.add_project(session_id, "new project", "description")
        project = Project(user_name=user.user_name, project_name="new project")
        r = UserManager.commit(session_id, Commit.new_commit(user.user_name, "new commit", "hi", b"Hello", project))
        self.assertEqual(r, UserManager.S_COMMIT_SUCCESSFUL)
        user.session.expire()
        r = UserManager.commit(session_id, Commit.new_commit(user.user_name, "new commit", "hi", b"Hello", project))
        self.assertEqual(r, UserManager.E_BAD_SESSION)

    def test_delete_commit(self):
        user = User("del com user",  b"password123")
        user.delete()
        user.create()
        session_id = user.session.id
        UserManager.add_project(session_id, "new project", "description")
        project = Project(user_name=user.user_name, project_name="new project")
        commit = Commit.new_commit(user.user_name, "new commit", "hi", b"Hello", project)
        r = UserManager.commit(session_id, commit)
        r = UserManager.delete_commit(session_id, commit.project.project_name, commit.commit_number)
        self.assertEqual(r, UserManager.S_COMMIT_DELETED)

    def test_delete_project(self):
        user = User("del pro user", b"password123")
        user.delete()
        user.create()
        session_id = user.session.id
        UserManager.add_project(session_id, "new project", "description")
        r = UserManager.delete_project(session_id, "new project")
        self.assertEqual(r, UserManager.S_PROJECT_DELETED)

    def test_permission(self):
        user = User("per user", b"password123")
        user.delete()
        user.create()
        user2 = User("test user", b"password123")
        user2.create()
        session_id = user.session.id
        UserManager.add_project(session_id, "new project", "description")
        r = UserManager.update_project_permissions(session_id, "new project", user2.user_name, True)
        self.assertEqual(r, UserManager.S_ACCESS_GRANTED)

    def test_project_info(self):
        user = User("test_user", b"password123")
        user.delete()
        user.create()
        session_id = user.session.id

        UserManager.delete_project(session_id, "test_project")
        UserManager.add_project(session_id, "test_project", "hi")
        r = UserManager.get_project_info(session_id, "test_project", "test_user")
        self.assertEqual(json.loads(r.response_message)[Project.PROJECT_DESCRIPTION_FIELD], "hi")



if __name__ == '__main__':
    unittest.main()