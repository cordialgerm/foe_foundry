import os
from pprint import pprint
from typing import Tuple
from urllib.parse import urljoin

import click
import requests

# https://fastapiguide.pythonanywhere.com/


def _creds() -> Tuple[str, str]:
    username = os.environ["PYTHONANYWHERE_USERNAME"]
    token = os.environ["PYTHONANYWHERE_TOKEN"]
    return username, token


@click.command(name="check_account")
def check_account():
    username, token = _creds()
    response = requests.get(
        "https://www.pythonanywhere.com/api/v0/user/{username}/cpu/".format(username=username),
        headers={"Authorization": "Token {token}".format(token=token)},
    )
    if response.status_code == 200:
        print("CPU quota info:")
        print(response.content)
    else:
        print(
            "Got unexpected status code {}: {!r}".format(response.status_code, response.content)
        )


@click.command(name="setup_website")
def setup_website():
    username, token = _creds()
    pythonanywhere_host = "www.pythonanywhere.com"  # or "eu.pythonanywhere.com" if your account is hosted on our EU servers
    pythonanywhere_domain = "pythonanywhere.com"  # or "eu.pythonanywhere.com"
    headers = {"Authorization": f"Token {token}"}

    # make sure you don't use this domain already!
    domain_name = f"{username}.{pythonanywhere_domain}"

    api_base = f"https://{pythonanywhere_host}/api/v1/user/{username}/"

    # delete existing site
    print("deleting existing site...")
    response = requests.delete(urljoin(api_base, f"websites/{domain_name}/"), headers=headers)
    print(response)

    command = (
        f"/home/{username}/.virtualenvs/foe_foundry/bin/uvicorn "
        "--uds $DOMAIN_SOCKET "
        "foe_foundry.foe_foundry.app:app"
    )

    response = requests.post(
        urljoin(api_base, "websites/"),
        headers=headers,
        json={"domain_name": domain_name, "enabled": True, "webapp": {"command": command}},
    )
    pprint(response.json())


@click.group()
def cli():
    pass


cli.add_command(setup_website)
cli.add_command(check_account)

if __name__ == "__main__":
    cli()
