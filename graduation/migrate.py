"""CLI helper to run Graduation migrations."""

from .journal import apply_migrations


def main() -> None:
    apply_migrations()


if __name__ == "__main__":
    main()
