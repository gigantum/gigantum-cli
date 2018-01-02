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
from __future__ import print_function
from six.moves import input
import ctypes
import os


class ExitCLI(Exception):
    """Custom Exception when exit with 1 should happen"""
    pass


def ask_question(question):
    """Method to ask the user a yes/no question

    Args:
        question(str): A question to ask the user

    Returns:
        bool: True if yes, False if no
    """
    valid_response = {"yes": True, "y": True, "no": False, "n": False}

    while True:
        print("{} [y/n]: ".format(question), end="")
        choice = input().lower().strip()
        if choice in valid_response:
            return valid_response[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def is_running_as_admin():
    """Method to check if the python script is running as an administrator

    Returns:
        bool
    """
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()

    return is_admin
