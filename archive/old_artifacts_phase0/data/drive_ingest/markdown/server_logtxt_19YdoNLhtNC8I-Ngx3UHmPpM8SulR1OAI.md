========================================
Verdict Systems - Starting Services
========================================
Starting API Server on port 8001...
INFO:     Will watch for changes in these directories: ['/Users/pikeymickey/ShadowTag-v2-fastapi-services']
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [99008] using StatReload
INFO:     Started server process [99125]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
WARNING:  StatReload detected changes in 'src/pnkln/intelligence_api.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [99125]
INFO:     Started server process [2030]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
WARNING:  StatReload detected changes in 'src/verdict_systems/api/main.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [2030]
Process SpawnProcess-3:
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/multiprocessing/process.py", line 313, in _bootstrap
    self.run()
    ~~~~~~~~^^
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
    ~~~~~~^^^^^^^^^^^^^^^^^
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/uvicorn/server.py", line 65, in run
    return asyncio.run(self.serve(sockets=sockets))
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "uvloop/loop.pyx", line 1518, in uvloop.loop.Loop.run_until_complete
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/uvicorn/server.py", line 69, in serve
    await self._serve(sockets)
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/uvicorn/server.py", line 76, in _serve
    config.load()
    ~~~~~~~~~~~^^
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/uvicorn/config.py", line 434, in load
    self.loaded_app = import_from_string(self.app)
                      ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1310, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/Users/pikeymickey/ShadowTag-v2-fastapi-services/src/verdict_systems/api/__init__.py", line 3, in <module>
    from .main import app
  File "/Users/pikeymickey/ShadowTag-v2-fastapi-services/src/verdict_systems/api/main.py", line 16, in <module>
    from slowapi import Limiter, _rate_limit_exceeded_handler
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/slowapi/__init__.py", line 1, in <module>
    from .extension import Limiter, _rate_limit_exceeded_handler
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/slowapi/extension.py", line 26, in <module>
    from limits import RateLimitItem  # type: ignore
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/limits/__init__.py", line 7, in <module>
    from . import _version, aio, storage, strategies
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/limits/aio/__init__.py", line 3, in <module>
    from . import storage, strategies
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/limits/aio/storage/__init__.py", line 8, in <module>
    from .base import MovingWindowSupport, SlidingWindowCounterSupport, Storage
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/limits/aio/storage/base.py", line 6, in <module>
    from deprecated.sphinx import versionadded
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/deprecated/__init__.py", line 15, in <module>
    from deprecated.classic import deprecated
  File "/Users/pikeymickey/Library/Python/3.13/lib/python/site-packages/deprecated/classic.py", line 35, in <module>
    class ClassicAdapter(wrapt.AdapterFactory):
                         ^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'wrapt' has no attribute 'AdapterFactory'
