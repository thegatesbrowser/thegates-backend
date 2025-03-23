"""Django's command-line utility for administrative tasks."""
#!/usr/bin/env python
import os
import sys


def check_django_installation():
    try:
        from django.core.management import execute_from_command_line
        return execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gates.settings')
    execute_command_line = check_django_installation()
    execute_command_line(sys.argv)


if __name__ == '__main__':
    main()
