import shutil
import unittest
from ProjectManager import ProjectManager
from Commit import Commit
from ProjectClass import Project


# TODO: finish writing this test
class TestCommits(unittest.TestCase):
    def test_bad_user(self):
        pass

    def test_double_commits(self):
        project = Project("test_user", "test_project")
        ProjectManager.add_project(project)
        commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                   commit_message="hi")
        first = (ProjectManager.commit_to(project=project, commit=commit)).success
        second = (ProjectManager.commit_to(project=project, commit=commit)).success

        self.assertTrue((first or second) and not (first and second) and first)  # only true if first=True second=False

    def test_deletion_middle(self):
        project = Project("test_user", "test_project")
        ProjectManager.delete_project(project)
        ProjectManager.add_project(project)
        for i in range(5):
            commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                       commit_message="hi")
            commit.commit()
        n = project.count_commits()
        c = Commit.from_commit_number(project=project, commit_number=1)
        s = c.delete()
        self.assertTrue(s and (n == project.count_commits() + 1))

    def test_deletion_start(self):
        project = Project("test_user", "test_project")
        ProjectManager.delete_project(project)
        ProjectManager.add_project(project)
        for i in range(3):
            commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                       commit_message="hi")
            commit.commit()
        n = project.count_commits()
        c = Commit.from_commit_number(project=project, commit_number=0)
        s = c.delete()
        self.assertTrue(s and (n == project.count_commits() + 1))

    def test_deletion_end(self):
        project = Project("test_user", "test_project")
        ProjectManager.delete_project(project)
        ProjectManager.add_project(project)
        for i in range(3):
            commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                       commit_message="hi")
            commit.commit()
        n = project.count_commits()
        c = Commit.from_commit_number(project=project, commit_number=2)
        s = c.delete()
        self.assertTrue(s and (n == project.count_commits() + 1))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
