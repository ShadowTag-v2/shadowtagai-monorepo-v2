from service.app.config import load_settings
from service.app.adapters.authority_state import AuthorityState
from service.app.adapters.memory_atoms import replace_authority_atoms

s = load_settings()
authority = AuthorityState(s.authority_state_path).read()
print(replace_authority_atoms(s.postgres_dsn, s.repo_id, authority))
