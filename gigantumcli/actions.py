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
from docker.errors import APIError, ImageNotFound

from gigantumcli.docker import DockerInterface


def install():
    """Method to install the Gigantum Image"""
    docker = DockerInterface()

    try:
        try:
            # Check to see if the image has already been pulled
            docker.client.images.get('gigantum/labmanager')
            print("** Application already installed. Run `gigantum update` instead.")
            sys.exit(1)
        except ImageNotFound:
            # Pull for the first time
            print("\nDownloading and installing the Gigantum Docker Image. Please wait...\n")
            image = docker.client.images.pull('gigantum/labmanager', 'latest')
    except APIError:
        print("ERROR: failed to pull image!")
        print("- Are you signed into DockerHub?")
        print("- Do you have access to gigantum/labmanager? If not, contact Gigantum.")
        print("    - Can test by going here: https://hub.docker.com/r/gigantum/labmanager/")
        print("    - If you see `404 Not Found`, request access\n")
        sys.exit(1)

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
    if not tag:
        tag = 'latest'

    try:
        # Get Changelog info for desired tag

        # Make sure user wants to pull

        # Pull
        print("\nDownloading and installing the Gigantum Docker Image. Please wait...\n")
        image = docker.client.images.pull('gigantum/labmanager', 'latest')

        # Set latest tag to what just got pulled down
    except APIError:
        print("ERROR: failed to pull image!")
        print("- Are you signed into DockerHub?")
        print("- Do you have access to gigantum/labmanager? If not, contact Gigantum.")
        print("    - Can test by going here: https://hub.docker.com/r/gigantum/labmanager/")
        print("    - If you see `404 Not Found`, request access\n")
        sys.exit(1)

    short_id = image.short_id.split(':')[1]
    print("\nSuccessfully pulled gigantum/labmanager:{}\n".format(short_id))

