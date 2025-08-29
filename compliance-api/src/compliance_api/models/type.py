"""EncryptedType."""

import base64

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from flask import current_app
from sqlalchemy.types import String, TypeDecorator


class EncryptedType(TypeDecorator):  # pylint: disable=too-many-ancestors
    """Custom type for reversible encryption using AES."""

    impl = String  # Use the base type that this will convert to/from

    def _get_cipher_suite(self, initialization_vector):  # pylint: disable=no-self-use
        """Create a new cipher object with the provided IV."""
        return AES.new(
            current_app.config["DB_ECRPT_KEY"].encode("utf-8"),
            AES.MODE_CBC,
            initialization_vector,
        )

    def process_bind_param(self, value, dialect):  # pylint: disable=no-self-use
        """Encrypt the value before storing in the database."""
        if value is not None:
            initialization_vector = get_random_bytes(
                AES.block_size
            )  # Generate a new IV for each encryption
            cipher = self._get_cipher_suite(initialization_vector)
            padded_value = pad(value.encode("utf-8"), AES.block_size)
            encrypted_value = cipher.encrypt(padded_value)
            # Prepend the IV to the encrypted data
            return base64.b64encode(initialization_vector + encrypted_value).decode(
                "utf-8"
            )
        return None

    def process_result_value(self, value, dialect):  # pylint: disable=no-self-use
        """Decrypt the value when retrieving from the database."""
        if value is not None:
            encrypted_value = base64.b64decode(value.encode("utf-8"))
            # Extract the IV
            initialization_vector = encrypted_value[:AES.block_size]
            encrypted_value = encrypted_value[AES.block_size :]
            cipher = self._get_cipher_suite(initialization_vector)
            decrypted_value = unpad(cipher.decrypt(encrypted_value), AES.block_size)
            return decrypted_value.decode("utf-8")
        return None

    def process_literal_param(self, value, dialect):  # pylint: disable=no-self-use
        """Process literal values in SQLAlchemy expressions."""
        return self.process_bind_param(value, dialect)

    @property
    def python_type(self):
        """Return the Python type corresponding to this type."""
        return str
