from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import Response
import os
from cryptography import x509
from cryptography.x509.oid import ExtensionOID

from .utils import get_tls_name
from .State import NAPSState, VMStatus


def create_app (config_file):
    
    app = FastAPI()
    state = NAPSState.parse_file(config_file)

    @app.get("/hello")
    async def mtls(request: Request):

        name = get_tls_name(request)
        return {"hola": name}

    @app.get("/check")
    async def check(request: Request):

        name = get_tls_name(request)
        return state.model_dump()

    @app.post("/ping")
    async def ping (request: Request, status: str = Body (...)):
        name = get_tls_name(request)
        if not state.is_name_allowed(name):
            return {"error": "Not allowed"}
        return {"answer": "OK"}



    return app


