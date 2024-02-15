import os
import shutil
import unittest

import constants
from project_manager import ProjectManager
from project_class import Project


class TestProjectCreation(unittest.TestCase):
    def test_bad_user(self):
        self.assertEqual(ProjectManager.add_project(Project("bad_user", "i shouldn't exist")),
                         ProjectManager.E_USER_DOESNT_EXIST)

    def test_project_exists(self):
        ProjectManager.add_project(Project("test_user", "test_project"))
        self.assertEqual(ProjectManager.add_project(Project("test_user", "test_project")),
                         ProjectManager.E_PROJECT_ALREADY_EXISTS)

    def test_project_limit(self):
        for i in range(constants.Constants.USER_PROJECT_LIMIT):
            ProjectManager.add_project(Project("test_user_full", f"test_project_{i}"))
        self.assertEqual(ProjectManager.add_project(Project("test_user_full", "this is a test")),
                         ProjectManager.E_PROJECT_LIMIT_REACHED)

    def test_successful_creation(self):
        project = Project("test_user", "test_project_2")
        try:
            shutil.rmtree(project.to_path())
        except:
            pass
        self.assertEqual(ProjectManager.add_project(project),
                         ProjectManager.S_PROJECT_CREATED)

    def test_project_deletion(self):
        project = Project("test_user", "test_project_2")
        ProjectManager.add_project(project)
        self.assertEqual(ProjectManager.delete_project(project),
                         ProjectManager.S_PROJECT_DELETED)

    def test_project_listing(self):
        try:
            os.makedirs("users\\listing_check\\projects")
        except:
            pass
        for i in range(3):
            project = Project(user_name="listing_check", project_name=f"project_{i}")
            ProjectManager.add_project(project)
        r = ProjectManager.get_user_projects("listing_check")
        self.assertTrue(r._success)
        for i in range(3):
            self.assertTrue(f"project_{i}" in r._response_message)

    def test_project_listing_bad_user(self):
        self.assertEqual(ProjectManager.get_user_projects("bad user"), ProjectManager.E_USER_DOESNT_EXIST)


def main():
    try:
        os.makedirs("users\\test_user\\projects")
    except:
        pass
    try:
        os.makedirs("users\\test_user_full\\projects")
    except:
        pass
    unittest.main()


if __name__ == '__main__':
    main()
