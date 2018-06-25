Installation
------------

Install ``jfddns`` into the directory
``/usr/local/share/python-virtualenv/jfddns`` using a virtual
environment.

.. code-block:: text

    python3 -m venv /usr/local/share/python-virtualenv/jfddns
    source /usr/local/share/python-virtualenv/jfddns/bin/activate
    pip3 install jfddns


The working directory of our flask web API is in the directory
``/var/www/dyndns.example.com``. Create a file
``/var/www/dyndns.example.com/jfddns.ini``.

.. code-block:: ini

    [uwsgi]
    module = jfddns.uwsgi:app

    master = true
    processes = 5

    socket = /var/www/dyndns.example.com/jfddns.sock
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
    			uwsgi_pass unix:/var/www/dyndns.example.com/jfddns.sock;
    	}

    }


``/etc/systemd/system/jfddns-uwsgi.service``

.. code-block:: text

    [Unit]
    Description=uWSGI instance to serve jfddns
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/var/www/dyndns.example.com
    Environment="PATH=/usr/local/share/python-virtualenv/jfddns/bin"
    ExecStart=/usr/local/share/python-virtualenv/jfddns/bin/uwsgi --ini uwsgi.ini

    [Install]
    WantedBy=multi-user.target
