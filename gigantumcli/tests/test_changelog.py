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
import pytest
from pkg_resources import resource_filename
import os
import json
from mock import patch

from gigantumcli.changelog import ChangeLog


@pytest.fixture(scope='class')
def fixture_changelog_data():
    """Fixture to create a Build instance with a test image name that does not exist and cleanup after"""
    with open(os.path.join(resource_filename('gigantumcli', 'tests'), 'changelog_test_data.json'), 'rt') as df:
        data = json.load(df)

    with patch.object(ChangeLog, '_load_data', lambda self: data):
        yield data


class TestChangelog(object):
    def test_constructor(self, fixture_changelog_data):
        """Test creating an object, mocking the query for actual data"""
        cl = ChangeLog()
        assert cl.data == fixture_changelog_data

    def test_is_update_available(self, fixture_changelog_data):
        """Test checking if an update is available"""
        cl = ChangeLog()
        assert cl.is_update_available('edfacdff') is True
        assert cl.is_update_available('fb4cced9') is False

    def test_get_changelog_no_data(self, fixture_changelog_data):
        """Test getting a changelog when no data available"""
        cl = ChangeLog()
        cl.data = None
        cl_str = cl.get_changelog()
        assert cl_str is None

    def test_get_changelog_bad_tag(self, fixture_changelog_data):
        """Test getting a changelog with a bad tag"""
        cl = ChangeLog()
        with pytest.raises(ValueError):
            cl.get_changelog('acdfacdf')

    def test_get_changelog(self, fixture_changelog_data):
        """Test getting a changelog string"""
        cl = ChangeLog()
        cl_str = cl.get_changelog()
        correct_str = """Version: fb4cced9
Release Date: 2017-10-30
Note: 
  - notification 1

Added: 
  - Added something

Changed: 
  - Changed something

Deprecated: 
  - Deprecated something

Removed: 
  - Removed something

Fixed: 
  - Added something 1
  - Added something 2
"""

        assert cl_str == correct_str
