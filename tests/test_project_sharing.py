import os
import shutil
import unittest
from ProjectManager import ProjectManager
from ProjectClass import Project
from Commit import Commit

class TestProjectCreation(unittest.TestCase):
    def test_bad_project(self):
        self.assertEqual(ProjectManager.update_project_permissions("test_user", Project("bad_user", "i shouldn't exist"),
                                                                   True), ProjectManager.E_PROJECT_DOESNT_EXIST)

    def test_bad_user(self):
        self.assertEqual(ProjectManager.update_project_permissions("bad_user", Project("test_user", "test_project"), False),
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


def main():
    unittest.main()


if __name__ == '__main__':
    main()
