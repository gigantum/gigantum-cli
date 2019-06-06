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
import platform
from docker.errors import APIError, ImageNotFound, NotFound
import os
import webbrowser
import time
import requests
import uuid

from gigantumcli.dockerinterface import DockerInterface
from gigantumcli.changelog import ChangeLog
from gigantumcli.utilities import ask_question, ExitCLI, is_running_as_admin, get_nvidia_driver_version


def _cleanup_containers() -> None:
    """Method to clean up gigantum managed containers, stopping if needed.

    Note: this method is the only place removal of containers should occur

    Returns:
        None
    """
    docker = DockerInterface()

    # Stop any project containers
    for container in docker.client.containers.list(all=True):
        if "gmlb-" in container.name:
            _, user, owner, project_name = container.name.split('-', 3)
            print('- Cleaning up container for Project: {}'.format(project_name))
            container.stop()
            container.remove()

    # Stop app container
    try:
        app_container = docker.client.containers.get("gigantum.labmanager-edge")

        print('- Cleaning up Gigantum Client container')
        app_container.stop()
        app_container.remove()
    except NotFound:
        pass

    try:
        app_container = docker.client.containers.get("gigantum.labmanager")

        print('- Cleaning up Gigantum Client container')
        app_container.stop()
        app_container.remove()
    except NotFound:
        pass


def install(image_name):
    """Method to install the Gigantum Image

    Args:
        image_name(str): Image name, including repository and namespace (e.g. gigantum/labmanager)


    """
    # Make sure user is not root
    if is_running_as_admin():
        raise ExitCLI("Do not run `gigantum install` as root.")

    docker = DockerInterface()

    try:
        try:
            # Check to see if the image has already been pulled
            docker.client.images.get(image_name)
            raise ExitCLI("** Gigantum Client image already installed. Run `gigantum update` instead.")

        except ImageNotFound:
            # Pull for the first time
            print("\nDownloading and installing the Gigantum Client Docker Image. Please wait...\n")
            image = docker.client.images.pull(image_name, 'latest')

    except APIError:
        msg = "ERROR: failed to pull image!"
        msg += "\n- Are you signed into DockerHub?"
        msg += "\n- Do you have access to {}? If not, contact Gigantum.".format(image_name)
        msg += "\n    - Can test by going here: https://hub.docker.com/r/gigantum/labmanager/"
        msg += "\n    - If you see `404 Not Found`, request access from Gigantum\n"
        raise ExitCLI(msg)

    short_id = image.short_id.split(':')[1]
    print("\nSuccessfully pulled {}:{}\n".format(image_name, short_id))


def update(image_name, tag=None, accept_confirmation=False):
    """Method to update the existing image, warning about changes before accepting

    Args:
        image_name(str): Image name, including repository and namespace (e.g. gigantum/labmanager)
        tag(str): Tag to pull if you wish to override `latest`
        accept_confirmation(bool): Optional Flag indicating if you should skip the confirmation and auto-accept

    Returns:
        None
    """
    # Make sure user is not root
    if is_running_as_admin():
        raise ExitCLI("Do not run `gigantum update` as root.")

    docker = DockerInterface()

    try:
        cl = ChangeLog()
        if "edge" not in image_name:
            # Normal install, so do checks
            if not tag:
                # Trying to update to the latest version
                tag = 'latest'

                # Get id of current labmanager install
                try:
                    current_image = docker.client.images.get("{}:latest".format(image_name))
                except ImageNotFound:
                    raise ExitCLI("Gigantum Client image not yet installed. Run 'gigantum install' first.")
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
        else:
            # Edge build, set tag if needed
            if not tag:
                # Trying to update to the latest version
                tag = 'latest'

        # Make sure user wants to pull
        if ask_question("Are you sure you want to update?", accept_confirmation):
            # Pull
            print("\nDownloading and installing the Gigantum Client Docker Image. Please wait...\n")
            image = docker.client.images.pull(image_name, tag)

            # If pulling not truly latest, force to latest
            if tag != 'latest':
                print("Tagging explicit version {} with latest".format(tag))
                docker.client.api.tag('{}:{}'.format(tag, image_name), image_name, 'latest')
        else:
            raise ExitCLI("Update cancelled")
    except APIError:
        msg = "ERROR: failed to pull image!"
        msg += "\n- Are you signed into DockerHub?"
        msg += "\n- Do you have access to {}? If not, contact Gigantum.".format(image_name)
        msg += "\n    - Can test by going here: https://hub.docker.com/r/gigantum/labmanager/"
        msg += "\n    - If you see `404 Not Found`, request access\n"
        raise ExitCLI(msg)

    short_id = image.short_id.split(':')[1]
    print("\nSuccessfully pulled {}:{}\n".format(image_name, short_id))


def _check_for_api(launch_browser=False, timeout=5):
    """Check for the API to be live for up to `timeout` seconds, then optionally launch a browser window

    Args:
        launch_browser(bool): flag indicating if the browser should be launched on success == True
        timeout(int): Number of seconds to wait for the API before returning
    Returns:
        bool: flag indicating if the API is ready
    """
    time.sleep(1)
    success = False
    for _ in range(timeout):
        try:
            resp = requests.get("http://localhost:10000/api/ping?v={}".format(uuid.uuid4().hex))

            if resp.status_code == 200:
                success = True
                break
        except requests.exceptions.ConnectionError:
            # allow connection errors, which mean the API isn't up yet.
            pass

        # Sleep for 1 sec and increment counter
        time.sleep(1)

    if success is True and launch_browser is True:
        time.sleep(1)
        # If here, things look OK. Start browser
        webbrowser.open_new("http://localhost:10000")

    return success


