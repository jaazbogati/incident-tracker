import pytest
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({'TESTING': True})

    with app.app_context():
        print(app.url_map)  # Print the URL map for debugging
    yield app

@pytest.fixture
def client(app):
    return app.test_client()


 