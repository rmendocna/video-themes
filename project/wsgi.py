try:
    from app import create_app  # noqa - running at container root
except ImportError:
    from .app import create_app


application = create_app()

if __name__ == "__main__":
    application.run()
