import json
import requests
import client.file_utils as file_utils

URL = "http://127.0.0.1:7112"
SUCCESS_FIELD = "success"
MSG_FIELD = "message"

USER_NAME_FIELD = "user_name"
PASSWORD_FIELD = "password"
SESSION_ID_FIELD = "session_id"
PROJECT_NAME_FIELD = "project_name"
PROJECT_OWNER_FIELD = "project_owner"
PROJECT_DESCRIPTION_FIELD = "project_description"
COMMIT_ID_FIELD = "commit_id"
COMMIT_NAME_FIELD = "commit_name"
COMMIT_MESSAGE_FIELD = "commit_message"
COMMIT_DATA_FIELD = "commit_data"
WRITE_PERMISSION_FIELD = "write"

SESSION_ID_CACHE_PATH = "session_id_cache.txt"


current_session_id = None


def cache_session_id(session_id: int):
    global current_session_id
    current_session_id = session_id
    try:
        f = open(SESSION_ID_CACHE_PATH, "w")
        f.write(str(session_id))
        f.close()
    except:
        pass


def get_cached_session_id() -> int or None:
    global current_session_id
    if not (current_session_id is None):
        return current_session_id
    try:
        f = open(SESSION_ID_CACHE_PATH, "r")
        session_id = f.read()
        f.close()
        session_id = int(session_id)
        current_session_id = session_id
        return session_id
    except:
        return None





def encode(s: str) -> str:
    """
    encodes messages to the server
    :param s: the message to encode
    :return: the encoded string
    """
    return s


def login(user_name: str, password: str) -> (bool, int or str):
    """
    logs user in
    :param user_name: the username
    :param password: the password
    :return: boolean and session id or error message
    """
    params = {USER_NAME_FIELD: encode(user_name),
              PASSWORD_FIELD: encode(password)}
    resp = (requests.get(url=f"{URL}/login", params=params)).json()
    if resp[SUCCESS_FIELD]:
        session_id = int(resp[MSG_FIELD])
        cache_session_id(session_id)
        return resp[SUCCESS_FIELD], session_id
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]



def logout(session_id: int) -> (bool, str):
    """
    logs user out of session
    :param session_id: the id of the session
    :return: boolean and response message
    """
    resp = requests.get(url=f"{URL}/logout", params={SESSION_ID_FIELD: session_id}).json()
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]


def sign_up(user_name: str, password: str) -> (bool, int or str):
    """
    sign user up
    :param user_name: the username
    :param password: the password
    :return: boolean and session id or error message
    """
    params = {USER_NAME_FIELD: encode(user_name),
              PASSWORD_FIELD: encode(password)}
    resp = (requests.get(url=f"{URL}/sign_up", params=params)).json()
    if resp[SUCCESS_FIELD]:
        session_id = int(resp[MSG_FIELD])
        cache_session_id(session_id)
        return resp[SUCCESS_FIELD], session_id
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]


def delete_user(session_id: int) -> (bool, str):
    """
    deletes a user
    :param session_id: the id of the session
    :return: boolean and response message
    """
    resp = requests.get(url=f"{URL}/delete_user", params={SESSION_ID_FIELD: session_id}).json()
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]


def get_commit_info(session_id: int, project_name: str, project_owner: str, commit_id: int) -> (bool, dict or str):
    """
    gets the info on a certain commit
    :param session_id: id of the session
    :param project_name: the name of the project
    :param project_owner: the username of the project owner
    :param commit_id: the id of the commit
    :return: boolean and dict of info on commit or error message
    """
    params = {
        SESSION_ID_FIELD: session_id,
        PROJECT_NAME_FIELD: encode(project_name),
        PROJECT_OWNER_FIELD: encode(project_owner),
        COMMIT_ID_FIELD: commit_id
    }
    resp = requests.get(url=f"{URL}/get_commit_info", params=params).json()
    return resp[SUCCESS_FIELD], (json.loads(resp[MSG_FIELD])) if resp[SUCCESS_FIELD] else resp[MSG_FIELD]


def get_commit_data(session_id: int, project_name: str, project_owner: str, commit_id: int, path: str) -> (
bool, bool or str):
    """
    gets the info on a certain commit
    :param path: path to save the data to
    :param session_id: id of the session
    :param project_name: the name of the project
    :param project_owner: the username of the project owner
    :param commit_id: the id of the commit
    :return: boolean and boolean showing if saved successfully or error message
    """
    params = {
        SESSION_ID_FIELD: session_id,
        PROJECT_NAME_FIELD: encode(project_name),
        PROJECT_OWNER_FIELD: encode(project_owner),
        COMMIT_ID_FIELD: commit_id
    }
    resp = requests.get(url=f"{URL}/get_commit_data", params=params).json()
    return resp[SUCCESS_FIELD], file_utils.save_commit_from_data(resp[MSG_FIELD], path) if \
        resp[SUCCESS_FIELD] else resp[MSG_FIELD]


