import json
from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from srbusapi.exceptions import EncryptionError, DecryptionError


def encrypt(base_dict: dict, b64_key: bytes, b64_iv: bytes) -> bytes:
    """
    Encrypts a dictionary using AES encryption in CBC mode.

    :param base_dict: The dictionary to encrypt.
    :param b64_key: The base64-encoded encryption key.
    :param b64_iv: The base64-encoded initialization vector.
    :return: The encrypted data, base64-encoded as bytes.
    :raises EncryptionError: If encryption fails due to invalid input or other errors.
    """
    try:
        if not isinstance(base_dict, dict):
            raise EncryptionError("Input data must be a dictionary")
        key = b64decode(b64_key)
        iv = b64decode(b64_iv)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(json.dumps(base_dict).encode("utf-8"), AES.block_size)

        encrypted_data = cipher.encrypt(padded_data)
        base64_encoded = b64encode(encrypted_data)

        return base64_encoded
    except (ValueError, TypeError) as e:
        raise EncryptionError(f"Encryption failed: {str(e)}") from e


def decrypt(cipher_text: bytes, b64_key: bytes, b64_iv: bytes) -> dict:
    """
    Decrypts data encrypted with AES encryption in CBC mode.

    :param cipher_text: The encrypted data, base64-encoded as bytes.
    :param b64_key: The base64-encoded encryption key.
    :param b64_iv: The base64-encoded initialization vector.
    :return: The decrypted data as a dictionary.
    :raises DecryptionError: If decryption fails due to invalid input or other errors.
    """
    try:
        key = b64decode(b64_key)
        iv = b64decode(b64_iv)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size)

        return json.loads(decrypted.decode("utf-8"))
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        raise DecryptionError(f"Decryption failed: {str(e)}") from e
