# Vulture Whitelist — False positives for framework-required variables
# Generated: 2026-04-22
# Reason: These variables are required by framework signatures (pytest fixtures,
# SQLAlchemy event handlers, Pydantic validators) even though they appear unused.

# pytest fixtures — used via dependency injection, not direct reference
server_fixture = None  # pytest fixture injection
setup_database = None  # pytest fixture injection
mock_bq = None  # pytest fixture injection
mock_anthropic_client = None  # pytest fixture injection

# SQLAlchemy event handler signatures — required by SA event API
connection_record = None  # @event.listens_for(engine, "connect") handler param

# Pydantic v1 validator context
__context = None  # @validator("field") context param

# Test variables named 'unused_*' are intentionally unused
unused_weights = None

# Variables needed for unpacking or API compliance
output_shape = None  # used in tensor shape computation context
stream_name = None  # async method parameter (monitor_output signature)
response_length = None  # Locust @events.request.add_listener required signature param
profile_id = None  # Kosmos CLI unpacking pattern
profile_type = None  # Kosmos CLI unpacking pattern
jurisdiction_name = None  # Lawtrack timeline_engine unpacking
fts_columns = None  # LanceDB hybrid search parameter
