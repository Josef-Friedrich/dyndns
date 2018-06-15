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

``jfddns`` requires a configuration file in the YAML markup language.


.. code-block:: yaml

    ---
    secret: 12345678
    nameserver: 127.0.0.1
    jfddns_domain: example.com
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

Arguments for the query string
""""""""""""""""""""""""""""""

* ``secret``: A password like secret string. The secret string has to
  be at least 8 characters long and only alphnumeric characters are
  allowed.
* ``fqdn``: The Fully-Qualified Domain Name (e. g. ``www.example.com``).
  If you specify the argument ``fqdn``, you don’t have to specify the
  arguments ``zone_name`` and ``record_name``.
* ``zone_name``: The zone name (e. g. ``example.com``). You have to
  specify the argument ``record_name``.
* ``record_name``: The record name (e. g. ``www``). You have to
  specify the argument ``zone_name``.
* ``ip_1``: A IP address, can be version 4 or version 6.
* ``ip_2``: A second IP address, can be version 4 or version 6. Must
  be a different version than ``ip_1``.
* ``ipv4``: A IP address version 4.
* ``ipv6``: A IP address version 6.
