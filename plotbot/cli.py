import click
from . import maze


@click.group()
@click.version_option()
def main():
    pass


main.add_command(maze.run)

if __name__ == '__main__':
    main()
