#! /usr/bin/env python3

import os


def get_path(*path_segments):
    return os.path.join(os.getcwd(), *path_segments)


def open_file(*path_segments, clean=False):
    file_path = get_path(*path_segments)
    if clean:
        open(file_path, 'w').close()
    return open(file_path, 'a')


def main():
    header = open_file('README_header.rst')
    readme = open_file('README.rst')

    configuration = open_file('jfddns', 'configuration.rst')
    usage = open_file('jfddns', 'usage.rst')

    for line in header.read():
        readme.write(str(line))

    for line in configuration.read():
        readme.write(str(line))

    for line in usage.read():
        readme.write(str(line))


if __name__ == '__main__':
    main()