def start(image_name, timeout, tag=None, working_dir="~/gigantum", accept_confirmation=False):
    """Method to start the application

    Args:
        image_name(str): Image name, including repository and namespace (e.g. gigantum/labmanager)
        timeout(int): Number of seconds to wait for API to come up
        tag(str): Tag to run, defaults to latest
        working_dir(str): Location to mount as the Gigantum working directory
        accept_confirmation(bool): Optional Flag indicating if you should skip the confirmation and auto-accept

    Returns:
        None
    """
    # Make sure user is not root
    if is_running_as_admin():
        raise ExitCLI("Do not run `gigantum start` as root.")

    print("Verifying Docker is available...")
    # Check if Docker is running
    docker = DockerInterface()

    if not tag:
        # Trying to update to the latest version
        tag = 'latest'

    # Check if working dir exists
    working_dir = os.path.expanduser(working_dir)
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    # Check if application has been installed
    try:
        docker.client.images.get("{}:{}".format(image_name, tag))
    except ImageNotFound:
        if ask_question("The Gigantum Client Docker image not found. Would you like to install it now?",
                        accept_confirmation):
            install(image_name)
        else:
            raise ExitCLI("Downloading the Gigantum Client Docker image is required to start the Client. "
                          "Please run `gigantum install`.")

    # Check to see if already running
    try:
        if _check_for_api(launch_browser=False, timeout=1):
            print("Client already running on http://localhost:10000")
            _check_for_api(launch_browser=True)
            raise ExitCLI("If page does not load, restart by running `gigantum stop` and then `gigantum start` again")

        # remove any lingering gigantum managed containers
        _cleanup_containers()

    except NotFound:
        # If here, the API isn't running and an older container isn't lingering, so just move along.
        pass

    # Start
    port_mapping = {'10000/tcp': 10000}

    # Make sure the container-container share volume exists
    if not docker.share_volume_exists():
        docker.create_share_volume()

    volume_mapping = {docker.share_vol_name: {'bind': '/mnt/share', 'mode': 'rw'}}

    if platform.system() == 'Windows':
        # windows docker has the following eccentricities
        # no user ids, WINDOWS_HOST env var, /C/a/b/ format for volume C:\\a\\b
        environment_mapping = {'HOST_WORK_DIR': docker.dockerize_volume_path(working_dir),
                               'WINDOWS_HOST': 1}
        volume_mapping[docker.dockerize_volume_path(working_dir)] = {'bind': '/mnt/gigantum', 'mode': 'rw'}

    elif platform.system() == 'Darwin':
        # For macOS, use the cached mode for improved performance
        environment_mapping = {'HOST_WORK_DIR': working_dir,
                               'LOCAL_USER_ID':  os.getuid()}
        volume_mapping[working_dir] = {'bind': '/mnt/gigantum', 'mode': 'cached'}
    else:
        # For anything else, just use default mode.
        environment_mapping = {'HOST_WORK_DIR': working_dir,
                               'LOCAL_USER_ID':  os.getuid(),
                               'NVIDIA_DRIVER_VERSION': get_nvidia_driver_version()}
        volume_mapping[working_dir] = {'bind': '/mnt/gigantum', 'mode': 'rw'}

    volume_mapping['/var/run/docker.sock'] = {'bind': '/var/run/docker.sock', 'mode': 'rw'}

    container = docker.client.containers.run(image="{}:{}".format(image_name, tag),
                                             detach=True,
                                             name=image_name.replace("/", "."),
                                             init=True,
                                             ports=port_mapping,
                                             volumes=volume_mapping,
                                             environment=environment_mapping)
    print("Starting, please wait...")
    time.sleep(1)

    # Make sure volumes have mounted properly, by checking for the log file for up to 60 seconds
    success = False
    for _ in range(60):
        if os.path.exists(os.path.join(working_dir, '.labmanager', 'logs', 'labmanager.log')):
            success = True
            break

        # Sleep for 1 sec and increment counter
        time.sleep(1)

    if not success:
        msg = "\n\nWorking directory failed to mount! Have you granted Docker access to your user directory?"
        msg = msg + " \nIn both Docker for Mac and Docker for Windows this should be shared by default, but may require"
        msg = msg + " a confirmation from the user."
        msg = msg + "\n\nRun `gigantum stop`, verify your OS and Docker versions are supported, the allowed Docker"
        msg = msg + " volume share locations include `{}`, and try again.".format(working_dir)
        msg = msg + "\n\nIf this problem persists, contact support."

        # Stop and remove the container
        container.stop()
        container.remove()

        raise ExitCLI(msg)

    # Wait for API to be live before opening the user's browser
    if not _check_for_api(launch_browser=True, timeout=timeout):
        msg = "\n\nTimed out waiting for Gigantum Client web API! Try restarting Docker and then start again." + \
                "\nOr, increase time-out with --wait option (default is 60 seconds)."

        # Stop and remove the container
        container.stop()
        container.remove()

        raise ExitCLI(msg)


def stop(accept_confirmation=False):
    """Method to stop all containers
    Args:
        accept_confirmation(bool): Optional Flag indicating if you should skip the confirmation and auto-accept

    Returns:
        None
    """
    if ask_question("Stop all Gigantum managed containers? MAKE SURE YOU HAVE SAVED YOUR WORK FIRST!",
                    accept_confirmation):
        # remove any lingering gigantum managed containers
        _cleanup_containers()
    else:
        raise ExitCLI("Stop command cancelled")


def feedback():
    """Method to throw up a browser to provide feedback

    Returns:
        None
    """
    feedback_url = "https://feedback.gigantum.com"
    print("You can provide feedback here: {}".format(feedback_url))
    webbrowser.open_new(feedback_url)
