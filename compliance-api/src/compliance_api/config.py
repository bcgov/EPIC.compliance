# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""All of the configuration for the service is captured here.

All items are loaded,
or have Constants defined here that are loaded into the Flask configuration.
All modules and lookups get their configuration from the Flask config,
rather than reading environment variables directly or by accessing this configuration directly.
"""

import os
import sys

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())


def get_named_config(config_name: str = "development"):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ["production", "staging", "default"]:
        config = ProdConfig()
    elif config_name == "testing":
        config = TestConfig()
    elif config_name == "development":
        config = DevConfig()
    elif config_name == "docker":
        config = DockerConfig()
    else:
        raise KeyError("Unknown configuration '{config_name}'")
    return config


class _Config:  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults for all the other configurations."""

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = "a secret"

    TESTING = False
    DEBUG = False

    # POSTGRESQL
    DB_USER = os.getenv("DATABASE_USERNAME", "")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DB_NAME = os.getenv("DATABASE_NAME", "")
    DB_HOST = os.getenv("DATABASE_HOST", "")
    DB_PORT = os.getenv("DATABASE_PORT", "5432")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"
    )
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # JWT_OIDC Settings

    # Service account details
    KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")
    KEYCLOAK_REALMNAME = os.getenv("KEYCLOAK_REALMNAME", "compliance")
    KEYCLOAK_SERVICE_ACCOUNT_ID = os.getenv("MET_ADMIN_CLIENT_ID")
    KEYCLOAK_SERVICE_ACCOUNT_SECRET = os.getenv("MET_ADMIN_CLIENT_SECRET")
    # TODO separate out clients for APIs and user management.
    # TODO API client wont need user management roles in keycloak.
    KEYCLOAK_ADMIN_USERNAME = os.getenv("MET_ADMIN_CLIENT_ID")
    KEYCLOAK_ADMIN_SECRET = os.getenv("MET_ADMIN_CLIENT_SECRET")
    AUTH_BASE_URL = os.getenv("AUTH_BASE_URL")
    EPIC_TRACK_URL = os.getenv("EPIC_TRACK_URL")

    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv("JWT_OIDC_WELL_KNOWN_CONFIG")
    JWT_OIDC_ALGORITHMS = os.getenv("JWT_OIDC_ALGORITHMS", "RS256")
    JWT_OIDC_JWKS_URI = os.getenv("JWT_OIDC_JWKS_URI")
    JWT_OIDC_ISSUER = os.getenv("JWT_OIDC_ISSUER")
    JWT_OIDC_AUDIENCE = os.getenv("JWT_OIDC_AUDIENCE", "account")
    JWT_OIDC_CACHING_ENABLED = os.getenv("JWT_OIDC_CACHING_ENABLED", "True")
    JWT_OIDC_CACHING_ENABLED = os.getenv("JWT_OIDC_CACHING_ENABLED", "True")
    APP_NAME = os.getenv("app_name", "")
    SECRET_KEY = os.getenv("secret_key", "")
    
    JWT_OIDC_JWKS_CACHE_TIMEOUT = 300


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Dev Config."""

    TESTING = False
    DEBUG = True
    print(f"SQLAlchemy URL (DevConfig): {_Config.SQLALCHEMY_DATABASE_URI}")


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.used by the py.test suite."""

    DEBUG = True
    TESTING = True

    # POSTGRESQL
    DB_USER = os.getenv("DATABASE_TEST_USERNAME", "postgres")
    DB_PASSWORD = os.getenv("DATABASE_TEST_PASSWORD", "postgres")
    DB_NAME = os.getenv("DATABASE_TEST_NAME", "postgres")
    DB_HOST = os.getenv("DATABASE_TEST_HOST", "localhost")
    DB_PORT = os.getenv("DATABASE_TEST_PORT", "5432")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"
    )

    JWT_OIDC_TEST_MODE = True
    # JWT_OIDC_ISSUER = _get_config('JWT_OIDC_TEST_ISSUER')
    JWT_OIDC_TEST_AUDIENCE = os.getenv("JWT_OIDC_TEST_AUDIENCE")
    # JWT_OIDC_TEST_CLIENT_SECRET = os.getenv("JWT_OIDC_TEST_CLIENT_SECRET")
    JWT_OIDC_TEST_ISSUER = os.getenv("JWT_OIDC_TEST_ISSUER")
    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv("JWT_OIDC_TEST_WELL_KNOWN_CONFIG")
    JWT_OIDC_TEST_ALGORITHMS = os.getenv("JWT_OIDC_TEST_ALGORITHMS")
    JWT_OIDC_TEST_JWKS_URI = os.getenv("JWT_OIDC_TEST_JWKS_URI", default=None)
    JWT_OIDC_TEST_KEYS = {
        "keys": [
            {
                "kid": "epic-compliance",
                "kty": "RSA",
                "alg": "RSA256",
                "use": "sig",
                "n": "3VRgQebxojvZlZv+rySZioGXjK5Ky4YOZ0LxFbQztwY93XaPeutDKAp7wNaYfRrx1Gwu0PpBgj+Lmg3vTqPvjR"
                "b0Uc23hr1cT68hHxgjIjvk7xXzGv66xwIPOWZXed4LcLbdCf67qvjjFT3ZD7poXnXM5lWlBHrIHQ5s7iUia9eHwoe96d"
                "DRzvDGrsoUvs1z5BdKvXby5usNQSWl6a0jrJ0KBatIY//9k8mwmDZ7iBEz4ag9ly1KXiwMQfzdSo5r/xX63sV/8P33Aj"
                "LtDEZYTUDr/YVMyh7G5MocyIDOM89dXpX3qdRY1RvTK0+Tg+hshMZQyEXO8qui/FrXhCrPVw==",
                "e": "AQAB",
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_JWKS = {
        "keys": [
            {
                "kid": "epic-compliance",
                "kty": "RSA",
                "alg": "RSA256",
                "use": "sig",
                "n": "3VRgQebxojvZlZv+rySZioGXjK5Ky4YOZ0LxFbQztwY93XaPeutDKAp7wNaYfRrx1Gwu0PpBgj+Lmg3vTqPvjRb0Uc23hr"
                "1cT68hHxgjIjvk7xXzGv66xwIPOWZXed4LcLbdCf67qvjjFT3ZD7poXnXM5lWlBHrIHQ5s7iUia9eHwoe96dDRzvDGrsoUvs"
                "1z5BdKvXby5usNQSWl6a0jrJ0KBatIY//9k8mwmDZ7iBEz4ag9ly1KXiwMQfzdSo5r/xX63sV/8P33AjLtDEZYTUDr/YVMyh"
                "7G5MocyIDOM89dXpX3qdRY1RvTK0+Tg+hshMZQyEXO8qui/FrXhCrPVw==",
                "e": "AQAB",
                "d": "eXTgDcoqN5kYYh1kucAf8f4DqFPM/7rlFI2LtxlYd8uZD3sMaavJAqQeHUimDaFHrAZh+pQadttgRH35IPKddpNuJ6X4X"
                "Jx1l9THHEUmopaznvAwpFO9M5BRwnIC9wF+za/LxLxhSAWkt/dksljdBVknxA6jq72lKyzLYjRGm155+O8vBeEOctsgJoEDso"
                "5pIf4MxQVedD3dFORjAX2ufbsDhxhw3OV5rOpzYCQ4KCsOFYcEFWVQs2j/PSkUiby2rCmxfVn/FYfXgNhYlNPcEdYZ+wtTCazs"
                "j/VidQ4iu1R18e1b7fhp630+qzjRCPwNLZcdqWisgMNR/JfFKn5boQ==",
                "p": "APKukszUOTbKcZzuXVo3F+8V7ZCWqwF5UXM6WILoWXDdECf+OW2M6VeEcqwd2CyvX2NTSFXmtptgnfaDNb4x7cim9mO2ZED"
                "rxyqH8NzMSDrxeWGa710yz0zekI7xuvc5fzs0hP+paHBumBDIj5wLDFt25yAt7qLvmMh1v7B4rP+t",
                "q": "AOl50x3AM4yjrXeVw5V2IFKpYb4Ag4pJqjhuJcYOZCCijWo6fzV9ClvJGKjkAXvx3sktceq7pLzhTDyYbCq4uMe59ChRyHxi"
                "A9Mp7+FnVs0qrTue8GEpk3uG7+Ce7uYzSwcZGfP2mI3bdXqhc2399nleBWCawEB5S2GaGPY559uT",
                "dp": "AN1At+oy2m7Pp0FyOH4VmKaLkWmvU/0mBFJPsX64I0M46I/twaHVRLBbusic9QfYY9kEhwB6NaX3Mk0bVxYuIyI6xowmL8T"
                "YsV5fTgOf44KJwSZxwSVxO3pTt+v7C4B2VT8/JLqKUwOecNlsYTHdCMki4JmABv9Z/itU3w0fGGqJ",
                "dq": "fO4PJZA/BTZgD+k3arZ2vUSdZInp2Qlp6CAoXj49HaldekYq43gxHsQQSe8XTDc0OvnyRuR5VghIPvRgjMujNFwwZZK9cLE"
                "R0uBR147wR4BaidiWT6drn2Go4cypkMxJjVbFKGH/Z4jS5/eUSHrodDD3N6YW0WkWCPfn+3kos7k=",
                "qi": "AJd7yPx3l6dEoYNkhGL/mGURwOBVq54HIh2O8BAJZE5gKgmtOnDndYlvNn2Nt3+O40bDM281PamSDN6lcbfTTcMmqzPWx0"
                "LWSga1w04ugaQIJltfJpxVaelVL4IydKlPQ8hU6Jp8H1EIdC15U4D3bsvWVBHXewqhKChqmBbrRIUk",
            }
        ]
    }

    JWT_OIDC_TEST_PRIVATE_KEY_PEM = """-----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEA3VRgQebxojvZlZv+rySZioGXjK5Ky4YOZ0LxFbQztwY93XaP
    eutDKAp7wNaYfRrx1Gwu0PpBgj+Lmg3vTqPvjRb0Uc23hr1cT68hHxgjIjvk7xXz
    Gv66xwIPOWZXed4LcLbdCf67qvjjFT3ZD7poXnXM5lWlBHrIHQ5s7iUia9eHwoe9
    6dDRzvDGrsoUvs1z5BdKvXby5usNQSWl6a0jrJ0KBatIY//9k8mwmDZ7iBEz4ag9
    ly1KXiwMQfzdSo5r/xX63sV/8P33AjLtDEZYTUDr/YVMyh7G5MocyIDOM89dXpX3
    qdRY1RvTK0+Tg+hshMZQyEXO8qui/FrXhCrPVwIDAQABAoIBAHl04A3KKjeZGGId
    ZLnAH/H+A6hTzP+65RSNi7cZWHfLmQ97DGmryQKkHh1Ipg2hR6wGYfqUGnbbYER9
    +SDynXaTbiel+FycdZfUxxxFJqKWs57wMKRTvTOQUcJyAvcBfs2vy8S8YUgFpLf3
    ZLJY3QVZJ8QOo6u9pSssy2I0RpteefjvLwXhDnLbICaBA7KOaSH+DMUFXnQ93RTk
    YwF9rn27A4cYcNzleazqc2AkOCgrDhWHBBVlULNo/z0pFIm8tqwpsX1Z/xWH14DY
    WJTT3BHWGfsLUwms7I/1YnUOIrtUdfHtW+34aet9Pqs40Qj8DS2XHalorIDDUfyX
    xSp+W6ECgYEA8q6SzNQ5NspxnO5dWjcX7xXtkJarAXlRczpYguhZcN0QJ/45bYzp
    V4RyrB3YLK9fY1NIVea2m2Cd9oM1vjHtyKb2Y7ZkQOvHKofw3MxIOvF5YZrvXTLP
    TN6QjvG69zl/OzSE/6locG6YEMiPnAsMW3bnIC3uou+YyHW/sHis/60CgYEA6XnT
    HcAzjKOtd5XDlXYgUqlhvgCDikmqOG4lxg5kIKKNajp/NX0KW8kYqOQBe/HeyS1x
    6rukvOFMPJhsKri4x7n0KFHIfGID0ynv4WdWzSqtO57wYSmTe4bv4J7u5jNLBxkZ
    8/aYjdt1eqFzbf32eV4FYJrAQHlLYZoY9jnn25MCgYEA3UC36jLabs+nQXI4fhWY
    pouRaa9T/SYEUk+xfrgjQzjoj+3BodVEsFu6yJz1B9hj2QSHAHo1pfcyTRtXFi4j
    IjrGjCYvxNixXl9OA5/jgonBJnHBJXE7elO36/sLgHZVPz8kuopTA55w2WxhMd0I
    ySLgmYAG/1n+K1TfDR8YaokCgYB87g8lkD8FNmAP6Tdqtna9RJ1kienZCWnoIChe
    Pj0dqV16RirjeDEexBBJ7xdMNzQ6+fJG5HlWCEg+9GCMy6M0XDBlkr1wsRHS4FHX
    jvBHgFqJ2JZPp2ufYajhzKmQzEmNVsUoYf9niNLn95RIeuh0MPc3phbRaRYI9+f7
    eSizuQKBgQCXe8j8d5enRKGDZIRi/5hlEcDgVaueByIdjvAQCWROYCoJrTpw53WJ
    bzZ9jbd/juNGwzNvNT2pkgzepXG3003DJqsz1sdC1koGtcNOLoGkCCZbXyacVWnp
    VS+CMnSpT0PIVOiafB9RCHQteVOA927L1lQR13sKoSgoapgW60SFJA==
    -----END RSA PRIVATE KEY-----"""


class DockerConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.used by the py.test suite."""

    # POSTGRESQL
    DB_USER = os.getenv("DATABASE_DOCKER_USERNAME")
    DB_PASSWORD = os.getenv("DATABASE_DOCKER_PASSWORD")
    DB_NAME = os.getenv("DATABASE_DOCKER_NAME")
    DB_HOST = os.getenv("DATABASE_DOCKER_HOST")
    DB_PORT = os.getenv("DATABASE_DOCKER_PORT", "5432")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"
    )

    print(f"SQLAlchemy URL (Docker): {SQLALCHEMY_DATABASE_URI}")


class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production Config."""

    SECRET_KEY = os.getenv("SECRET_KEY", None)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24)
        print("WARNING: SECRET_KEY being set as a one-shot", file=sys.stderr)

    TESTING = False
    DEBUG = False
