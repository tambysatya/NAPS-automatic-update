

run:
	./mk_certs.sh hosts.local
	./mk_certs.sh client.local
	uv run naps-automatic-update \
        --ssl_cert certs/hosts.local/hosts.local.crt \
        --ssl_key certs/hosts.local/hosts.local.key \
        --ssl_ca certs/root_ca.crt

