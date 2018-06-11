.. image:: http://img.shields.io/pypi/v/jfddns.svg
    :target: https://pypi.python.org/pypi/jfddns

.. image:: https://travis-ci.org/Josef-Friedrich/jfddns.svg?branch=master
    :target: https://travis-ci.org/Josef-Friedrich/jfddns


jfddns
======

A simple dynamic DNS update HTTP based API using python and the flask
web framework.

Configuration
-------------

``jfddns`` requires a configuration file in the YAML markup language


.. code-block:: yaml

    ---
    secret: 12345678
    nameserver: 127.0.0.1
    zones:
      - name: example.com
        tsig_key: tPyvZA==


``jfddns`` looks on three places for its configuration. It picks the
first existing configuration file and ignores the later in this order:

1. Custom path specified in the environment variable ``JFDDNS_CONFIG_FILE``
2. Current working directory of the ``jfddns`` app (cwd): ``<cwd>/.jfddns.yml``
3. ``/etc/jfddns.yml``

Usage
-----

Update by path
^^^^^^^^^^^^^^

1. ``<your-domain>/update-by-path/<secret>/<fqdn>``
2. ``<your-domain>/update-by-path/<secret>/<fqdn>/<ip_1>``
3. ``<your-domain>/update-by-path/<secret>/<fqdn>/<ip_1>/<ip_2>``


Update by query
^^^^^^^^^^^^^^^

``<your-domain>/update-by-query?secret=<secret>&fqdn=<fqdn>``
