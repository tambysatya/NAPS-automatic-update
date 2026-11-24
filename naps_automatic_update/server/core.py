from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import Response
import os
from cryptography import x509
from cryptography.x509.oid import ExtensionOID

from .utils import get_tls_name
from .Types import NAPSManifest, VMStatus
from .State import NAPSState


def create_app (config_file):
    
    app = FastAPI()
    manifest = NAPSManifest.parse_file(config_file)
    state = NAPSState(manifest=manifest)

    @app.get("/hello")
    async def mtls(request: Request):

        name = get_tls_name(request)
        return {"hola": name}

    @app.get("/check")
    async def check(request: Request):

        name = get_tls_name(request)
        return state.manifest.model_dump()

    @app.post("/ping")
    async def ping (request: Request, status: str = Body (...)):
        name = get_tls_name(request)
        if not state.is_name_allowed(name):
            return {"error": "Not allowed"}
        return {"answer": "OK"}



    return app


