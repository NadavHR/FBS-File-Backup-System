from Response import Response


class Constants:
    USER_PROJECT_LIMIT = 8
    PROJECT_SHARING_LIMIT = 32
    PROJECT_DESCRIPTION_SIZE_LIMIT = 128
    PROJECT_NAME_SIZE_LIMIT = 2048

    # possible errors:
    E_USER_DOESNT_EXIST = Response(success=False, response_message="user does not exist")
    E_PROJECT_DOESNT_EXIST = Response(success=False, response_message="project does not exist")
    E_BAD_PERMISSIONS = Response(success=False, response_message="you don't have the right permissions to this project")
    E_BAD_COMMIT_SIZE = Response(success=False, response_message="commit size too big")
    E_COMMIT_LIMIT_REACHED = Response(success=False, response_message="can not add any more commits to this project")
    E_UNKNOWN_ERROR = Response(success=False, response_message="unknown error has occurred")
    E_PROJECT_ALREADY_EXISTS = Response(success=False, response_message="project already exists")
    E_PROJECT_LIMIT_REACHED = Response(success=False, response_message="user at project_limit")
    E_PROJECT_SHARE_LIMIT_REACHED = Response(success=False,
                                             response_message="can not share project with any more users")
    E_CANT_CHANGE_OWNER_ACCESS = Response(success=False, response_message="can't modify the owners access")
    E_CANT_DELETE_NON_EXISTENT_ACCESS = Response(success=False, response_message="can't delete access to a user who had"
                                                                                 " no access to begin with")

    # possible success messages
    S_PROJECT_CREATED = Response(success=True, response_message="successfully created project")
    S_ACCESS_GRANTED = Response(success=True, response_message=f"successfully modified access to user")
    S_COMMIT_SUCCESSFUL = Response(success=True, response_message="successfully created new commit")
    S_PROJECT_DELETED = Response(success=True, response_message="successfully deleted project")

    USERS_DIR = "users"
    PROJECTS_DIR = "projects"
    # to access a project {USERS_DIR}\{user_name}\{PROJECTS_DIR}\{project_name}
    USER_SHARED_DIR = "shared"  # this dir contains a folder for every user who shares a project with this user and a
    # file named after the project for every project that user shares with the current user
    # to access shared projects {USERS_DIR}\{user_name}\{USER_SHARED_DIR}\{checked_user}\{checked_project}
    PROJECT_PERMISSIONS_DIR = "permissions"  # this dir contains a folder for every user with permissions and the folder
    # is either empty (meaning readonly permissions) or has an empty file meaning write permissions
    # to access permissions {path_to_project}\{PROJECT_PERMISSIONS_DIR}\{user_name}
    PROJECT_METADATA_FILE = "metadata.json"
    # to access {path_to_project}\{PROJECT_METADATA_FILE}
    WRITE_PERMISSION_FILE_NAME = "W"
    # a user with write access {path_to_project}\{PROJECT_PERMISSIONS_DIR}\{user_name}\{WRITE_PERMISSION_FILE_NAME}
    COMMIT_DIR = "last_commit"  # every commit has a folder named as such so it points to the last commit
    # to access commits {path_to_project}\({COMMIT_DIR}\*n) with n being the number of commits you want to go back
    COMMIT_DATA_FILE = "data"
    # to access commit data {path_to_commit}\{COMMIT_DATA}
    COMMIT_NUMBER_FILE = "n"  # a file that only contains the commit number
    # to access commit number {path_to_commit}\{COMMIT_NUMBER_FILE}
    COMMIT_METADATA_FILE = "metadata.json"  # a json that contains the commits metadata
    # to access metadata {path_to_commit}\{COMMIT_METADATA_FILE}
    COMMIT_LIMIT = 50  # the maximum amount of commits in a project
    COMMIT_SIZE_LIMIT = 64000000  # the maximum size of commit data (64mb)
    COMMIT_MESSAGE_LIMIT = 512  # maximum length of commit message
    COMMIT_NAME_LIMIT = 64  # maximum length of commit name

    COMMIT_USER_FIELD = "user"  # the key to the commit user in the metadata json
    COMMIT_DATE_FIELD = "time"  # the key to the commit time in the metadata json
    COMMIT_NAME_FIELD = "name"  # the key to the commit name in the metadata json
    COMMIT_MSG_FIELD = "message"  # the key to the commit msg in the metadata json

    PROJECT_DESCRIPTION_FIELD = "description"  # the key to the projects description in project metadata
    PROJECT_DATE_FIELD = "time"  # the key to the projects creation time in project metadata