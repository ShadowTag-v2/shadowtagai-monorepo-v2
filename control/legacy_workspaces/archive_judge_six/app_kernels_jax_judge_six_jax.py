import jax
import jax.numpy as jnp
from jax import jit
from functools import partial

@jit
def judge_six_enforce(input_ids, policy_matrix):
    """
    JAX implementation of Judge #6 enforcement kernel.
    
    Args:
        input_ids: (batch_size, seq_len) array of token IDs
        policy_matrix: (batch_size, seq_len) array of policy masks
        
    Returns:
        violation_flags: (batch_size,) boolean array indicating violations
    """
    # Bitwise AND to find violations
    violations = (input_ids & policy_matrix) != 0
    
    # Reduce across sequence dimension
    # If any token violates, the sequence is flagged
    any_violation = jnp.any(violations, axis=1)
    
    return any_violation

@partial(jit, static_argnums=(2,))
def batched_enforce(input_ids, policy_matrix, batch_size):
    """
    Batched enforcement wrapper.
    """
    return judge_six_enforce(input_ids, policy_matrix)

def init_mock_data(batch_size=1024, seq_len=256):
    """Initialize random data for testing."""
    key = jax.random.PRNGKey(0)
    k1, k2 = jax.random.split(key)
    
    input_ids = jax.random.randint(k1, (batch_size, seq_len), 0, 65536, dtype=jnp.int32)
    policy_matrix = jax.random.randint(k2, (batch_size, seq_len), 0, 65536, dtype=jnp.int32)
    
    return input_ids, policy_matrix
