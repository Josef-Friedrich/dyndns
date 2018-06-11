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
