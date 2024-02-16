import shutil
import unittest
from project_manager import ProjectManager
from commit import Commit
from project_class import Project


# TODO: finish writing this test
class TestCommits(unittest.TestCase):
    def test_bad_user(self):
        project = Project("test_user", "test_project")
        ProjectManager.add_project(project)
        commit = Commit.new_commit(project=project, user="bad user", data=b"i shouldn't be written",
                                   commit_name="i shouldn't exist", commit_message="")
        n = project.count_commits()
        self.assertEqual(ProjectManager.commit_to(project, commit), ProjectManager.E_USER_DOESNT_EXIST)
        self.assertEqual(n, project.count_commits())

    def test_bad_project(self):
        project = Project("test_user", "bad project")
        ProjectManager.delete_project(project)
        commit = Commit.new_commit(project=project, user="test_user", commit_name="hi",
                                   commit_message="i shouldnt exists", data=b"hi")
        n = project.count_commits()
        self.assertEqual(ProjectManager.commit_to(project, commit), ProjectManager.E_PROJECT_DOESNT_EXIST)
        self.assertEqual(n, project.count_commits())

    # Permissions tested in project sharing tests

    def test_bad_commit_size(self):
        project = Project("test_user", "test_project")
        ProjectManager.add_project(project)
        commit = Commit.new_commit(project=project, user="test_user", data=(b" " * (ProjectManager.COMMIT_SIZE_LIMIT + 1)),
                                   commit_name="i shouldn't exist", commit_message="")
        n = project.count_commits()
        self.assertEqual(ProjectManager.commit_to(project, commit), ProjectManager.E_BAD_COMMIT_SIZE)
        self.assertEqual(n, project.count_commits())

    def test_commit_limit(self):
        project = Project("test_user", "test_project")
        ProjectManager.delete_project(project)
        ProjectManager.add_project(project)
        for i in range(ProjectManager.COMMIT_LIMIT + 1):
            commit = Commit.new_commit(project=project, user="test_user", data=b"", commit_name="hi",
                                       commit_message="hi")
            ProjectManager.commit_to(project, commit)
        n = project.count_commits()
        commit = Commit.new_commit(project=project, user="test_user", data=b"i shouldn't exist",
                                   commit_name="im above the commit limit", commit_message="i")
        self.assertEqual(n, ProjectManager.COMMIT_LIMIT)
        self.assertEqual(ProjectManager.commit_to(project, commit), ProjectManager.E_COMMIT_LIMIT_REACHED)
        self.assertEqual(n, project.count_commits())

    def test_incorrect_project(self):
        project = Project("test_user", "test_project")
        project2 = Project("test_user", "test_project_2")
        ProjectManager.add_project(project)
        ProjectManager.add_project(project2)
        commit = Commit.new_commit(project=project2, user="test_user", commit_name="im in the wrong project",
                                   data=b"i shouldn't be here", commit_message="")
        self.assertEqual(ProjectManager.commit_to(project, commit), ProjectManager.E_UNKNOWN_ERROR)

    def test_double_commits(self):
        project = Project("test_user", "test_project")
        ProjectManager.add_project(project)
        commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                   commit_message="hi")
        r1 = (ProjectManager.commit_to(project=project, commit=commit))
        r2 = (ProjectManager.commit_to(project=project, commit=commit))
        first = r1.success
        second = r2.success
        self.assertEqual(r1, ProjectManager.S_COMMIT_SUCCESSFUL)
        self.assertEqual(r2, ProjectManager.E_UNKNOWN_ERROR)
        self.assertTrue((first or second) and not (first and second) and first)  # only true if first=True second=False

    def test_deletion_middle(self):
        project = Project("test_user", "test_project")
        ProjectManager.delete_project(project)
        ProjectManager.add_project(project)
        for i in range(5):
            commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                       commit_message="hi")
            ProjectManager.commit_to(project, commit)
        n = project.count_commits()
        c = Commit.from_commit_number(project=project, commit_number=1)
        self.assertEqual(ProjectManager.delete_commit(c), ProjectManager.S_COMMIT_DELETED)
        self.assertTrue(n == project.count_commits() + 1)

    def test_deletion_start(self):
        project = Project("test_user", "test_project")
        ProjectManager.delete_project(project)
        ProjectManager.add_project(project)
        for i in range(3):
            commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                       commit_message="hi")
            ProjectManager.commit_to(project, commit)
        n = project.count_commits()
        c = Commit.from_commit_number(project=project, commit_number=1)
        self.assertEqual(ProjectManager.delete_commit(c), ProjectManager.S_COMMIT_DELETED)
        self.assertTrue(n == project.count_commits() + 1)

    def test_deletion_end(self):
        project = Project("test_user", "test_project")
        ProjectManager.delete_project(project)
        ProjectManager.add_project(project)
        for i in range(3):
            commit = Commit.new_commit(project=project, user="test_user", data=b"Hello, World", commit_name="hi",
                                       commit_message="hi")
            ProjectManager.commit_to(project, commit)
        n = project.count_commits()
        c = Commit.from_commit_number(project=project, commit_number=1)
        self.assertEqual(ProjectManager.delete_commit(c), ProjectManager.S_COMMIT_DELETED)
        self.assertTrue(n == project.count_commits() + 1)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
