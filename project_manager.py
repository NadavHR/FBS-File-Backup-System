import base64
import json
import os
import shutil

import constants
from project_class import Project
from response import Response
from commit import Commit


class ProjectManager(constants.Constants):

    def __init__(self):
        pass

    @staticmethod
    def authenticate_permissions(user: str, target_project: Project, write: bool) -> bool:
        """
        this method checks if a user has permission to perform a certain action (write or read only)
        :param target_project: the target project we want to check permissions to
        :param user: the name of the user who's trying to perform the action
        :param write: True if we ask for an action requiring write permissions, False for readonly
        :return: True if the user has permissions to perform that action, False otherwise
        """
        check = target_project.check_permission(user)
        if check is None:
            return False
        if check:
            return True
        if check == write:
            return True
        return False

    @staticmethod
    def is_user(user_name: str) -> bool:
        """
        checks if a user exists
        :param user_name: the username to check
        :return: true if the user exists, false if not
        """
        return os.path.isdir(Project.USERS_DIR + "\\" + user_name)

    @staticmethod
    def _list_projects(user_name: str) -> list[Project]:
        """
        lists all of the projects a user has, DOES NOT CHECK IF THE USER EXISTS,
         DO NOT USE UNLESS ALREADY MADE SURE USER EXISTS
        :param user_name: the user we want to check
        :return: a list of every project the user has
        """
        projects = []
        dir_path = f"{Project.USERS_DIR}\\{user_name}\\{Project.USER_PROJECTS_DIR}"
        for path in os.listdir(dir_path):
            # check if current path is a file
            if not os.path.isfile(os.path.join(dir_path, path)):
                projects.append(Project(user_name=user_name, project_name=path))
        return projects

    @staticmethod
    def _list_shared_projects(user_name: str) -> dict[str, dict[str, bool]]:
        """
        lists all of the projects shared with a user by other users, DOES NOT CHECK IF THE USER EXISTS,
         DO NOT USE UNLESS ALREADY MADE SURE USER EXISTS
        :param user_name: the user we want o check
        :return: a dict of every user who shares a project containing a dict of all shared projects with the key being
         the project name and the value being True for write access and False for readonly
        """
        shared = {}
        dir_path = f"{Project.USERS_DIR}\\{user_name}\\{Project.USER_SHARED_DIR}"
        if os.path.isdir(dir_path):
            for user in os.listdir(dir_path):  # goes through all users (who ever shared a project with this user)
                path = os.path.join(dir_path, user)
                projects = {}
                if not os.path.isfile(path):
                    for project_name in os.listdir(path):  # goes through all projects shared by this specific user with
                        # this user
                        project_path = os.path.join(path, project_name)
                        if os.path.isfile(project_path):
                            f = open(project_path, "rb+")
                            write = bool.from_bytes(f.read(), "big") and Project.USER_SHARED_PROJECT_WRITE
                            f.close()
                            project = Project(user_name=user, project_name=project_name)
                            if project.exists():  # makes sure the project actually exists
                                real_perms = project.check_permission(user_name)
                                if real_perms is None:  # if the user actually has no permissions
                                    project.delete_permission(user_name)  # makes sure to delete perms from user
                                else:
                                    if real_perms != write:
                                        # makes sure to update the permissions if theres a mismatch
                                        project.give_permissions(user_name, real_perms)
                                    projects[project.project_name] = real_perms
                # if there are no valid projects shared by a user don't add them to the checked list and delete the dir
                if len(projects) != 0:
                    shared[user] = projects
                else:
                    shutil.rmtree(path)
        else:
            os.makedirs(dir_path)
        return shared

    @staticmethod
    def get_user_projects(user_name: str) -> Response:
        """
        lists a users projects including shared projects, REMEMBER TO MAKE SURE THE USER CHECKING IS THE USER BEING CHECKED
        :param user_name: the user we want to check
        :return: a response with all of the projects in the response message
        """
        if not ProjectManager.is_user(user_name):
            return ProjectManager.E_USER_DOESNT_EXIST
        projects = [a.project_name for a in ProjectManager._list_projects(user_name)]
        shared = ProjectManager._list_shared_projects(user_name)
        r = json.dumps({Project.RESP_SELF_PROJECTS_FIELD: projects, Project.RESP_SHARED_PROJECTS_FIELD: shared})
        return Response(success=True, response_message=r)

    @staticmethod
    def _count_projects(user_name: str) -> int:
        """
        counts how many projects a user has
        :param user_name: the name of the user we want to check
        :return: the amount of projects a user has
        """
        return len(ProjectManager._list_projects(user_name))

    @staticmethod
    def add_project(project: Project) -> Response:
        """
        add a project to a user (if possible)
        :param project: the project were trying to create
        :return: the response to the request
        """

        if not ProjectManager.is_user(project.user_name):  # makes sure the user exists
            return ProjectManager.E_USER_DOESNT_EXIST

        if ProjectManager._count_projects(project.user_name) == ProjectManager.USER_PROJECT_LIMIT:
            # checks if user exceeds project limit
            return ProjectManager.E_PROJECT_LIMIT_REACHED

        if project.exists():  # checks if the project exists
            return ProjectManager.E_PROJECT_ALREADY_EXISTS

        if not project.create():  # failed for some reason were not sure of
            return ProjectManager.E_UNKNOWN_ERROR

        return ProjectManager.S_PROJECT_CREATED

    @staticmethod
    def update_project_permissions(user: str, project: Project, write: bool = None) -> Response:
        """
        updates the permissions of a user MAKE SURE WHO EVER SUBMITTED THE REQUEST IS QUALIFIED TO DO IT!!!
        :param user: the user who's permissions we want to update
        :param project: the project who's permissions we want to update
        :param write: the access we want to grant (True for write, False for readonly, None to delete access)
        :return: the response to the request
        """
        if not project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST

        if not ProjectManager.is_user(user):
            return ProjectManager.E_USER_DOESNT_EXIST

        if project.user_name == user:
            return ProjectManager.E_CANT_CHANGE_OWNER_ACCESS
        # deletes permissions for users who no longer exist
        perms = project.list_permission()
        for p in perms:
            if not ProjectManager.is_user(p[0]):
                project.delete_permission(p[0])
        perms = project.list_permission()
        if len(perms) == ProjectManager.PROJECT_SHARING_LIMIT:
            return ProjectManager.E_PROJECT_SHARE_LIMIT_REACHED

        if not (write is None):
            project.give_permissions(user, write)
        elif user in [a[0] for a in perms]:
            project.delete_permission(user)
        else:
            return ProjectManager.E_CANT_DELETE_NON_EXISTENT_ACCESS

        return ProjectManager.S_ACCESS_GRANTED

    @staticmethod
    def commit_to(project: Project, commit: Commit) -> Response:
        """
        this method commits a new commit to a given project (if possible)
        :param project: the project being commited to
        :param commit: the commit we are trying to commit to the project
        :return: a Response object with the fitting response message
        """
        if not ProjectManager.is_user(commit.user):
            return ProjectManager.E_USER_DOESNT_EXIST
        elif not project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST
        elif not ProjectManager.authenticate_permissions(user=commit.user, target_project=project, write=True):
            return ProjectManager.E_BAD_PERMISSIONS
        elif len(commit.data) > ProjectManager.COMMIT_SIZE_LIMIT:
            return ProjectManager.E_BAD_COMMIT_SIZE
        elif project.count_commits() >= Project.COMMIT_LIMIT:
            return ProjectManager.E_COMMIT_LIMIT_REACHED
        elif project != commit.project:
            return ProjectManager.E_UNKNOWN_ERROR
        elif not commit.commit():
            return ProjectManager.E_UNKNOWN_ERROR
        return ProjectManager.S_COMMIT_SUCCESSFUL

    @staticmethod
    def delete_project(project: Project):
        """
        deletes a project, ONLY USE IF THE USER WHO ASKS FOR DELETION IS THE OWNER
        :param project: the project we want to delete
        :return: Response object
        """
        if project.delete():
            return ProjectManager.S_PROJECT_DELETED
        else:
            return ProjectManager.E_PROJECT_DOESNT_EXIST

    @staticmethod
    def delete_commit(commit: Commit):
        """
        deletes a commit, ONLY USE IF THE USER ASKING FOR DELETION IS THE OWNER
        :param commit: the commit to delete
        :return: a Response object with the fitting response
        """
        if not commit.project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST
        if not commit.exists():
            return ProjectManager.E_COMMIT_DOESNT_EXIST
        if not commit.delete():
            return ProjectManager.E_UNKNOWN_ERROR

        return ProjectManager.S_COMMIT_DELETED

    @staticmethod
    def get_commit_data(user: str, project: Project, commit_number: int) -> Response:
        """
        gets the data stored in a specific commit
        :param user: the user making the request
        :param project: the project the commit belongs to
        :param commit_number: the number of the commit
        :return: a response object detailing the actions success
        """
        if not project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST
        if not ProjectManager.authenticate_permissions(user, project, False):
            return ProjectManager.E_BAD_PERMISSIONS
        if not ((project.count_commits() > commit_number) and (commit_number >= 0)):
            return ProjectManager.E_COMMIT_DOESNT_EXIST
        commit = Commit.from_commit_number(commit_number, project)
        return Response(True, base64.b64encode(commit.data))

    @staticmethod
    def get_commit_info(user: str, project: Project, commit_number: int) -> Response:
        """
        gets the info on a specific commit
        :param user: the user making the request
        :param project: the project the commit belongs to
        :param commit_number: the number of the commit
        :return: a response object detailing the actions success
        """
        if not project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST
        if not ProjectManager.authenticate_permissions(user, project, False):
            return ProjectManager.E_BAD_PERMISSIONS
        if not ((project.count_commits() > commit_number) and (commit_number >= 0)):
            return ProjectManager.E_COMMIT_DOESNT_EXIST
        commit = Commit.from_commit_number(commit_number, project)
        return Response(True, commit.to_metadata())

    @staticmethod
    def get_project_info(user: str, project: Project) -> Response:
        """
        gets the projects info
        :param user: the user making the request
        :param project: the project to check
        :return: response object detailing the actions success
        """
        if not project.exists():
            return ProjectManager.E_PROJECT_DOESNT_EXIST
        if not ProjectManager.authenticate_permissions(user, project, False):
            return ProjectManager.E_BAD_PERMISSIONS
        return Response(True, project.get_info())

