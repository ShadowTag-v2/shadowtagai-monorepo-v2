============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-7.4.3, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
benchmark: 4.0.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: /Users/pikeymickey/ShadowTag-v2-fastapi-services
configfile: pytest.ini
plugins: langsmith-0.4.47, timeout-2.2.0, cov-4.1.0, asyncio-0.21.1, mock-3.12.0, benchmark-4.0.0, anyio-4.11.0
asyncio: mode=Mode.AUTO
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
_________________ ERROR collecting tests/test_quality_gates.py _________________
ImportError while importing test module '/Users/pikeymickey/ShadowTag-v2-fastapi-services/tests/test_quality_gates.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_quality_gates.py:9: in <module>
    from gemini_ingestion_layer.quality import GateStatus, QualityGates
E   ModuleNotFoundError: No module named 'gemini_ingestion_layer'
------------------------------- Captured stderr --------------------------------
2025-11-26 01:19:16,115 - src.ShadowTag-v2.main - WARNING - CORS origins not configured - no CORS middleware added
2025-11-26 01:19:18,635 - src.ShadowTag-v2.main - INFO - Mounted game landing pages from /Users/pikeymickey/ShadowTag-v2-fastapi-services/src/ShadowTag-v2/../../landing-pages/gameport
=============================== warnings summary ===============================
src/ShadowTag-v2/config.py:13
  /Users/pikeymickey/ShadowTag-v2-fastapi-services/src/ShadowTag-v2/config.py:13: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Settings(BaseSettings):

src/ShadowTag-v2/database.py:47
  /Users/pikeymickey/ShadowTag-v2-fastapi-services/src/ShadowTag-v2/database.py:47: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

src/ShadowTag-v2/routes/ingestion.py:44
  /Users/pikeymickey/ShadowTag-v2-fastapi-services/src/ShadowTag-v2/routes/ingestion.py:44: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class IngestionJobResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR tests/test_quality_gates.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
========================= 3 warnings, 1 error in 0.13s =========================
