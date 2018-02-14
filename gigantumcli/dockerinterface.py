# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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


class DockerInterface(object):
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
            print_cmd = "Docker isn't running. Typically docker runs at startup. Check that `dockerd` is running."
        elif queried_system == 'Darwin':
            print_cmd = "Docker isn't running. Start the Docker for Mac app and try again!"
        elif queried_system == 'Windows':
            print_cmd = "Docker isn't running. Start the Docker CE for Windows app and try again!"
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
            print_cmd = "{}- Be sure to sign-in to DockerHub by clicking on Sign-In\n".format(print_cmd)
            print_cmd = "{}- You don't need to leave Docker running all the time, but it must be".format(print_cmd)
            print_cmd = "{} running before you start the Gigantum application\n".format(print_cmd)

        elif queried_system == 'Windows':
            print_cmd = "Docker isn't installed!\n"
            print_cmd = "{}If you have 64bit Windows 10 Pro, install Docker for Windows app here:".format(print_cmd)
            print_cmd = "{}\n\n  https://docs.docker.com/docker-for-windows/install/  \n\n".format(print_cmd)
            print_cmd = "{}- Install the `Stable Channel` version.\n".format(print_cmd)
            print_cmd = "{}- You can change the amount of RAM and CPU allocated to Docker from".format(print_cmd)
            print_cmd = "{} the preferences menu that is available when clicking on the Docker logo".format(print_cmd)
            print_cmd = "{} in the notification area.\n".format(print_cmd)
            print_cmd = "{}- Be sure to sign-in to DockerHub by clicking on Sign-In\n".format(print_cmd)
            print_cmd = "{}- You don't need to leave Docker running all the time, but it must be".format(print_cmd)
            print_cmd = "{} running before you start the Gigantum application\n".format(print_cmd)
            print_cmd = "{}\nIf you have an old version of Windows, you can still use Docker Toolbox:".format(print_cmd)
            print_cmd = "{}\n\n  https://docs.docker.com/toolbox/overview/  \n\n".format(print_cmd)
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

    @staticmethod
    def dockerize_volume_path(volpath):
        """Returns a path that can be mounted as a docker volume on windows
            Docker uses non-standard formats for windows mounts.
            This routine converts C:\\a\\b -> /C/a/b on windows and does
            nothing on posix systems.

        Args:
            volpath(str): a python path

        Returns:
            str: path that can be handed to Docker for a volume mount
        """
        # Docker does not take ntpath formatted strings as volume mounts.
        # detect if it's a volume path and rewrite the string.
        if os.path.__name__ == 'ntpath':
            # for windows switch the slashes and then sub the drive letter
            return re.sub('(^[A-Z]):(.*$)', '/\g<1>\g<2>', volpath.replace('\\', '/'))
        else:
            return volpath

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
