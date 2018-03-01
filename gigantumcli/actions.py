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

from gigantumcli.dockerinterface import DockerInterface
from gigantumcli.changelog import ChangeLog
from gigantumcli.utilities import ask_question, ExitCLI, is_running_as_admin


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
            raise ExitCLI("** Application already installed. Run `gigantum update` instead.")

        except ImageNotFound:
            # Pull for the first time
            print("\nDownloading and installing the Gigantum Docker Image. Please wait...\n")
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


def update(image_name, tag=None):
    """Method to update the existing image, warning about changes before accepting

    Args:
        image_name(str): Image name, including repository and namespace (e.g. gigantum/labmanager)
        tag(str): Tag to pull if you wish to override `latest`

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
        else:
            # Edge build, set tag if needed
            if not tag:
                # Trying to update to the latest version
                tag = 'latest'

        # Make sure user wants to pull
        if ask_question("Are you sure you want to update?"):
            # Pull
            print("\nDownloading and installing the Gigantum Docker Image. Please wait...\n")
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
    print("\nSuccessfully pulled {}:{}\n".format(short_id, image_name))


def _check_for_api(launch_browser=False, timeout=5):
    """Helper method to check for the API to be live for up to 15 seconds and then optionally launch a browser window

    Args:
        launch_browser(bool): flag indicating if the browser should be launched on success == True
        timeout(int): Number of seconds to wait for the API before returning
    Returns:
        bool: flag indicating if the API is ready
    """
    success = False
    for _ in range(timeout * 2):
        try:
            resp = requests.get("http://localhost:10001/ping")

            if resp.status_code == 200:
                success = True
                break
        except requests.exceptions.ConnectionError:
            # allow connection errors, which mean the API isn't up yet.
            pass

        # Sleep for 1 sec and increment counter
        time.sleep(.5)

    if success is True and launch_browser is True:
        # If here, things look OK. Start browser
        webbrowser.open_new("http://localhost:10000")

    return success


def start(image_name, tag=None):
    """Method to start the application

    Args:
        tag(str): Tag to run, defaults to latest
        image_name(str): Image name, including repository and namespace (e.g. gigantum/labmanager)

    Returns:
        None 
    """
    print("Verifying Docker is available...")
    # Check if Docker is running
    docker = DockerInterface()

    if not tag:
        # Trying to update to the latest version
        tag = 'latest'

    # Make sure user is not root
    if is_running_as_admin():
        raise ExitCLI("Do not run `gigantum start` as root.")

    # Check if working dir exists
    working_dir = os.path.join(os.path.expanduser("~"), "gigantum")
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    # Check if application has been installed
    try:
        docker.client.images.get("{}:{}".format(image_name, tag))
    except ImageNotFound:
        raise ExitCLI("Application not found. Did you run `gigantum install` yet?")

    # Check to see if already running
    try:
        if _check_for_api(launch_browser=False, timeout=1):
            print("Application already running on http://localhost:10000")
            _check_for_api(launch_browser=True)
            raise ExitCLI("If app does not load in your browser, run `gigantum stop` and then `gigantum start`")

        # Check to see if the container already exists
        old_container = docker.client.containers.get(image_name.replace("/", "-"))

        # if here it does, so for now remove the old container so you can relaunch
        old_container.stop()
        old_container.remove()

    except NotFound:
        # If here, the API isn't running and an older container isn't lingering, so just move along.
        pass

    # Start
    port_mapping = {'10000/tcp': 10000,
                    '10001/tcp': 10001}

    # Make sure the container-container share volume exists
    if not docker.share_volume_exists():
        docker.create_share_volume()

    volume_mapping = {docker.share_vol_name: {'bind': '/mnt/share', 'mode': 'rw'}}

    # windows docker has the following eccentricities
    #    no user ids
    #    /C/a/b/ format for volume C:\\a\\b
    if platform.system() == 'Windows':
        environment_mapping = {'HOST_WORK_DIR': docker.dockerize_volume_path(working_dir),
                               'WINDOWS_HOST': 1}
        volume_mapping[docker.dockerize_volume_path(working_dir)] = {'bind': '/mnt/gigantum', 'mode': 'cached'}

    else:
        environment_mapping = {'HOST_WORK_DIR': working_dir,
                               'LOCAL_USER_ID':  os.getuid()}
        volume_mapping[working_dir] = {'bind': '/mnt/gigantum', 'mode': 'cached'}

    volume_mapping['/var/run/docker.sock'] = {'bind': '/var/run/docker.sock', 'mode': 'rw'}

    container = docker.client.containers.run(image="{}:{}".format(image_name, tag),
                                             detach=True,
                                             name=image_name.replace("/", "-"),
                                             init=True,
                                             ports=port_mapping,
                                             volumes=volume_mapping,
                                             environment=environment_mapping)
    print("Starting, please wait...")
    time.sleep(1)

    # Make sure volumes have mounted properly, by checking for the log file for up to 30 seconds
    success = False
    for _ in range(30):
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
    if not _check_for_api(launch_browser=True):
        msg = "\n\nGigantum client failed to start! Try restarting Docker and then start again."

        # Stop and remove the container
        container.stop()
        container.remove()

        raise ExitCLI(msg)


def stop():
    """Method to stop all containers

    Returns:
        None
    """
    if ask_question("Stop all Gigantum managed containers? MAKE SURE YOU HAVE SAVED YOUR WORK FIRST!"):
        docker = DockerInterface()

        # Stop any labbook containers
        for container in docker.client.containers.list():
            if "gmlb-" in container.name:
                _, user, owner, labbook_name = container.name.split('-', 3)
                print('- Stopping container for LabBook: {}'.format(labbook_name))
                container.stop()
                container.remove()

        # Stop app container
        try:
            app_container = docker.client.containers.get("gigantum-labmanager")

            print('- Stopping Gigantum app container')
            app_container.stop()
            app_container.remove()
        except NotFound:
            pass
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
