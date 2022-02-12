import json

import typer
import requests


cli = typer.Typer()


@cli.command()
def read(root, skip, limit):
    data = requests.get(f'{root}/meets/?skip={skip}&limit={limit}')
    # print(data.content) нужно для разработки


@cli.command()
def read_by_id(root, id: int):
    data = requests.get(f'{root}/meets/{id}')
    # print(data.content) нужно для разработки


@cli.command()
def write(root, dict):
    write_thinks = json.loads(dict)
    data = requests.post(f'{root}/meets/',
                         json=write_thinks)
    # print(data.content) нужно для разработки


@cli.command()
def update_record(root, id: int, dict):
    update_thinks = json.loads(dict)
    data = requests.put(f'{root}/meets/?meet_id={id}',
                        json=update_thinks)
    # print(data.content) нужно для разработки


@cli.command()
def delete(root, id: int):
    data = requests.delete(f'{root}/meets/{id}')
    # print(data.content) нужно для разработки



if __name__ == '__main__':
    cli()
