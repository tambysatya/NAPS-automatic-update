#!/usr/bin/env bash


mk_cert(){


	CERT_NAME="$1"
	mkdir -p "certs/$CERT_NAME"
	TARGET="certs/$CERT_NAME/$CERT_NAME"
	export STEPPATH=./step-ca

	step ca certificate \
		--offline \
		--provisioner ca \
		--password-file "$STEPPATH/ca-password.key" \
		--san $CERT_NAME \
		$CERT_NAME  $TARGET.crt $TARGET.key
}

mk_cert $1
