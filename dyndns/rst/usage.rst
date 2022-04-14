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
