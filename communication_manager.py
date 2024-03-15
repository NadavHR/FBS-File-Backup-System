import uvicorn
from fastapi import FastAPI

import constants
from user_manager import UserManager
from commit import Commit
from project_class import Project

app = FastAPI()


def decode(s: str) -> str:  # TODO: implement
    """
    decodes messages from client
    :param s: the message to decode
    :return: the decoded string (json)
    """
    return s


def safe_to_int(int_s: str) -> int:
    """
    takes an integer as given by the client (string and encrypted) and returns it as an int
    :param int_s: the encrypted int string as sent to the server
    :return: decrypted int_s as an int or -1 if not an int
    """
    int_s = decode(int_s)
    try:
        return int(int_s)
    except:
        return -1


@app.get("/login")
def login(user_name: str, password: str):
    user_name = decode(user_name)
    password = decode(password)

    return UserManager.login(user_name, password.encode()).to_dict()


@app.get("/logout")
def logout(session_id: str):
    session_id = safe_to_int(session_id)
    return UserManager.logout(session_id).to_dict()


@app.get("/sign_up")
def sign_up(user_name: str, password: str):
    user_name = decode(user_name)
    password = decode(password)
    return UserManager.create_user(user_name, password.encode()).to_dict()


@app.get("/delete_user")
def delete_user(session_id: str):
    session_id = safe_to_int(session_id)

    return UserManager.delete_user(session_id).to_dict()


@app.get("/get_commit_info")
def get_commit_info(session_id: str, project_name: str, project_owner: str, commit_id: str):
    session_id = safe_to_int(session_id)
    project_owner = decode(project_owner)
    project_name = decode(project_name)
    commit_id = safe_to_int(commit_id)
    return UserManager.get_commit_info(session_id=session_id, project_name=project_name, user_name=project_owner,
                                       commit_number=commit_id).to_dict()


@app.get("/get_commit_data")
def get_commit_data(session_id: str, project_name: str, project_owner: str, commit_id: str):
    session_id = safe_to_int(session_id)
    project_name = decode(project_name)
    project_owner = decode(project_owner)
    commit_id = safe_to_int(commit_id)
    return UserManager.get_commit_data(session_id=session_id, project_name=project_name, user_name=project_owner,
                                       commit_number=commit_id).to_dict()


@app.get("/commit")
def commit(session_id: str, project_name: str, project_owner: str, commit_name: str,
           commit_message: str, commit_data: str):
    session_id = safe_to_int(session_id)
    project_name = decode(project_name)
    project_owner = decode(project_owner)
    commit_name = decode(commit_name)
    commit_message = decode(commit_message)
    commit_data = decode(commit_data).encode()

    project = Project(project_owner, project_name)
    c = Commit.new_commit(user="", commit_name=commit_name,
                          commit_message=commit_message, project=project, data=commit_data)
    return UserManager.commit(session_id, c).to_dict()


@app.get("/delete_commit")
def delete_commit(session_id: str, project_name: str, commit_id: str):
    session_id = safe_to_int(session_id)
    project_name = decode(project_name)
    commit_id = safe_to_int(commit_id)

    return UserManager.delete_commit(session_id=session_id, project_name=project_name, commit_id=commit_id).to_dict()


@app.get("/get_project_info")
def get_project_info(session_id: str, project_name: str, project_owner: str):
    session_id = safe_to_int(session_id)
    project_name = decode(project_name)
    project_owner = decode(project_owner)

    return UserManager.get_project_info(session_id, project_name, project_owner).to_dict()


@app.get("/get_user_projects")
def get_user_projects(session_id: str):
    session_id = safe_to_int(session_id)
    return UserManager.get_user_projects(session_id).to_dict()


@app.get("/add_project")
def add_project(session_id: str, project_name: str, project_description: str):
    session_id = safe_to_int(session_id)
    project_name = decode(project_name)
    project_description = decode(project_description)
    return UserManager.add_project(session_id, project_name, project_description).to_dict()


@app.get("/delete_project")
def delete_project(session_id: str, project_name: str):
    session_id = safe_to_int(session_id)
    project_name = decode(project_name)
    return UserManager.delete_project(session_id, project_name).to_dict()


@app.get("/update_project_sharing")
def update_project_sharing(session_id: str, project_name: str, user_name: str, write: bool = None):
    session_id = safe_to_int(session_id)
    project_name = decode(project_name)
    user_name = decode(user_name)
    return UserManager.update_project_permissions(session_id, project_name, user_name, write).to_dict()


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=constants.Constants.COMMUNICATION_PORT)
