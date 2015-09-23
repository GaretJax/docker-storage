import os

from docker.utils import create_host_config
from docker.errors import APIError


class BoxNotFound(Exception):
    pass


class Storage(object):
    BASE_IMAGE = 'busybox:latest'

    def __init__(self, client):
        self.client = client

    def create_box(self, name, volume, base_image=None):
        if base_image is None:
            base_image = self.BASE_IMAGE
        container = self.client.create_container(
            base_image,
            '/bin/true',
            name=name,
            network_disabled=True,
            volumes=[volume],
            entrypoint=['chroot', volume],
            labels=['data-only'],
        )
        self.client.start(container=container['Id'])
        return Box(self, container)

    def box(self, name):
        try:
            container = self.client.inspect_container(container=name)
        except APIError as e:
            if e.response.status_code == 404:
                is_box = False
            else:
                raise
        else:
            is_box = all([
                'data-only' in container['Config']['Labels'],
                not container['State']['Running'],
            ])

        if not is_box:
            raise BoxNotFound('box {} was not found'.format(name))

        return Box(self, container)

    def copy(self, src, dst):
        def parse(path):
            if ':' in path:
                box_name, path = path.split(':', 1)
                return BoxLocation(self.box(box_name), path)
            else:
                return LocalLocation(self.client, path)

        src = parse(src)
        dst = parse(dst)

        container = self.client.create_container(
            image=self.BASE_IMAGE,
            host_config=create_host_config(binds={
                src.get_mountpoint(): {
                    'bind': '/mnt/src',
                    'ro': True,
                },
                dst.get_mountpoint(): {
                    'bind': '/mnt/dst',
                    'ro': False,
                }
            }),
            command=[
                'cp', '-afv',
                os.path.join('/mnt/src', src.get_path()),
                os.path.join('/mnt/dst', dst.get_path()),
            ],
        )
        self.client.start(container=container['Id'])
        return self.client.logs(container=container['Id'], stream=True)

    def iter_boxes(self):
        containers = self.client.containers(
            all=True,
            filters={
                'label': 'data-only',
                'status': 'exited',
            },
        )
        for container in containers:
            yield Box(self, self.client.inspect_container(container['Id']))

    def boxes(self):
        return list(self.iter_boxes())


class LocalLocation(object):
    def __init__(self, client, path):
        self.client = client
        self.path = path

    def get_mountpoint(self):
        return os.getcwd()

    def get_path(self):
        return self.path


class BoxLocation(object):
    def __init__(self, box, path):
        self.box = box
        self.path = path

    def get_mountpoint(self):
        for mount in self.box.container['Mounts']:
            if mount['Destination'] == self.box.shared_path:
                return mount['Source']

    def get_path(self):
        return self.path


class Box(object):
    def __init__(self, storage, container):
        self.storage = storage
        self.container = container

    def delete(self):
        self.storage.client.remove_container(container=self.id, v=True)

    @property
    def id(self):
        return self.container['Id']

    @property
    def name(self):
        return self.container['Name'][1:]

    @property
    def shared_path(self):
        return self.container['Config']['Volumes'].keys()[0]

    def run(self, cmd):
        container = self.storage.client.create_container(
            image=self.storage.BASE_IMAGE,
            command=cmd,
            working_dir=self.shared_path,
        )
        self.storage.client.start(
            container=container['Id'],
            volumes_from=[self.id],
        )
        return self.storage.client.logs(container=container['Id'], stream=True)
