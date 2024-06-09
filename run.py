"""
run file just for quick testing code
"""

from src.group import Group
import click


@click.command()
@click.option("--first", prompt="First Group", help="The first group")
@click.option("--second", prompt="Second Group", help="The second group")
def main(first, second):
    x = Group(first)
    y = Group(second)
    # sub = x.generate_subgroup(("6", "8"))
    z = x * y
    print(z.multable)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
