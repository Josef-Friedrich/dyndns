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
