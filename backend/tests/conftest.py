import pytest
from context_core.fixtures import generate
@pytest.fixture(scope='session')
def clips(tmp_path_factory):
    return generate(tmp_path_factory.mktemp('media'))
