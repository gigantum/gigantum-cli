from urllib.parse import urljoin, urlparse
import os
import json
import glob
import requests
from gigantumcli.utilities import ExitCLI, ask_question
import urllib3


class ServerConfig:
    def __init__(self, working_dir):
        self.working_dir = os.path.expanduser(working_dir)
        self.servers_dir = os.path.join(self.working_dir, '.labmanager', 'servers')

    @staticmethod
    def _fetch_wellknown_data(url):
        succeed = False
        data = None
        verify = True
        try:
            response = requests.get(url, verify=verify)
            if response.status_code == 200:
                try:
                    # If a 200, make sure you get valid JSON back in case you were routed to some other 200 response.
                    data = response.json()
                    succeed = True
                except json.JSONDecodeError:
                    pass
        except requests.exceptions.SSLError:
            print("WARNING: SSL verification failed while trying to configure from server located at {}.\nIf this"
                  " is expected, it may be safe to proceed (e.g. a server created with a self-signed TLS "
                  "certificate).".format(url))
            if ask_question("Do you want to continue?"):
                # Try again with SSL verification disabled
                try:
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    verify = False
                    response = requests.get(url, verify=verify)
                    if response.status_code == 200:
                        try:
                            # If a 200, make sure you get valid JSON back in case you were routed to some
                            # other 200 response.
                            data = response.json()
                            succeed = True
                        except json.JSONDecodeError:
                            pass
                except requests.exceptions.ConnectionError:
                    pass
            else:
                # User decided not to proceed.
                raise ExitCLI("SSL Verification failed on server located at {}.".format(url))
        except requests.exceptions.ConnectionError:
            pass

        return succeed, data, verify

    def _discover_server(self, url: str):
        """Method to load the server's discovery data

        Args:
            url(str): URL/domain to the server's root (users may not be precise here, so we'll try to be smart)

        Returns:
            dict: discovery data returned from the server
        """
        url_parts = urlparse(url)
        if not url_parts.scheme:
            url_parts = urlparse("https://" + url)

        team_url = urljoin("https://" + url_parts.netloc, 'gigantum/.well-known/discover.json')
        enterprise_url = urljoin("https://" + url_parts.netloc, '.well-known/discover.json')

        succeed, data, verify = self._fetch_wellknown_data(team_url)
        if not succeed:
            succeed, data, verify = self._fetch_wellknown_data(enterprise_url)

        if not succeed:
            raise ExitCLI("Failed to discover configuration for server located at"
                          " {}. Check server URL and try again.".format(url))
        return data, verify

    def add_server(self, url):
        """Method to discover a server's configuration and add it to the local configured servers

        Args:
            url: URL/domain to the server's root (users may not be precise here, so we'll try to be smart)

        Returns:
            str: id for the server
        """
        server_data, verify = self._discover_server(url)

        # Ensure core URLS have trailing slashes to standardize within codebase
        server_data['git_url'] = server_data['git_url'] if server_data['git_url'][-1] == '/' \
            else server_data['git_url'] + '/'
        server_data['hub_api_url'] = server_data['hub_api_url'] if server_data['hub_api_url'][-1] == '/' \
            else server_data['hub_api_url'] + '/'
        server_data['object_service_url'] = server_data['object_service_url'] \
            if server_data['object_service_url'][-1] == '/' \
            else server_data['object_service_url'] + '/'

        # Verify Server is not already configured
        server_data_file = os.path.join(self.servers_dir, server_data['id'] + ".json")
        if os.path.exists(server_data_file):
            raise ValueError("The server `{}` located at {} is already configured.".format(server_data['name'], url))

        # Fetch Auth configuration
        response = requests.get(server_data['auth_config_url'], verify=verify)
        if response.status_code != 200:
            raise ExitCLI("Failed to load auth configuration "
                          "for server located at {}: {}".format(url, response.status_code))
        auth_data = response.json()

        # Create servers dir if it is missing (maybe this user has never started the client)
        if not os.path.isdir(self.servers_dir):
            os.makedirs(self.servers_dir, exist_ok=True)

        # Save configuration data
        save_data = {"server": server_data,
                     "auth": auth_data}
        with open(server_data_file, 'wt') as f:
            json.dump(save_data, f, indent=2)

        # Create directory for server's projects/datasets
        user_storage_dir = os.path.join(self.working_dir, 'servers', server_data['id'])
        os.makedirs(user_storage_dir, exist_ok=True)

        return server_data['id']

    def list_servers(self, should_print: bool = False):
        """Method to list configured servers, optionally printing a table

        Args:
            should_print(bool): flag indicating if the results should be printed

        Returns:
            list
        """
        configured_servers = list()
        for server_file in glob.glob(os.path.join(self.servers_dir, "*.json")):
            with open(server_file, 'rt') as f:
                data = json.load(f)
                hub_url_parts = urlparse(data['server']['hub_api_url'])
                server_url = hub_url_parts.scheme + "://" + hub_url_parts.netloc
                configured_servers.append((data['server']['id'], data['server']['name'], server_url))

        if should_print:
            print('%-30s' % "Server ID", '%-30s' % "Server Name", '%-30s' % "Server Location")
            for server in configured_servers:
                print('%-30s' % server[0], '%-30s' % server[1], '%-30s' % server[2])
            print("\n")

        return configured_servers
