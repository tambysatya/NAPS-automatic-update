from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from pydantic import ValidationError
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

    @app.websocket("/connect")
    async def connect (ws : WebSocket):
        vm = get_tls_name(ws.scope)

        if not state.is_name_allowed(vm):
            await ws.close(code=1008)
            print (f"{vm}: not allowed to connect")
            return
            

        await state.connect(vm, ws)

        try:
            while True:
                json = await ws.receive_json()
                try: 
                    message = VMMessage.model_validate(json)
                except ValidationError as v:
                    print (f"Invalid JSON from {vm}: {json}")
                    continue
                state.process_message (vm, message)
        except WebSocketDisconnect:
            state.disconnect(vm)
        

        return {"answer": "OK"}



    return app


