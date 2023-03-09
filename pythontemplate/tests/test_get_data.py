import pytest
from pythontemplate import TemplateClass


@pytest.fixture
def template_class():
    yield TemplateClass(3)


def test_get_data(template_class, int_fixture):
    assert template_class.get_data(int_fixture) == [3, 3, 3]
