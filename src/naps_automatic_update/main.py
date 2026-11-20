import anyio
from anycorn import serve
from anycorn.config import Config
from pathlib import Path
import os
import argparse
import ssl

from .State import NAPSState
from .core import create_app

LISTEN = Path(os.environ.get("LISTEN_ADDR", "0.0.0.0:8000"))

async def run_server():
    parser = argparse.ArgumentParser (
            prog = "NAPS update orchestrator",
            description = "Opens a HTTPS server to synchronize updates and rollbacks using mTLS"
        )
    parser.add_argument ('--listen_on', help='the IP address to listen on', default="0.0.0.0")
    parser.add_argument ('--port', default="8090")
    parser.add_argument ('--ssl_cert', help='path to the ssl certificate')
    parser.add_argument ('--ssl_key', help ='path to the ssl certificate key')
    parser.add_argument ('--ssl_ca', help ='path to the ssl authority', required=True)
    parser.add_argument ('--vms', help ='path to the virtual machines JSON file', required=True)
    args = parser.parse_args()


    print (f"ssl_cert={args.ssl_cert} ssl_key={args.ssl_key} ssl_ca={args.ssl_ca}")

    config = Config ()

    config.bind = [args.listen_on + ":" + args.port]
    config.accesslog = "-"
    config.errorlog = "-"

    config.certfile = args.ssl_cert
    config.keyfile = args.ssl_key

    config.ca_certs = args.ssl_ca
    config.verify_mode = ssl.CERT_REQUIRED


    state = NAPSState.parse_file(args.vms)
    await serve (create_app(state) , config)

def main():
    anyio.run(run_server)


if __name__ == "__main__":
    main()
