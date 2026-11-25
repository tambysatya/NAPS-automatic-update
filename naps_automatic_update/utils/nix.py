import asyncio



async def nix_path_info(*args):
    proc = await asyncio.create_subprocess_exec(
                "nix", "path-info", *args,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE
            )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode().strip())

    return stdout.decode().strip()

