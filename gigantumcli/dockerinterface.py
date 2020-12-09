import socket
import json
import os
import docker
import re
import subprocess
import platform
import requests
from docker.errors import NotFound

from gigantumcli.utilities import ask_question, ExitCLI


class DockerInterface:
    """Class to provide an interface to Docker"""

    def __init__(self):
        """Constructor"""
        # Get a docker client, or print help on how to install/run docker first
        if self.docker_is_installed():
            # Get client
            self.client = self._get_docker_client()

            if not self.docker_is_running():
                # Docker isn't running
                self._print_running_help()
                raise ExitCLI()
        else:
            # Docker isn't installed
            self._print_installing_help()
            raise ExitCLI()

        # Name of Docker volume used to share between containers
        self.share_vol_name = "labmanager_share_vol"

    @staticmethod
    def _print_running_help():
        """Print help for running docker, taking OS into account

        Returns:
            str
        """
        queried_system = platform.system()
        if queried_system == 'Linux':
            print_cmd = "Docker isn't running. Typically Docker runs as a service. Check that `dockerd` is running."
        elif queried_system == 'Darwin':
            print_cmd = "Docker isn't running. Start the Docker Desktop app and try again!"
        elif queried_system == 'Windows':
            print_cmd = "Docker isn't running. Start the Docker Desktop app and try again!"
        else:
            raise ValueError("Unsupported OS: {}".format(queried_system))

        print(print_cmd)

    @staticmethod
    def _print_installing_help():
        """Print help for installing docker, taking OS into account

        Returns:
            str
        """
        queried_system = platform.system()
        if queried_system == 'Linux':
            if ask_question("Docker isn't installed. Would you like to try to install it now?"):
                installer_path = os.path.expanduser('~/get-docker.sh')
                resp = requests.get('https://get.docker.com/')
                with open(installer_path, 'wb') as file_handle:
                    file_handle.write(resp.content)

                print_cmd = "An installer script has been downloaded to {}:\n".format(installer_path)
                print_cmd = "{}- Run `sudo sh ~/get-docker.sh`\n".format(print_cmd)
                print_cmd = "{}- Wait for installer to complete\n".format(print_cmd)
                print_cmd = "{}- Run `sudo usermod -aG docker <your-user-name>`\n".format(print_cmd)
                print_cmd = "{}  - This lets you run Docker commands not as root\n".format(print_cmd)
                print_cmd = "{}- Log out and then log back in\n".format(print_cmd)
            else:
                raise ExitCLI("You must install Docker to use the Gigantum application")

        elif queried_system == 'Darwin':
            print_cmd = "Docker isn't installed. Get the Docker for Mac app here: "
            print_cmd = "{}\n\n  https://docs.docker.com/docker-for-mac/install/  \n\n".format(print_cmd)
            print_cmd = "{}- Install the `Stable Channel` version.\n".format(print_cmd)
            print_cmd = "{}- You can change the amount of RAM and CPU allocated to Docker from".format(print_cmd)
            print_cmd = "{} the preferences menu that is available when clicking on the Docker logo".format(print_cmd)
            print_cmd = "{} in the OSX taskbar.\n".format(print_cmd)
            print_cmd = "{}- You don't need to leave Docker running all the time, but it must be".format(print_cmd)
            print_cmd = "{} running before you start the Gigantum application\n\n".format(print_cmd)

        elif queried_system == 'Windows':
            print_cmd = "Docker isn't installed!\n"
            print_cmd = "{}If you have 64bit Windows 10 Professional, Education, or Enterprise install " \
                        "Docker for Windows app here:".format(print_cmd)
            print_cmd = "{}\n\n  https://docs.docker.com/docker-for-windows/install/  \n\n".format(print_cmd)
            print_cmd = "{}- Install the `Stable Channel` version.\n".format(print_cmd)
            print_cmd = "{}- You can change the amount of RAM and CPU allocated to Docker from".format(print_cmd)
            print_cmd = "{} the preferences menu that is available when clicking on the Docker logo".format(print_cmd)
            print_cmd = "{} in the notification area.\n".format(print_cmd)
            print_cmd = "{}- You don't need to leave Docker running all the time, but it must be".format(print_cmd)
            print_cmd = "{} running before you start Gigantum\n\n".format(print_cmd)
        else:
            raise ValueError("Unsupported OS: {}".format(queried_system))

        print(print_cmd)

    @staticmethod
    def docker_is_installed():
        """Method to check if docker is installed"""
        queried_system = platform.system()
        if queried_system in {'Linux', 'Darwin'}:
            check_cmd = "which"
        elif queried_system == 'Windows':
            check_cmd = "where"
        else:
            raise ValueError("Unsupported OS: {}".format(queried_system))

        try:
            subprocess.check_output([check_cmd, 'docker'])
            return True
        except subprocess.CalledProcessError:
            return False

    def docker_is_running(self):
        """Method to check if docker is running"""
        try:
            if not self.client:
                self._get_docker_client()
            return self.client.ping()
        except requests.exceptions.ConnectionError as _:
            return False
        except docker.errors.APIError as _:
            return False
        except Exception as err:
            # Simple way to avoid importing pywintypes while catching the exception, which will only exist on windows
            # This error will be raised when the docker socket can't be open on windows because
            # docker isn't running
            if "pywintypes.error" in str(type(err)):
                return False
            else:
                # Some other error happened, so bubble it up
                raise

    @staticmethod
    def _get_docker_server_api_version():
        """Retrieve the Docker server API version. """

        socket_path = '/var/run/docker.sock'
        if not os.path.exists(socket_path):
            raise ValueError('No docker.sock on machine (is a Docker server installed?)')

        try:
            socket_connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            socket_connection.connect(socket_path)
            socket_connection.send(b'GET http://*/version HTTP/1.1\r\nHost: *\r\n\r\n')
        except ConnectionRefusedError:
            # Assume docker was running at some point to setup env vars, but not running now
            raise ValueError("Could not read from Docker socket")

        response_data = socket_connection.recv(4000)
        content_lines = response_data.decode().split('\r\n')

        version_dict = json.loads(content_lines[-1])
        if 'ApiVersion' not in version_dict.keys():
            raise ValueError('ApiVersion not in Docker version config data')
        else:
            return version_dict['ApiVersion']

    def dockerize_mount_path(self, host_path: str, image_name_with_tag: str) -> str:
        """Returns a path that can be mounted as a docker volume from the host

        Docker uses non-standard formats for windows mounts.
        Last we checked, this routine converts C:\a/gigantum -> /host_mnt/c/a/gigantum
        on windows and does nothing on posix systems.

        Args:
            host_path: a path on the host - Windows can use a mix of forward and back slashes
            image_name_with_tag: e.g., 'gigantum/labmanager:latest'

        Returns:
            path that can be handed to Docker inside another container for a volume mount
        """
        volume_mapping = {host_path: {'bind': '/mnt/gigantum', 'mode': 'ro'}}
        container = self.client.containers.run(image=image_name_with_tag,
                                               entrypoint='/usr/bin/tail',
                                               command='-f /dev/null',
                                               detach=True,
                                               init=True,
                                               volumes=volume_mapping,
                                               remove=True)
        rewritten_work_dir = container.attrs['Mounts'][0]['Source']
        container.stop()

        return rewritten_work_dir

    def _get_docker_client(self, check_server_version=True, fallback=True):
        """Return a docker client with proper version to match server API.

        Args:
            check_server_version(bool):
            fallback(bool):

        Returns:
            docker.DockerClient
        """

        if check_server_version:
            try:
                docker_server_api_version = self._get_docker_server_api_version()
                return docker.from_env(version=docker_server_api_version)
            except ValueError as e:
                if fallback:
                    return docker.from_env()
                else:
                    raise e
        else:
            return docker.from_env()

    def share_volume_exists(self):
        """Check if the container-container share volume exists

        Returns:
            bool
        """
        try:
            self.client.volumes.get(self.share_vol_name)
            return True
        except NotFound:
            return False

    def create_share_volume(self):
        """Create the share volume

        Returns:
            None
        """
        self.client.volumes.create(self.share_vol_name)

    def remove_share_volume(self):
        """Remove the share volume

        Returns:
            None
        """
        volume = self.client.volumes.get(self.share_vol_name)
        volume.remove()
