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
import sys
from docker.errors import APIError, ImageNotFound, NotFound
import os
import webbrowser
import time

from gigantumcli.dockerinterface import DockerInterface
from gigantumcli.changelog import ChangeLog
from gigantumcli.utilities import ask_question, ExitCLI


def install():
    """Method to install the Gigantum Image"""
    docker = DockerInterface()

    try:
        try:
            # Check to see if the image has already been pulled
            docker.client.images.get('gigantum/labmanager')
            raise ExitCLI("** Application already installed. Run `gigantum update` instead.")

        except ImageNotFound:
            # Pull for the first time
            print("\nDownloading and installing the Gigantum Docker Image. Please wait...\n")
            image = docker.client.images.pull('gigantum/labmanager', 'latest')

    except APIError:
        msg = "ERROR: failed to pull image!"
        msg += "\n- Are you signed into DockerHub?"
        msg += "\n- Do you have access to gigantum/labmanager? If not, contact Gigantum."
        msg += "\n    - Can test by going here: https://hub.docker.com/r/gigantum/labmanager/"
        msg += "\n    - If you see `404 Not Found`, request access\n"
        raise ExitCLI(msg)

    short_id = image.short_id.split(':')[1]
    print("\nSuccessfully pulled gigantum/labmanager:{}\n".format(short_id))


def update(tag=None):
    """Method to update the existing image, warning about changes before accepting

    Args:
        tag(str): Tag to pull if you wish to override `latest`

    Returns:
        None
    """
    docker = DockerInterface()

    try:
        cl = ChangeLog()
        if not tag:
            # Trying to update to the latest version
            tag = 'latest'

            # Get id of current labmanager install
            try:
                current_image = docker.client.images.get("gigantum/labmanager:latest")
            except ImageNotFound:
                raise ExitCLI("Gigantum Image not yet installed. Run 'gigantum install' first.")
            short_id = current_image.short_id.split(':')[1]

            # Check if there is an update available
            if not cl.is_update_available(short_id):
                print("Latest version already installed.")
                sys.exit(0)

        # Get Changelog info for the latest or specified version
        try:
            print(cl.get_changelog(tag))
        except ValueError as err:
            raise ExitCLI(err)

        # Make sure user wants to pull
        if ask_question("Are you sure you want to update?"):
            # Pull
            print("\nDownloading and installing the Gigantum Docker Image. Please wait...\n")
            image = docker.client.images.pull('gigantum/labmanager', tag)

            # If pulling not truly latest, force to latest
            if tag != 'latest':
                print("Tagging explicit version {} with latest".format(tag))
                docker.client.api.tag('gigantum/labmanager:{}'.format(tag), 'gigantum/labmanager', 'latest')
        else:
            raise ExitCLI("Update cancelled")
    except APIError:
        msg = "ERROR: failed to pull image!"
        msg += "\n- Are you signed into DockerHub?"
        msg += "\n- Do you have access to gigantum/labmanager? If not, contact Gigantum."
        msg += "\n    - Can test by going here: https://hub.docker.com/r/gigantum/labmanager/"
        msg += "\n    - If you see `404 Not Found`, request access\n"
        raise ExitCLI(msg)

    short_id = image.short_id.split(':')[1]
    print("\nSuccessfully pulled gigantum/labmanager:{}\n".format(short_id))


def start(tag=None):
    """Method to start the application

    Args:
        tag(str): Tag to run, defaults to latest

    Returns:
        None 
    """
    # Check if Docker is running
    docker = DockerInterface()

    # Check if working dir exists
    working_dir = os.path.expanduser("~/gigantum")
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    if not tag:
        tag = "latest"

    # Check if application has been installed
    try:
        docker.client.images.get("gigantum/labmanager:latest")
    except ImageNotFound:
        raise ExitCLI("Application not found. Did you run `gigantum install` yet?")

    # Check to see if already running
    try:
        docker.client.containers.get("gigantum-labmanager")
        raise ExitCLI("Application already running on http://localhost:10000")
    except NotFound:
        pass

    # Start
    working_dir = os.path.join(os.path.expanduser("~"), "gigantum")
    port_mapping = {'10000/tcp': 10000,
                    '10001/tcp': 10001}

    # Make sure the container-container share volume exists
    if not docker.share_volume_exists():
        docker.create_share_volume()

    environment_mapping = {'HOST_WORK_DIR': working_dir}
    volume_mapping = {docker.share_vol_name: {'bind': '/mnt/share', 'mode': 'rw'}}

    # windows docker has several eccentricities
    #    no user ids
    #    //var for the socker mapping
    #    //C/a/b/ format for volume C:\\a\\b
    if sys.platform.startswith('win') or sys.platform.startswith('cygwin'):
        environment_mapping['WINDOWS_HOST'] = 1
        volume_mapping[docker.dockerize_volume_path(working_dir)] = {'bind': '/mnt/gigantum', 'mode': 'cached'}
        volume_mapping['//var/run/docker.sock'] = {'bind': '/var/run/docker.sock', 'mode': 'rw'}

    else:
        environment_mapping['LOCAL_USER_ID'] = os.getuid()
        volume_mapping[working_dir] = {'bind': '/mnt/gigantum', 'mode': 'cached'}
        volume_mapping['/var/run/docker.sock'] = {'bind': '/var/run/docker.sock', 'mode': 'rw'}

    docker.client.containers.run(image="gigantum/labmanager:{}".format(tag),
                                 detach=True,
                                 name="gigantum-labmanager",
                                 init=True,
                                 ports=port_mapping,
                                 volumes=volume_mapping,
                                 environment=environment_mapping)
    print("Starting...")
    time.sleep(5)
    webbrowser.open_new("http://localhost:10000")


def stop():
    """Method to stop all containers

    Returns:
        None
    """
    if ask_question("Stop all containers? MAKE SURE YOU HAVE SAVED YOUR WORK FIRST!"):
        docker = DockerInterface()

        for container in docker.client.containers.list():
            print('- stopping {}'.format(container.short_id))
            container.stop()

        docker.client.containers.prune()
    else:
        raise ExitCLI("Stop command cancelled")


def feedback():
    """Method to throw up a browser to provide feedback

    Returns:
        None
    """
    feedback_url = "https://app.craft.io/share/C3174F4B2305843009657781316"
    print("You can provide feedback here: {}".format(feedback_url))
    webbrowser.open_new(feedback_url)