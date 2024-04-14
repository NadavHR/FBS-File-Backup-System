import base64
import io
import os
import zipfile
from typing import Callable


def decode(data: str) -> bytes:
    """
    decodes the data as given by the server
    :param data: the data as given by the server
    :return: the decoded data as bytes
    """
    return base64.b64decode(data)


def decompress(data: bytes, path: str):
    """
    decompresses data (bytes) as given after decoding the initial message from the server
    :param path: the path to save to
    :param data: the data to decompress
    """
    zipped = zipfile.ZipFile(io.BytesIO(data))

    zipped.extractall(path)


def save_commit_from_data(data_raw: str, save_path: str) -> bool:
    """
    saves a specific commit on the machine based on the data as given from the server
    :param data_raw: the data as given from the server
    :param save_path: the path to save the data to
    :return: a boolean signaling the data was successfully saved, in case it wasn't, you should usually get an exception
    the boolean is here for good measure.
    """
    data_bytes = decode(data_raw)
    decompress(data_bytes, save_path)
    return True


def encode(data: bytes) -> str:
    """
    encodes the zipped data bytes containing the data we want to send to the server
    :param data: the data (zipped)
    :return: a string encoded with the data
    """
    return base64.b64encode(data).decode()


def compress(path: str) -> bytes:
    """
    compress a directory so we can send it compressed
    :param path: the path to the dir
    :return: the bytes of the compressed directory
    """
    buffer = io.BytesIO()
    ziph = zipfile.ZipFile(buffer, "w",  zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))

    ziph.close()
    data = buffer.getvalue()
    buffer.close()
    return data


def compress_and_encode(path: str) -> str:
    """
    compresses a given dir and encodes it so you could send it to the server
    :param path: the path to the directory
    :return: the data in a form you can send to the server
    """
    compressed = compress(path)
    return encode(compressed)
