.. image:: http://img.shields.io/pypi/v/dyndns.svg
    :target: https://pypi.python.org/pypi/dyndns

.. image:: https://travis-ci.org/Josef-Friedrich/dyndns.svg?branch=master
    :target: https://travis-ci.org/Josef-Friedrich/dyndns

About
-----

`dyndns <https://pypi.org/project/dyndns>`_  is a HTTP based API to
dynamically update DNS records (DynDNS). It’s uses Python and the
Flask web framework to accomplish this task.

Installation
------------

Install ``dyndns`` into the directory
``/usr/local/share/python-virtualenv/dyndns`` using a virtual
environment.

.. code-block:: text

    python3 -m venv /usr/local/share/python-virtualenv/dyndns
    source /usr/local/share/python-virtualenv/dyndns/bin/activate
    pip3 install dyndns


The working directory of our flask web API is in the directory
``/var/www/dyndns.example.com``. Create a file
``/var/www/dyndns.example.com/dyndns.ini``.

.. code-block:: ini

    [uwsgi]
    module = dyndns.webapp:app

    master = true
    processes = 5

    socket = /var/www/dyndns.example.com/dyndns.sock
    chmod-socket = 664
    uid = www-data
    gid = www-data
    vacuum = true

    die-on-term = true


Example configuration file for nginx:
``/etc/nginx/sites-available/dyndns.example.com.``

.. code-block:: text

    server {
    	server_name dyndns.example.com;
    	listen 80;
    	listen [::]:80;
    	return 301 https://$host$request_uri;
    }

    server {
    	listen 443 ssl;
    	listen [::]:443 ssl;
    	server_name dyndns.example.com;
    	ssl_certificate /etc/letsencrypt/live/dyndns.example.com/fullchain.pem;
    	ssl_certificate_key /etc/letsencrypt/live/dyndns.example.com/privkey.pem;

    	location / {
    			include uwsgi_params;
    			uwsgi_pass unix:/var/www/dyndns.example.com/dyndns.sock;
    	}

    }


``/etc/systemd/system/dyndns-uwsgi.service``

.. code-block:: text

    [Unit]
    Description=uWSGI instance to serve dyndns
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/var/www/dyndns.example.com
    Environment="PATH=/usr/local/share/python-virtualenv/dyndns/bin"
    ExecStart=/usr/local/share/python-virtualenv/dyndns/bin/uwsgi --ini uwsgi.ini

    [Install]
    WantedBy=multi-user.target

Configuration
-------------

``dyndns`` requires a configuration file in the YAML markup language.

``dyndns`` looks on three places for its configuration. It picks the
first existing configuration file and ignores the later in this order:

1. Custom path specified in the environment variable
   ``dyndns_CONFIG_FILE``
2. Current working directory of the ``dyndns`` app (cwd):
   ``<cwd>/.dyndns.yml``
3. ``/etc/dyndns.yml``

.. code-block:: yaml

    ---
    secret: 12345678
    nameserver: 127.0.0.1
    dyndns_domain: dyndns.example.com
    zones:
      - name: example.com
        tsig_key: tPyvZA==

* ``secret``: A password like secret string. The secret string has to
  be at least 8 characters long and only alphnumeric characters are
  allowed.
* ``nameserver``: The IP address of your nameserver. Version 4 or
  version 6 are allowed. Use ``127.0.0.1`` to communicate with your
  nameserver on the same machine.
* ``dyndns_domain``: The domain to serve the ``dyndns`` HTTP API. This
  key is only used in the usage page. Can be omitted.
* ``zones``: At least one zone specified as a list.

Usage
-----

``dyndns`` offers two HTTP web APIs to update DNS records. A simple
and a more restricted one using only path segments and a more flexible
using query strings.

Update by path
^^^^^^^^^^^^^^

1. ``<your-domain>/update-by-path/secret/fqdn``
2. ``<your-domain>/update-by-path/secret/fqdn/ip_1``
3. ``<your-domain>/update-by-path/secret/fqdn/ip_1/ip_2``

Update by query
^^^^^^^^^^^^^^^

``<your-domain>/update-by-query?secret=secret&fqdn=fqdn&ip_1=1.2.3.4``

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
* ``ttl``: Time to live. The default value is 300.

Delete by path
^^^^^^^^^^^^^^

Hit this url to delete a DNS record corresponding to the ``fqdn``.
Both ipv4 and ipv6 entries are deleted.

``<your-domain>/delete-by-path/secret/fqdn``

