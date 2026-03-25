import pytest

from app.repositories.helpers.repository_manager import RepositoryManager

#   TODO: I commented out because currently we have test files that relies on each other. Which could break when the testing order changes. I can revisit and modify them so each test is isolated.

# #   Clear database before testing each file, to ensure data is independent between files.
# @pytest.fixture(scope="module", autouse=True)
# def clean_up():
#     RepositoryManager.reset_all_repositories()