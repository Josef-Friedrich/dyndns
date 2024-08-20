.. image:: http://img.shields.io/pypi/v/dyndns.svg
    :target: https://pypi.org/project/dyndns
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/dyndns/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/dyndns/actions/workflows/tests.yml
    :alt: Tests

.. image:: https://readthedocs.org/projects/dyndns/badge/?version=latest
    :target: https://dyndns.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

About
-----

`dyndns <https://pypi.org/project/dyndns>`_  is a HTTP based API to
dynamically update DNS records (DynDNS). It’s uses Python and the
Flask web framework to accomplish this task.

Installation
------------

Bind9 installation
^^^^^^^^^^^^^^^^^^

``apt install bind9``

``vim /etc/bind/named.conf``

.. code-block:: text

    zone "dyndns.example.com" {
      type master;
      file "/var/cache/bind/dyndns.example.com.db";
      allow-update { key "dyndns.example.com."; };
    };

``tsig-keygen -a hmac-sha512 dyndns.example.com``

``vim /etc/bind/named.conf.local``

.. code-block:: text

    key "dyndns.example.com." {
      algorithm hmac-sha512;
      secret "nbB5i/5pyFywRPaUpEkzxtS0she1JOuZlASceu0lLU8Pe7dYpzuVDn9vbGvof2wjGkVsSZBG2DlaM3RwPHkd9g==";
    };

``vim /var/cache/bind/dyndns.example.com.db``

.. code-block:: text

    $ORIGIN dyndns.example.com.
    $TTL 300 ; 5 minutes

    ;; NAME IN SOA MNAME RNAME
    ; NAME: name of the zone
    ; IN: zone class (usually IN for internet)
    ; SOA: abbreviation for Start of Authority
    ; MNAME: Primary master name server for this zone
    ; RNAME: Email address of the administrator responsible for this zone. address is encoded as a name. (john\.doe.example.com.)

    @	IN SOA	ns1.example.com. admin.example.com. (
        1  ; SERIAL: Serial number for this zone.
        3600       ; REFRESH: number of seconds after which secondary name servers should query
        1000       ; RETRY: number of seconds after which secondary name servers should retry to request
        3600000    ; EXPIRE: number of seconds after which secondary name servers should stop answering request
        300        ; TTL: Time To Live for purposes of negative caching
        )
          NS	ns1.example.com.
          NS	ns2.example.com.
          A	185.11.138.33
          AAAA	2a03:2900:7:96::2

``systemctl enable named.service``

``systemctl start named.service``

Test Bind9 setup
^^^^^^^^^^^^^^^^

.. code-block:: text

    echo "server ns1.example.com
    debug
    update add debug.dyndns.example.com. 10 IN TXT \"$(date)\"
    send
    quit
    " | nsupdate -y 'hmac-sha512:dyndns.example.com:nbB5i/5pyFywRPaUpEkzxtS0she1JOuZlASceu0lLU8Pe7dYpzuVDn9vbGvof2wjGkVsSZBG2DlaM3RwPHkd9g=='

Show all records of the zone ``dyndns.example.com``

``dig @ns1.example.com. dyndns.example.com. axfr``
(axfr = Asynchronous Xfer Full Range)

dyndns installation
^^^^^^^^^^^^^^^^^^^

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
    module = dyndns.wsgi:app

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

``vim /etc/systemd/system/dyndns.service``

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

``systemctl enable dyndns.service``

``systemctl start dyndns.service``

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
    secret: '12345678'
    nameserver: 127.0.0.1
    port: 53
    zones:
      - name: dyndns.example.com
        tsig_key: tPyvZA==

* ``secret``: A password-like secret string. The secret string must be at least
  8 characters long and only alphanumeric characters are permitted.
* ``nameserver``: The IP address of your nameserver. Version 4 or
  version 6 are allowed. Use ``127.0.0.1`` to communicate with your
  nameserver on the same machine.
* ``port``: The port to which the DNS server listens. If the DNS server listens
  to port 53 by default, the value does not need to be specified.
* ``zones``: At least one zone specified as a list.
    * ``name``: The domain name of the zone, for example
      ``dyndns.example.com``.
    * ``tsig_key``: The tsig-key. Use the ``hmac-sha512`` algorithm to
      generate the key:
      ``tsig-keygen -a hmac-sha512 dyndns.example.com``

Usage
-----

``dyndns`` offers two HTTP web APIs to update DNS records: A simple API
and a more flexible API.

The simple API uses path segments
(``<your-domain>/update-by-path/secret/fqdn/ip_1`` see section “Update
by path”) and the more flexible API uses query strings
(``<your-domain>/update-by-query?secret=secret&fqdn=fqdn&ip_1=1.2.3.4``
see section “Update by query”).

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
* ``ip_1``: An IP address, can be version 4 or version 6.
* ``ip_2``: A second IP address, can be version 4 or version 6. Must
  be a different version than ``ip_1``.
* ``ipv4``: A version 4 IP address.
* ``ipv6``: A version 6 IP address.
* ``ttl``: Time to live. The default value is 300.

Delete by path
^^^^^^^^^^^^^^

Hit this url to delete a DNS record corresponding to the ``fqdn``.
Both ipv4 and ipv6 entries are deleted.

``<your-domain>/delete-by-path/secret/fqdn``

Update script
^^^^^^^^^^^^^

To update the ``dyndns`` server you can use the corresponding shell
script `dyndns-update-script.sh
<https://github.com/Josef-Friedrich/dyndns-update-script.sh>`_.

Edit the top of the shell script to fit your needs:

.. code-block:: text

    #! /bin/sh

    VALUE_DYNDNS_DOMAIN='dyndns.example.com'
    VALUE_SECRET='123'
    VALUE_ZONE_NAME='sub.example.com'

This update shell script is designed to work on OpenWRT. The only
dependency you have to install is `curl`.

Use cron jobs (``crontab -e``) to periodically push updates to the
``dyndns`` server:

.. code-block:: text

    */2 * * * * /usr/bin/dyndns-update-script.sh -S 5 -d br-lan -4 nrouter
    */2 * * * * /usr/bin/dyndns-update-script.sh -d br-lan -4 nuernberg
