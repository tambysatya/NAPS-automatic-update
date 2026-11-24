import asyncio
import websockets
import ssl

async def main():
    ssl_context = ssl.create_default_context(cafile="certs/root_ca.crt")
    ssl_context.load_cert_chain(
        certfile="certs/test-client.local/test-client.local.crt",
        keyfile ="certs/test-client.local/test-client.local.key"
    )
    async with websockets.connect(
        "wss://localhost:8090/connect",
        ssl = ssl_context
    ) as ws:
        async def receive():
            async for message in ws:
                print(f"\n[SERVER] {message}")

        async def send():
            while True:
                message = await asyncio.to_thread(input, "> ")
                await ws.send(message)

        await asyncio.gather(receive(), send())

asyncio.run(main())
