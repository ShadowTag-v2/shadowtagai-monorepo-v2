from service.app.adapters.cortexltm import (
  add_event,
  create_thread,
  upsert_master_memory,
  write_summary,
)
from service.app.config import load_settings

s = load_settings()
user_id = "00000000-0000-0000-0000-000000000001"
thread_id = create_thread(s.postgres_dsn, user_id, "ANE exploration")
add_event(
  s.postgres_dsn,
  thread_id,
  "user",
  "We are testing ANE as the primary runtime on M1 Pro.",
)
add_event(
  s.postgres_dsn,
  thread_id,
  "assistant",
  "Understood. We will treat ANE as first choice with Metal fallback.",
)
write_summary(
  s.postgres_dsn,
  thread_id,
  "ANE-first policy with fallback is active for M1 Pro validation.",
)
upsert_master_memory(
  s.postgres_dsn,
  user_id,
  "PROJECTS",
  "ANE-first antigravity workbench on M1 Pro with CortexLTM + Beads + LanceDB",
)
