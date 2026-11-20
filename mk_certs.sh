#!/usr/bin/env bash


mk_cert(){


	CERT_NAME="$1"
	[[ -d "certs/$CERT_NAME" ]] && rm -R "certs/$CERT_NAME"
	mkdir -p "certs/$CERT_NAME"
	TARGET="certs/$CERT_NAME/$CERT_NAME"
	export STEPPATH=./step-ca

	step ca certificate \
		--offline \
		--provisioner ca \
		--password-file "$STEPPATH/ca-password.key" \
		--san $CERT_NAME \
		--san localhost \
		$CERT_NAME  $TARGET.crt $TARGET.key

	cat $TARGET.crt step-ca/certs/intermediate_ca.crt | sponge $TARGET.crt
}

mk_cert $1
