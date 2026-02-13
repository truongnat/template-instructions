
def pytest_ignore_collect(path, config):
    """Ignore all tests in this directory as they target removed V2 orchestration modules."""
    return True
