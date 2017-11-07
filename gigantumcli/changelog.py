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
import requests
import json


class ChangeLog(object):
    """Class to provide an interface to the posted ChangeLog information"""

    def __init__(self):
        """Constructor"""
        # Load data
        self._change_log_url = "https://s3.amazonaws.com/io.gigantum.changelog/changelog.json"
        self.data = self._load_data()

    def _load_data(self):
        """Load the changelog data file from remote source

        Returns:
            dict
        """
        data = None
        try:
            response = requests.get(self._change_log_url)
            data = response.json()
        finally:
            return data

    def is_update_available(self, tag):
        """Method to check if an update is available using the changelog as a history

        Args:
            tag(str): The 8-char short hash tag for the CURRENT image in used

        Returns:
            bool
        """
        latest_hash = self.data['latest']['id']
        return latest_hash != tag

    def get_changelog(self, tag="latest"):
        """Method to print the changelog data

        Args:
            tag(str): Version of the changelog to grab

        Returns:
            str
        """
        if not self.data:
            # No changelog data was available...probably no internet connection
            return None

        if tag not in self.data:
            raise ValueError("Tag {} not available".format(tag))

        data = self.data[tag]
        msg = "Version: {}\n".format(data['id'])
        msg = "{}Release Date: {}\n".format(msg, data['date'])
        msg = "{}Note: \n".format(msg)

        # Show notices
        if 'messages' in data:
            for note in data['messages']:
                msg = "{}  - {}\n".format(msg, note)

        # Show changes
        for change_key in data['changes']:
            msg = "{}\n{}: \n".format(msg, change_key)
            for change_str in data['changes'][change_key]:
                msg = "{}  - {}\n".format(msg, change_str)

        return msg

