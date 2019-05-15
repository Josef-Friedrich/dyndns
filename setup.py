import os

from setuptools import setup, find_packages
import versioneer


def read(file_name):
    """
    Read the contents of a text file and return its content.

    :param str file_name: The name of the file to read.

    :return: The content of the text file.
    :rtype: str
    """
    return open(
        os.path.join(os.path.dirname(__file__), file_name),
        encoding='utf-8'
    ).read()


setup(
    name="dyndns",
    author="Josef Friedrich",
    author_email="josef@friedrich.rocks",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A simple dynamic DNS update HTTP based API using python and the flask web framework.",
    long_description=read('README.rst'),
    url="https://github.com/Josef-Friedrich/dyndns",
    packages=find_packages(),
    install_requires=[
        'dnspython',
        'docutils',
        'flask',
        'Pygments',
        'PyYAML',
    ],
    tests_require=[
        'beautifulsoup4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'dyndns-debug = dyndns.cli:main',
        ],
    },
    package_data={
        '': ['rst/*.rst', 'templates/*.html', 'static/*'],
    },
)
