import base64
import hashlib
import json

import uvicorn
from fastapi import FastAPI, Request

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


def hash_password(password: str) -> bytes:
    """
    hashes a password
    :param password: the password
    :return: the hash of the password
    """
    return hashlib.sha256(password.encode()).hexdigest().encode()


@app.get("/login")
def login(user_name: str, password: str):
    user_name = decode(user_name)
    password = decode(password)

    return UserManager.login(user_name, hash_password(password)).to_dict()


@app.get("/logout")
def logout(session_id: int):
    return UserManager.logout(session_id).to_dict()


@app.get("/sign_up")
def sign_up(user_name: str, password: str):
    user_name = decode(user_name)
    password = decode(password)
    return UserManager.create_user(user_name, hash_password(password)).to_dict()


@app.get("/delete_user")
def delete_user(session_id: int):
    return UserManager.delete_user(session_id).to_dict()


@app.get("/get_commit_info")
def get_commit_info(session_id: int, project_name: str, project_owner: str, commit_id: int):
    project_owner = decode(project_owner)
    project_name = decode(project_name)
    return UserManager.get_commit_info(session_id=session_id, project_name=project_name, user_name=project_owner,
                                       commit_number=commit_id).to_dict()


@app.get("/get_commit_data")
def get_commit_data(session_id: int, project_name: str, project_owner: str, commit_id: int):
    project_name = decode(project_name)
    project_owner = decode(project_owner)
    return UserManager.get_commit_data(session_id=session_id, project_name=project_name, user_name=project_owner,
                                       commit_number=commit_id).to_dict()


@app.post("/commit")
async def commit(session_id: int, project_name: str, project_owner: str, commit_name: str,
           commit_message: str, request: Request):
    project_name = decode(project_name)
    project_owner = decode(project_owner)
    commit_name = decode(commit_name)
    commit_message = decode(commit_message)
    COMMIT_DATA_FIELD = "commit_data"
    j = await request.body()
    j = json.loads(j)
    commit_data = decode(j[COMMIT_DATA_FIELD]).encode()

    project = Project(project_owner, project_name)
    c = Commit.new_commit(user="", commit_name=commit_name,
                          commit_message=commit_message, project=project, data=base64.b64decode(commit_data))
    return UserManager.commit(session_id, c).to_dict()


@app.get("/delete_commit")
def delete_commit(session_id: int, project_name: str, commit_id: int):
    project_name = decode(project_name)

    return UserManager.delete_commit(session_id=session_id, project_name=project_name, commit_id=commit_id).to_dict()


@app.get("/get_project_info")
def get_project_info(session_id: int, project_name: str, project_owner: str):
    project_name = decode(project_name)
    project_owner = decode(project_owner)

    return UserManager.get_project_info(session_id, project_name, project_owner).to_dict()


@app.get("/get_user_projects")
def get_user_projects(session_id: int):
    return UserManager.get_user_projects(session_id).to_dict()


@app.get("/add_project")
def add_project(session_id: int, project_name: str, project_description: str):
    project_name = decode(project_name)
    project_description = decode(project_description)
    return UserManager.add_project(session_id, project_name, project_description).to_dict()


@app.get("/delete_project")
def delete_project(session_id: int, project_name: str):
    project_name = decode(project_name)
    return UserManager.delete_project(session_id, project_name).to_dict()


@app.get("/update_project_sharing")
def update_project_sharing(session_id: int, project_name: str, user_name: str, write: bool = None):
    project_name = decode(project_name)
    user_name = decode(user_name)
    return UserManager.update_project_permissions(session_id, project_name, user_name, write).to_dict()


def main():
    uvicorn.run(app, host="127.0.0.1", port=constants.Constants.COMMUNICATION_PORT)


if __name__ == '__main__':
    main()
