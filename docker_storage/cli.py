import sys
import os

from six.moves import urllib, shlex_quote

import click
from tabulate import tabulate
from docker import Client, tls

from docker_storage.driver import Storage, BoxNotFound


class BoxParam(click.ParamType):
    name = 'box-name'

    def convert(self, value, param, ctx):
        try:
            return ctx.obj.box(value)
        except BoxNotFound:
            self.fail('{} is not a valid box name'.format(value), param, ctx)


class QuotedCommand(click.ParamType):
    name = 'command'

    def convert(self, value, param, ctx):
        return shlex_quote(value)


def get_client(host, cert_path):
    tls_config = None
    url = urllib.parse.urlparse(host)
    if url.scheme == 'tcp':
        host = 'https://{}'.format(url.netloc)
        if cert_path:
            cert = os.path.join(cert_path, 'cert.pem')
            key = os.path.join(cert_path, 'key.pem')
            ca = os.path.join(cert_path, 'ca.pem')
            tls_config = tls.TLSConfig(
                client_cert=(cert, key),
                verify=ca,
                assert_hostname=False,
            )
    return Client(host, tls=tls_config, version='auto')


@click.group()
@click.option('--docker-host', envvar='DOCKER_HOST',
              default='unix://var/run/docker.sock')
@click.option('--cert-path', envvar='DOCKER_CERT_PATH')
@click.pass_context
def main(ctx, docker_host, cert_path):
    client = get_client(docker_host, cert_path)
    ctx.obj = Storage(client)


@main.group(invoke_without_command=True)
@click.pass_context
def box(ctx):
    storage = ctx.obj
    if ctx.invoked_subcommand is None:
        headers = ['Name', 'Path']
        table = [[box.name, box.shared_path] for box in storage.boxes()]
        click.echo(tabulate(table, headers, tablefmt='simple'))
        ctx.exit()


@box.command(name='create')
@click.option('-i', '--image', 'base_image')
@click.argument('name')
@click.argument('volume')
@click.pass_obj
def create_box(storage, name, volume, base_image):
    """
    Create a new box named `name` with an empty volume mounted at `volume`.
    """
    storage.create_box(name, volume, base_image=base_image)


@box.command(name='rm')
@click.argument('box', type=BoxParam())
def remove_box(box):
    box.delete()


@box.command(name='ls')
@click.argument('box', type=BoxParam())
def list_files(box):
    sys.stdout.writelines(box.run('/bin/ls -al'))


@box.command(name='exec')
@click.argument('box', type=BoxParam())
@click.argument('command', nargs=-1, type=QuotedCommand())
def execute_command(box, command):
    sys.stdout.writelines(box.run(command))


@box.command(name='cp')
@click.argument('src')
@click.argument('dst')
@click.pass_obj
def copy_files(storage, src, dst):
    """
    Copy files between `src` and `dst`.

    The source and destination arguments accept either a local path in the form
    <path> or a box path in the form <box-name>:<path>.
    """
    sys.stdout.writelines(storage.copy(src, dst))


@main.group(invoke_without_command=True)
@click.pass_context
def bundle(ctx):
    raise NotImplementedError('Bundles are not implemented yet')
