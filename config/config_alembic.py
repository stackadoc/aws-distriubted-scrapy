import os
import traceback

try:
    from dotenv import load_dotenv

    load_dotenv()
except (ModuleNotFoundError, ImportError):
    print("Unable to load_dotenv")
    print(traceback.format_exc())


def get_db_uri(domain: str, environment: str = None, is_superuser: bool = False) -> str:
    """
    Get the URI of a database
    :param domain: "DATA" or "REF"
    :param environment: "DEV" / "STAGE" / "PROD"
    :param is_superuser: Set True to get the super-user URI
    :return: The DB URI
    """

    environment = environment or os.environ.get("ENVIRONMENT", "STAGE")

    allowed_domains = {"DATA", "REF"}
    if domain not in allowed_domains:
        raise ValueError(f"Unknown domain {domain}. Allowed domains : {allowed_domains}.")

    allowed_environments = {"DEV", "STAGE", "PROD"}
    if environment not in allowed_environments:
        raise ValueError(
            f"Unknown environment {environment}. Allowed environment : {allowed_environments}."
        )

    db_names = {
        "DEV": "stackabot_data_dev_local",
        "STAGE": "stackabot_data_dev",
        "PROD": "stackabot_data_prod",
    }
    db_config = {
        "DEV": {
            "host": os.environ.get("DB_HOST_LOCAL"),
            "port": os.environ.get("DB_PORT_LOCAL"),
            "user": os.environ.get("DB_USER_LOCAL"),
            "password": os.environ.get("DB_PASSWORD_LOCAL"),
        },
        "STAGE": {
            "host": os.environ.get("DB_HOST"),
            "port": os.environ.get("DB_PORT"),
            "user": os.environ.get("DB_USER_SUPERUSER" if is_superuser else "DB_USER"),
            "password": os.environ.get("DB_PASSWORD_SUPERUSER" if is_superuser else "DB_PASSWORD"),
        },
        "PROD": {
            "host": os.environ.get("DB_HOST"),
            "port": os.environ.get("DB_PORT"),
            "user": os.environ.get("DB_USER_SUPERUSER" if is_superuser else "DB_USER"),
            "password": os.environ.get("DB_PASSWORD_SUPERUSER" if is_superuser else "DB_PASSWORD"),
        },
    }

    if domain == "REF":
        db_name = os.environ["REF_DB_NAME"]
    else:
        db_name = db_names.get(environment, db_names["STAGE"])

    db_config = db_config.get(environment, db_config["STAGE"])

    for key, value in db_config.items():
        if is_superuser and key in ["user", "password"] and value is None:
            continue
        if value is None:
            raise ValueError(f"{key} is not defined in the .env file.")

    db_host = db_config["host"]
    db_port = db_config["port"]
    db_user = db_config["user"]
    db_password = db_config["password"]

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATA_DB_URI = get_db_uri(
    domain="DATA", environment=os.environ.get("ENVIRONMENT"), is_superuser=False
)
