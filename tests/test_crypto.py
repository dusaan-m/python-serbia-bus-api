import pytest
import base64
from Crypto.Cipher import AES

from srbusapi.crypto import encrypt, decrypt
from srbusapi.exceptions import EncryptionError, DecryptionError


class TestCryptoFunctions:
    def test_encrypt_decrypt_round_trip(self):
        # Prepare test data
        test_dict = {
            "string_test": "test",
            "number_test": 123,
            "bool_test": False,
            "list_test": ["users", "guests"],
        }

        # Generate a random 256-bit key and IV
        key = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        # Encrypt
        encrypted = encrypt(test_dict, key, iv)

        # Decrypt
        decrypted = decrypt(encrypted, key, iv)

        # Verify
        assert decrypted == test_dict

    def test_encrypt_complex_data(self):
        # Test with a more complex nested dictionary
        test_dict = {
            "station": {
                "id": 123,
                "buses": {"number": 49, "route": ["123123,123123", "4566546,45645654"]},
            },
            "timestamp": 1609459200,
        }

        key = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        encrypted = encrypt(test_dict, key, iv)
        decrypted = decrypt(encrypted, key, iv)

        assert decrypted == test_dict

    def test_encrypt_invalid_key(self):
        # Test encryption with invalid key
        test_dict = {"data": "test"}

        # Invalid base64 encoded key
        invalid_key = base64.b64encode(b"short")
        iv = base64.b64encode(AES.get_random_bytes(16))

        with pytest.raises(EncryptionError, match="Encryption failed"):
            encrypt(test_dict, invalid_key, iv)

    def test_decrypt_invalid_key(self):
        # Prepare a valid encrypted payload
        test_dict = {"data": "test"}
        key = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        encrypted = encrypt(test_dict, key, iv)

        # Try decrypting with invalid key
        invalid_key = base64.b64encode(b"short")

        with pytest.raises(DecryptionError, match="Decryption failed"):
            decrypt(encrypted, invalid_key, iv)

    def test_encrypt_invalid_input_type(self):
        # Test encryption with invalid input type
        string_data = "test"

        key = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        with pytest.raises(EncryptionError, match="Input data must be a dictionary"):
            # noinspection PyTypeChecker
            encrypt(string_data, key, iv)

    def test_decrypt_tampered_cipher_text(self):
        # Prepare a valid encrypted payload
        test_dict = {"data": "test"}
        key = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        encrypted = encrypt(test_dict, key, iv)

        # Tamper with the cipher text
        tampered_encrypted = encrypted[:-1] + b"0"

        with pytest.raises(DecryptionError, match="Decryption failed"):
            decrypt(tampered_encrypted, key, iv)

    def test_encrypt_empty_dict(self):
        # Test encrypting an empty dictionary
        test_dict = {}
        key = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        encrypted = encrypt(test_dict, key, iv)
        decrypted = decrypt(encrypted, key, iv)

        assert decrypted == test_dict

    def test_encrypt_null_values(self):
        # Test with null/None values
        test_dict = {"bus": None, "station": False, "bus_lines": [None, 123]}

        key = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        encrypted = encrypt(test_dict, key, iv)
        decrypted = decrypt(encrypted, key, iv)

        assert decrypted == test_dict

    def test_different_keys_produce_different_cipher_texts(self):
        # Ensure different keys produce different encrypted outputs
        test_dict = {"data": "test"}

        key1 = base64.b64encode(AES.get_random_bytes(32))
        key2 = base64.b64encode(AES.get_random_bytes(32))
        iv = base64.b64encode(AES.get_random_bytes(16))

        encrypted1 = encrypt(test_dict, key1, iv)
        encrypted2 = encrypt(test_dict, key2, iv)

        assert encrypted1 != encrypted2

    def test_key_and_iv_length(self):
        # Test various key and IV lengths
        test_dict = {"data": "test"}

        # Test 256-bit key (32 bytes)
        key_256 = base64.b64encode(AES.get_random_bytes(32))
        iv_16 = base64.b64encode(AES.get_random_bytes(16))

        encrypted = encrypt(test_dict, key_256, iv_16)
        decrypted = decrypt(encrypted, key_256, iv_16)

        assert decrypted == test_dict

        # Additional length checks could be added here if needed
