import pytest
import mock
import shutil
import os
from docker.errors import ImageNotFound
import getpass

from gigantumcli.utilities import ExitCLI
from gigantumcli.dockerinterface import DockerInterface
from gigantumcli.actions import start, install


@pytest.fixture()
def fixture_remove_busybox():
    """Fixture start fake project and client containerss"""
    docker = DockerInterface()
    try:
        # Check to see if the image has already been pulled
        img = docker.client.images.get('busybox')
        docker.client.images.remove(img.id, force=True)
    except ImageNotFound:
        pass


@pytest.fixture()
def fixture_temp_work_dir():
    """Fixture create a temporary working directory"""
    temp_dir = os.path.join('/tmp', 'testing-working-dir')
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)
    yield temp_dir

    # Remove temp dir
    shutil.rmtree(temp_dir)

    # Stop and remove Client container
    docker = DockerInterface()
    for container in docker.client.containers.list(all=True):
        if container.name == "gigantum.labmanager":
            container.stop()
            container.remove()


def mock_api_check(launch_browser, timeout):
    return launch_browser


def mock_is_running_as_admin():
    return True


class TestActions(object):
    def test_is_running_as_admin(self):
        from gigantumcli.utilities import is_running_as_admin
        assert is_running_as_admin() is False

    def test_install(self, fixture_remove_busybox):
        docker = DockerInterface()

        # image should exist not exist before install
        try:
            # Check to see if the image has already been pulled
            docker.client.images.get('busybox')
            assert "Image should not exist"
        except ImageNotFound:
            pass

        install('busybox')

        # image should exist after install
        docker = DockerInterface()
        docker.client.images.get('busybox')

        # Calling again should exit with a message since already installed
        with pytest.raises(ExitCLI):
            install('busybox')

    @pytest.mark.skipif(getpass.getuser() == 'circleci', reason="Cannot run this test in CircleCI, needs access "
                                                                "to docker machine file system")
    def test_start_with_install_non_default_work_dir(self, fixture_temp_work_dir):
        with mock.patch('gigantumcli.actions._check_for_api', mock_api_check):
            start('gigantum/labmanager', 60, working_dir=fixture_temp_work_dir, accept_confirmation=True)

        docker = DockerInterface()

        is_running = False
        for container in docker.client.containers.list():
            if container.name in 'gigantum.labmanager':
                is_running = True
                break

        assert is_running is True
