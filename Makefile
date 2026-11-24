

run:
	./mk_certs.sh hosts.local
	./mk_certs.sh test-client.local
	uv run naps-automatic-update \
        --ssl_cert certs/hosts.local/hosts.local.crt \
        --ssl_key certs/hosts.local/hosts.local.key \
        --ssl_ca certs/root_ca.crt \
        --vms examples/infra.json

test-check:
	uv run python -m naps_automatic_update.client.main
test-ping:
	curl --cacert certs/intermediate_ca.crt \
         --cert certs/test-client.local/test-client.local.crt \
         --key certs/test-client.local/test-client.local.key \
         https://localhost:8090/ping\
         -d "running"\
         | jq
         #-H "Content-Type: application/json" \

         
