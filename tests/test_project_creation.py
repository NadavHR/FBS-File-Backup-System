import shutil
import unittest
from ProjectManager import ProjectManager
from ProjectClass import Project


class TestProjectCreation(unittest.TestCase):
    def test_bad_user(self):
        self.assertEqual(ProjectManager.add_project(Project("bad_user", "i shouldn't exist")),
                         ProjectManager.E_USER_DOESNT_EXIST)

    def test_project_exists(self):
        self.assertEqual(ProjectManager.add_project(Project("test_user", "test_project")),
                         ProjectManager.E_PROJECT_ALREADY_EXISTS)

    def test_project_limit(self):
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



def main():
    unittest.main()


if __name__ == '__main__':
    main()
