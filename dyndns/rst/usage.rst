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
