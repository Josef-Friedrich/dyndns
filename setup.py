from setuptools import setup, find_packages
import os
import versioneer


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="dyndns",
    author="Josef Friedrich",
    author_email="josef@friedrich.rocks",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A dynamic DNS HTTP based update server using the flask web framework.",
    long_description=read('README.rst'),
    url="https://github.com/Josef-Friedrich/dyndns",
    packages=find_packages(),
    install_requires=[
        'dnspython',
        'docutils',
        'flask',
        'Pygments',
        'PyYAML',
        'sphinx-argparse',
    ],
    tests_require=[
        'beautifulsoup4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'dyndns-debug = dyndns.cli:main',
        ],
    },
    package_data = {
        '': ['rst/*.rst', 'templates/*.html', 'static/*'],
    },
)
