from flask import make_response

from common.credentials import Credentials
from monkey_island.cc.repository import ICredentialsRepository
from monkey_island.cc.resources.AbstractResource import AbstractResource


class PropagationCredentials(AbstractResource):
    urls = ["/api/propagation-credentials"]

    def __init__(self, credentials_repository: ICredentialsRepository):
        self._credentials_repository = credentials_repository

    def get(self):
        propagation_credentials = self._credentials_repository.get_all_credentials()

        return make_response(Credentials.to_json_array(propagation_credentials), 200)
