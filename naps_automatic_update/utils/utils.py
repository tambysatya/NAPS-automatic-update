
from fastapi import FastAPI, HTTPException, Request
from starlette.requests import HTTPConnection
from cryptography import x509
from cryptography.x509.oid import ExtensionOID

def get_tls_name (request: HTTPConnection):
    tls = request.scope.get("extensions", {}).get("tls")
    if not tls:
        raise HTTPException(500, "TLS extension unavailable")

    chain = tls.get("client_cert_chain", [])
    if not chain:
        raise HTTPException(401, "No client certificate")

    cert = x509.load_pem_x509_certificate(chain[0].encode())

    san = cert.extensions.get_extension_for_oid(
        ExtensionOID.SUBJECT_ALTERNATIVE_NAME
    ).value

    dns = san.get_values_for_type(x509.DNSName),
    if dns == []:
        raise HTTPException(401, "No san in the certificate")
    name = dns[0][0].split(".")[0]
    return name



