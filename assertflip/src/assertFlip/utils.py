import typing as T
import subprocess
import os
from pathlib import Path

async def subprocess_run(args: T.Sequence[str], check: bool = False, timeout: T.Optional[int] = None, env = None) -> subprocess.CompletedProcess:
    """Provides an asynchronous version of subprocess.run"""
    import asyncio
    process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.STDOUT, env=env)
    output = None
    try:
        if timeout is not None:
            output, _ = await asyncio.wait_for(process.communicate(), timeout=timeout)
        else:
            output, _ = await process.communicate()

    except (asyncio.TimeoutError, asyncio.exceptions.TimeoutError):
        try:
            process.terminate()
            await process.wait()
        except ProcessLookupError:
            pass

        if timeout:
            timeout_f = float(timeout)
        else:
            timeout_f = 0.0
        raise subprocess.TimeoutExpired(args, timeout_f) from None
    
    if check and process.returncode:

        raise subprocess.CalledProcessError(process.returncode, args, output=output)

    return subprocess.CompletedProcess(args=args, returncode=T.cast(int, process.returncode), stdout=output)


def get_results_dir() -> Path:
    """
    Returns a writable directory for logs/attempts.

    Priority:
      1) ASSERTFLIP_RESULTS_DIR env (absolute or relative; ~ expanded)
      2) <repo_root>/result  (computed as two directories above this file)

    Ensures the directory exists.
    """
    env = os.environ.get("ASSERTFLIP_RESULTS_DIR")
    if env:
        p = Path(env).expanduser().resolve()
    else:
        # Two levels up from this file -> repo root; then "result"
        p = Path(__file__).resolve().parents[2] / "result"
    p.mkdir(parents=True, exist_ok=True)
    return p