def commit(session_id: int, project_name: str, project_owner: str, commit_name: str,
           commit_message: str, path_to_data: str) -> (bool, str):
    """
    commits a new commit to the project
    :param session_id: the id of the session
    :param project_name: the name of the project
    :param project_owner: the owner of the project
    :param commit_name: the name of the commit
    :param commit_message: commit message
    :param path_to_data: path to the data
    :return: boolean and response message
    """

    params = {SESSION_ID_FIELD: session_id,
              PROJECT_NAME_FIELD: encode(project_name),
              PROJECT_OWNER_FIELD: encode(project_owner),
              COMMIT_NAME_FIELD: encode(commit_name),
              COMMIT_MESSAGE_FIELD: encode(commit_message)
              }

    resp = requests.post(url=f"{URL}/commit", params=params,
                         json={COMMIT_DATA_FIELD: encode(file_utils.compress_and_encode(path_to_data))}).json()
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]


def delete_commit(session_id: int, project_name: str, commit_id: int) -> (bool, str):
    """
    deletes a commit
    :param session_id: the id of the session
    :param project_name: the name of the project
    :param commit_id: the id of the commit
    :return: boolean and response message
    """

    params = {
        SESSION_ID_FIELD: session_id,
        PROJECT_NAME_FIELD: encode(project_name),
        COMMIT_ID_FIELD: commit_id
    }
    resp = requests.get(url=f"{URL}/delete_commit", params=params).json()
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]


def get_project_info(session_id: int, project_name: str, project_owner: str) -> (bool, dict or str):
    """
    gets the info on a project
    :param session_id: the id of the session
    :param project_name: the name of the project
    :param project_owner: the owner of the project
    :return: boolean and dict with info on project or error message
    """
    params = {SESSION_ID_FIELD: session_id,
              PROJECT_NAME_FIELD: encode(project_name),
              PROJECT_OWNER_FIELD: encode(project_owner)}
    resp = requests.get(url=f"{URL}/get_project_info", params=params).json()
    return resp[SUCCESS_FIELD], json.loads(resp[MSG_FIELD]) if resp[SUCCESS_FIELD] else resp[MSG_FIELD]


def get_user_projects(session_id: int) -> (bool, dict or str):
    """
    gets all of the projects accessible by this user
    :param session_id: the id of the session
    :return: boolean and dict of projects and shared projects or error message
    """
    params = {SESSION_ID_FIELD: session_id}
    resp = requests.get(url=f"{URL}/get_user_projects", params=params).json()
    return resp[SUCCESS_FIELD], json.loads(resp[MSG_FIELD]) if resp[SUCCESS_FIELD] else resp[MSG_FIELD]


def add_project(session_id: int, project_name: str, project_description: str) -> (bool, str):
    """
    adds a new project to the user's projects
    :param session_id: the id of the session
    :param project_name: the name of the project
    :param project_description: description of project
    :return: boolean and response message
    """
    params = {
        SESSION_ID_FIELD: session_id,
        PROJECT_NAME_FIELD: encode(project_name),
        PROJECT_DESCRIPTION_FIELD: encode(project_description)
    }
    resp = requests.get(url=f"{URL}/add_project", params=params).json()
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]


def delete_project(session_id: int, project_name: str) -> (bool, str):
    """
    deletes a project
    :param session_id: the id of the session
    :param project_name: the name of the project
    :return: boolean and response message
    """
    params = {SESSION_ID_FIELD: session_id,
              PROJECT_NAME_FIELD: encode(project_name)}
    resp = requests.get(url=f"{URL}/delete_project", params=params).json()
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]


def update_project_sharing(session_id: int, project_name: str, user_name: str, write: bool = None) -> (bool, str):
    """
    updates the permissions to a project
    :param write: true for write, false for readonly, None for no permissions
    :param user_name: the name of the user who's access is to be updated
    :param session_id: the id of the session
    :param project_name: the name of the project
    :return: boolean and response message
    """
    params = {SESSION_ID_FIELD: session_id,
              PROJECT_NAME_FIELD: encode(project_name),
              USER_NAME_FIELD: encode(user_name)}
    if not (write is None):
        params[WRITE_PERMISSION_FIELD] = write
    resp = requests.get(url=f"{URL}/update_project_sharing", params=params).json()
    return resp[SUCCESS_FIELD], resp[MSG_FIELD]
