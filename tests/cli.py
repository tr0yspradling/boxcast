# -*- coding: utf-8 -*-

"""Console script for boxcast_python_sdk."""
import sys
import click
from boxcast import BoxCastClient


@click.command()
@click.option('--client_id')
@click.option('--client_secret')
def main(client_id, client_secret):
    """Console script for boxcast_python_sdk."""
    client = BoxCastClient(client_id, client_secret)
    account = client.get_account()
    print(account)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
