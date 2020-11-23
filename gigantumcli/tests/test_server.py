import pytest
import tempfile
import uuid
import os
import shutil
import responses

from gigantumcli.server import ServerConfig
from gigantumcli.utilities import ExitCLI


@pytest.fixture
def server_config():
    """Fixture to create a Build instance with a test image name that does not exist and cleanup after"""
    unit_test_working_dir = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
    os.mkdir(unit_test_working_dir)
    yield ServerConfig(working_dir=unit_test_working_dir)
    shutil.rmtree(unit_test_working_dir)


class TestServerConfig(object):
    @responses.activate
    def test_server_discovery_fails(self, server_config):
        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/discover.json',
                      json={},
                      status=404)
        responses.add(responses.GET, 'https://test2.gigantum.com/.well-known/discover.json',
                      json={},
                      status=404)

        with pytest.raises(ExitCLI):
            server_config.add_server("test2.gigantum.com")

    @responses.activate
    def test_auth_discovery_fails(self, server_config):
        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/discover.json',
                      json={},
                      status=404)
        responses.add(responses.GET, 'https://test2.gigantum.com/.well-known/discover.json',
                      json={"id": 'another-server',
                            "name": "Another server",
                            "git_url": "https://test2.repo.gigantum.com/",
                            "git_server_type": "gitlab",
                            "hub_api_url": "https://test2.gigantum.com/api/v1/",
                            "object_service_url": "https://test2.api.gigantum.com/object-v1/",
                            "user_search_url": "https://user-search2.us-east-1.cloudsearch.amazonaws.com",
                            "lfs_enabled": True,
                            "auth_config_url": "https://test2.gigantum.com/.well-known/auth.json"},
                      status=200)

        responses.add(responses.GET, 'https://test2.gigantum.com/.well-known/auth.json',
                      json={},
                      status=404)

        with pytest.raises(ExitCLI):
            server_config.add_server("https://test2.gigantum.com/")

        with pytest.raises(ExitCLI):
            server_config.add_server("https://thiswillneverwork.gigantum.com/")

    @responses.activate
    def test_add_server(self, server_config):
        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/discover.json',
                      json={"id": 'another-server',
                            "name": "Another server",
                            "git_url": "https://test2.repo.gigantum.com/",
                            "git_server_type": "gitlab",
                            "hub_api_url": "https://test2.gigantum.com/api/v1/",
                            "object_service_url": "https://test2.api.gigantum.com/object-v1/",
                            "user_search_url": "https://user-search2.us-east-1.cloudsearch.amazonaws.com",
                            "lfs_enabled": True,
                            "auth_config_url": "https://test2.gigantum.com/gigantum/.well-known/auth.json"},
                      status=200)

        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/auth.json',
                      json={"audience": "test2.api.gigantum.io",
                            "issuer": "https://test2-auth.gigantum.com",
                            "signing_algorithm": "RS256",
                            "public_key_url": "https://test2-auth.gigantum.com/.well-known/jwks.json",
                            "login_url": "https://test2.gigantum.com/client/login",
                            "login_type": "auth0",
                            "auth0_client_id": "0000000000000000"},
                      status=200)

        server_id = server_config.add_server("https://test2.gigantum.com/")
        assert server_id == 'another-server'
        assert os.path.isfile(os.path.join(server_config.servers_dir, 'another-server.json'))
        assert os.path.isdir(os.path.join(server_config.working_dir, 'servers', 'another-server'))

    @responses.activate
    def test_add_server_already_configured(self, server_config):
        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/discover.json',
                      json={"id": 'another-server',
                            "name": "Another server",
                            "git_url": "https://test2.repo.gigantum.com/",
                            "git_server_type": "gitlab",
                            "hub_api_url": "https://test2.gigantum.com/api/v1/",
                            "object_service_url": "https://test2.api.gigantum.com/object-v1/",
                            "user_search_url": "https://user-search2.us-east-1.cloudsearch.amazonaws.com",
                            "lfs_enabled": True,
                            "auth_config_url": "https://test2.gigantum.com/gigantum/.well-known/auth.json"},
                      status=200)

        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/auth.json',
                      json={"audience": "test2.api.gigantum.io",
                            "issuer": "https://test2-auth.gigantum.com",
                            "signing_algorithm": "RS256",
                            "public_key_url": "https://test2-auth.gigantum.com/.well-known/jwks.json",
                            "login_url": "https://test2.gigantum.com/client/login",
                            "login_type": "auth0",
                            "auth0_client_id": "0000000000000000"},
                      status=200)

        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/discover.json',
                      json={"id": 'another-server',
                            "name": "Another server",
                            "git_url": "https://test2.repo.gigantum.com/",
                            "git_server_type": "gitlab",
                            "hub_api_url": "https://test2.gigantum.com/api/v1/",
                            "object_service_url": "https://test2.api.gigantum.com/object-v1/",
                            "user_search_url": "https://user-search2.us-east-1.cloudsearch.amazonaws.com",
                            "lfs_enabled": True,
                            "auth_config_url": "https://test2.gigantum.com/gigantum/.well-known/auth.json"},
                      status=200)

        server_id = server_config.add_server("https://test2.gigantum.com/")
        assert server_id == 'another-server'
        assert os.path.isfile(os.path.join(server_config.servers_dir, 'another-server.json'))
        assert os.path.isdir(os.path.join(server_config.working_dir, 'servers', 'another-server'))

        with pytest.raises(ValueError):
            server_config.add_server("https://test2.gigantum.com/")

    @responses.activate
    def test_list_servers(self, server_config):
        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/discover.json',
                      json={"id": 'another-server',
                            "name": "Another server",
                            "git_url": "https://test2.repo.gigantum.com/",
                            "git_server_type": "gitlab",
                            "hub_api_url": "https://test2.gigantum.com/api/v1/",
                            "object_service_url": "https://test2.api.gigantum.com/object-v1/",
                            "user_search_url": "https://user-search2.us-east-1.cloudsearch.amazonaws.com",
                            "lfs_enabled": True,
                            "auth_config_url": "https://test2.gigantum.com/gigantum/.well-known/auth.json"},
                      status=200)

        responses.add(responses.GET, 'https://test2.gigantum.com/gigantum/.well-known/auth.json',
                      json={"audience": "test2.api.gigantum.io",
                            "issuer": "https://test2-auth.gigantum.com",
                            "signing_algorithm": "RS256",
                            "public_key_url": "https://test2-auth.gigantum.com/.well-known/jwks.json",
                            "login_url": "https://test2.gigantum.com/client/login",
                            "login_type": "auth0",
                            "auth0_client_id": "0000000000000000"},
                      status=200)
        responses.add(responses.GET, 'https://test3.gigantum.com/gigantum/.well-known/discover.json',
                      json={"id": 'my-server',
                            "name": "My Server 1",
                            "git_url": "https://test3.repo.gigantum.com/",
                            "git_server_type": "gitlab",
                            "hub_api_url": "https://test3.gigantum.com/api/v1/",
                            "object_service_url": "https://test3.api.gigantum.com/object-v1/",
                            "user_search_url": "https://user-search3.us-east-1.cloudsearch.amazonaws.com",
                            "lfs_enabled": True,
                            "auth_config_url": "https://test3.gigantum.com/gigantum/.well-known/auth.json"},
                      status=200)

        responses.add(responses.GET, 'https://test3.gigantum.com/gigantum/.well-known/auth.json',
                      json={"audience": "test3.api.gigantum.io",
                            "issuer": "https://test3-auth.gigantum.com",
                            "signing_algorithm": "RS256",
                            "public_key_url": "https://test3-auth.gigantum.com/.well-known/jwks.json",
                            "login_url": "https://test3.gigantum.com/client/login",
                            "login_type": "auth0",
                            "auth0_client_id": "0000000000000000"},
                      status=200)

        server_id = server_config.add_server("https://test2.gigantum.com/")
        assert server_id == 'another-server'
        assert os.path.isfile(os.path.join(server_config.servers_dir, 'another-server.json'))
        assert os.path.isdir(os.path.join(server_config.working_dir, 'servers', 'another-server'))
        server_id = server_config.add_server("https://test3.gigantum.com/")
        assert server_id == 'my-server'
        assert os.path.isfile(os.path.join(server_config.servers_dir, 'my-server.json'))
        assert os.path.isdir(os.path.join(server_config.working_dir, 'servers', 'my-server'))

        server_list = server_config.list_servers(should_print=True)

        assert len(server_list) == 2
