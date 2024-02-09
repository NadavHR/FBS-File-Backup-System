import json
import os
import shutil
import unittest

from constants import Constants
from ProjectManager import ProjectManager
from ProjectClass import Project
from Commit import Commit


class TestProjectCreation(unittest.TestCase):
    def test_bad_project(self):
        self.assertEqual(
            ProjectManager.update_project_permissions("test_user", Project("bad_user", "i shouldn't exist"),
                                                      True), ProjectManager.E_PROJECT_DOESNT_EXIST)

    def test_bad_user(self):
        self.assertEqual(
            ProjectManager.update_project_permissions("bad_user", Project("test_user", "test_project"), False),
            ProjectManager.E_USER_DOESNT_EXIST)

    def test_sharing_limit(self):
        share_project = Project("test_user_full", "test_project_0")
        for i in range(ProjectManager.PROJECT_SHARING_LIMIT):
            project = Project(f"test_user_{i}", "test_project")
            try:
                os.makedirs(project.to_path())
            except:
                pass
            ProjectManager.update_project_permissions(f"test_user_{i}", share_project, False)
        self.assertEqual(ProjectManager.update_project_permissions("test_user", share_project, False),
                         ProjectManager.E_PROJECT_SHARE_LIMIT_REACHED)

    def test_successful_share(self):
        project = Project("test_user", "test_project")
        self.assertEqual(ProjectManager.update_project_permissions("test_user_full", project, False),
                         ProjectManager.S_ACCESS_GRANTED)

    def test_read_only(self):
        project = Project("test_user", "test_project")
        ProjectManager.update_project_permissions("test_user_full", project, False)
        self.assertEqual(ProjectManager.commit_to(project, Commit.new_commit(user="test_user_full",
                                                                             commit_message="hello",
                                                                             commit_name="test",
                                                                             data=b"Hello, World!",
                                                                             project=project)),
                         ProjectManager.E_BAD_PERMISSIONS)

    def test_write(self):
        project = Project("test_user", "test_project")
        ProjectManager.update_project_permissions("test_user_full", project, True)
        self.assertEqual(ProjectManager.commit_to(project, Commit.new_commit(user="test_user_full",
                                                                             commit_message="hello",
                                                                             commit_name="test",
                                                                             data=b"Hello, World!",
                                                                             project=project)),
                         ProjectManager.S_COMMIT_SUCCESSFUL)

    def test_listing(self):
        shutil.rmtree(f"{Constants.USERS_DIR}\\listing_check")
        shutil.rmtree(f"{Constants.USERS_DIR}\\test_user")
        os.makedirs(f"{Constants.USERS_DIR}\\listing_check\\{Constants.USER_PROJECTS_DIR}")
        os.makedirs(f"{Constants.USERS_DIR}\\test_user\\{Constants.USER_PROJECTS_DIR}")
        project = Project("test_user", "test_project")
        project2 = Project("test_user", "test_project_2")
        ProjectManager.add_project(project)
        ProjectManager.add_project(project2)
        ProjectManager.update_project_permissions("listing_check", project, True)
        f = open(f"{Constants.USERS_DIR}\\listing_check\\{Constants.USER_SHARED_DIR}\\test_user\\test_project", "wb+")
        f.write(b"\000")
        f.close()
        r = json.loads(ProjectManager.get_user_projects("listing_check").response_message)
        self.assertTrue(r[Constants.RESP_SHARED_PROJECTS_FIELD]["test_user"]["test_project"])

        ProjectManager.update_project_permissions("listing_check", project, False)
        f = open(f"{Constants.USERS_DIR}\\listing_check\\{Constants.USER_SHARED_DIR}\\test_user\\test_project", "wb+")
        f.write(b"\001")
        f.close()
        r = json.loads(ProjectManager.get_user_projects("listing_check").response_message)
        self.assertFalse(r[Constants.RESP_SHARED_PROJECTS_FIELD]["test_user"]["test_project"])

        ProjectManager.update_project_permissions("listing_check", project, None)
        f = open(f"{Constants.USERS_DIR}\\listing_check\\{Constants.USER_SHARED_DIR}\\test_user\\test_project", "wb+")
        f.write(b"\001")
        f.close()
        r = json.loads(ProjectManager.get_user_projects("listing_check").response_message)
        self.assertFalse("test_user" in (r[Constants.RESP_SHARED_PROJECTS_FIELD]).keys())

        ProjectManager.update_project_permissions("listing_check", project, False)
        ProjectManager.update_project_permissions("listing_check", project2, False)
        ProjectManager.update_project_permissions("listing_check", project, None)
        r = json.loads(ProjectManager.get_user_projects("listing_check").response_message)
        self.assertFalse(r[Constants.RESP_SHARED_PROJECTS_FIELD]["test_user"]["test_project_2"])
        self.assertFalse("test_project" in r[Constants.RESP_SHARED_PROJECTS_FIELD]["test_user"].keys())




def main():
    unittest.main()


if __name__ == '__main__':
    main()
