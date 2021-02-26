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


``vim /etc/systemd/system/dyndns-uwsgi.service``

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

``systemctl enable dyndns-uwsgi.service``

``systemctl start dyndns-uwsgi.service``
