"""Entry point for the (not yet implemented) cli."""


import logging

logger = logging.getLogger("debianbts")
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.WARNING,
)


def main() -> None:
    """CLI entry point."""
    logger.warning("Not implemented yet, sorry!")


if __name__ == "__main__":
    main()
