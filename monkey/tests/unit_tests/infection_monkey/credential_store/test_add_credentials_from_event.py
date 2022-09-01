from unittest.mock import MagicMock
from uuid import UUID

from common.credentials import Credentials, Password, Username
from common.events import CredentialsStolenEvent
from infection_monkey.credential_repository import (
    IPropagationCredentialsRepository,
    add_credentials_from_event_to_propagation_credentials_repository,
)

credentials = [
    Credentials(
        identity=Username(username="test_username"), secret=Password(password="some_password")
    )
]

credentials_stolen_event = CredentialsStolenEvent(
    source=UUID("f811ad00-5a68-4437-bd51-7b5cc1768ad5"),
    target=None,
    timestamp=0.0,
    tags=frozenset({"stolen credentials"}),
    stolen_credentials=credentials,
)


def test_add_credentials_from_event_to_propagation_credentials_repository():
    mock_propagation_credentials_repository = MagicMock(spec=IPropagationCredentialsRepository)
    fn = add_credentials_from_event_to_propagation_credentials_repository(
        mock_propagation_credentials_repository
    )

    fn(credentials_stolen_event)

    assert mock_propagation_credentials_repository.add_credentials.called_with(credentials)
