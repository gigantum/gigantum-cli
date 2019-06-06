import pytest
from pkg_resources import resource_filename
import os
import json
from mock import patch

from gigantumcli.dockerinterface import DockerInterface
from gigantumcli.actions import _cleanup_containers
from gigantumcli.actions import stop


@pytest.fixture()
def fixture_create_dummy_containers():
    """Fixture start fake project and client containerss"""
    docker = DockerInterface()
    docker.client.images.pull("busybox", 'latest')

    names = ['gigantum.labmanager-edge', 'gigantum.labmanager', 'gmlb-test-test-test-project',
             'gmlb-test-test-test-project-2', 'rando']

    containers = list()
    for name in names:
        containers.append(docker.client.containers.run(image="busybox:latest",
                                                       detach=True,
                                                       name=name,
                                                       init=True,
                                                       command="tail -f /dev/null"))
    yield

    # make sure all containers are moved in case of failures
    for container in docker.client.containers.list(all=True):
        if container.name in names:
            container.stop()
            container.remove()


class TestContainerCleanup(object):
    def test_cleanup_containers_running(self, fixture_create_dummy_containers):
        docker = DockerInterface()
        _cleanup_containers()

        running_containers = docker.client.containers.list()
        assert len(running_containers) == 1
        assert running_containers[0].name == 'rando'

    def test_cleanup_containers_stopped(self, fixture_create_dummy_containers):
        docker = DockerInterface()

        # Stop some containers, simulating what happens when docker is kill while running
        c1 = docker.client.containers.get('gmlb-test-test-test-project')
        c1.stop()
        c2 = docker.client.containers.get('gigantum.labmanager')
        c2.stop()

        running_containers = docker.client.containers.list()
        running_containers = [x.name for x in running_containers]
        assert len(running_containers) == 3
        assert 'rando' in running_containers
        assert 'gmlb-test-test-test-project-2' in running_containers
        assert 'gigantum.labmanager-edge' in running_containers

        all_containers = docker.client.containers.list(all=True)
        all_containers = [x.name for x in all_containers]
        assert len(all_containers) >= 5
        assert 'rando' in all_containers
        assert 'gmlb-test-test-test-project-2' in all_containers
        assert 'gmlb-test-test-test-project' in all_containers
        assert 'gigantum.labmanager-edge' in all_containers
        assert 'gigantum.labmanager' in all_containers

        _cleanup_containers()

        running_containers = docker.client.containers.list()
        running_containers = [x.name for x in running_containers]
        assert len(running_containers) == 1
        assert running_containers[0] == 'rando'

        all_containers = docker.client.containers.list(all=True)
        all_containers = [x.name for x in all_containers]
        assert len(all_containers) >= 1
        assert 'rando' in all_containers
        assert 'gmlb-test-test-test-project-2' not in all_containers
        assert 'gmlb-test-test-test-project' not in all_containers
        assert 'gigantum.labmanager-edge' not in all_containers
        assert 'gigantum.labmanager' not in all_containers

    def test_stop_auto_confirm(self, fixture_create_dummy_containers):
        docker = DockerInterface()
        stop(True)

        running_containers = docker.client.containers.list()
        assert len(running_containers) == 1
        assert running_containers[0].name == 'rando'
