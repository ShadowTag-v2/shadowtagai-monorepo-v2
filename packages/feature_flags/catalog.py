# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Feature flag catalog — All 119 GrowthBook flags mapped from Claude Code v2.1.91.

This module provides:
  - FlagCatalog: StrEnum of all known feature flags
  - FlagCategory: Grouping categories for operational awareness
  - HARDCODED_OVERRIDES: Dict of flags with forced local values
  - is_flag_enabled: Primary API for checking flag state

The catalog was extracted from src/services/analytics/growthbook.ts
and cross-referenced with the 372 ant-gate inventory.
"""

from __future__ import annotations

import logging
import os
from enum import StrEnum

logger = logging.getLogger(__name__)


class FlagCategory(StrEnum):
    """Operational groupings for feature flags."""

    SECURITY = "security"
    COMPACTION = "compaction"
    BRIDGE = "bridge"
    KAIROS = "kairos"
    MODEL = "model"
    TELEMETRY = "telemetry"
    UI = "ui"
    TOOL = "tool"
    PLUGIN = "plugin"
    SESSION = "session"
    CODENAME = "codename"  # Obfuscated internal codenames
    UNKNOWN = "unknown"


class FlagCatalog(StrEnum):
    """All 119 feature flags extracted from Claude Code v2.1.91 source leak.

    Naming convention: tengu_<codename> for Anthropic internal flags.
    Non-prefixed flags are infrastructure gates (Datadog, surveys, etc.).
    """

    # ── Infrastructure gates ──────────────────────────────────────────
    DATADOG_GATE_NAME = "DATADOG_GATE_NAME"
    MEMORY_SURVEY_GATE = "MEMORY_SURVEY_GATE"
    POST_COMPACT_SURVEY_GATE = "POST_COMPACT_SURVEY_GATE"
    TRUSTED_DEVICE_GATE = "TRUSTED_DEVICE_GATE"
    ENHANCED_TELEMETRY_BETA = "enhanced_telemetry_beta"
    TEAMMEM = "TEAMMEM"  # Gates team memory sync + extractMemories modules

    # ── Amber series (prompt/JSON tooling) ────────────────────────────
    AGENT_LIST_ATTACH = "tengu_agent_list_attach"
    AMBER_FLINT = "tengu_amber_flint"
    AMBER_JSON_TOOLS = "tengu_amber_json_tools"
    AMBER_PRISM = "tengu_amber_prism"
    AMBER_QUARTZ_DISABLED = "tengu_amber_quartz_disabled"
    AMBER_STOAT = "tengu_amber_stoat"

    # ── Model/security ────────────────────────────────────────────────
    ANT_MODEL_OVERRIDE = "tengu_ant_model_override"
    ANTI_DISTILL_FAKE_TOOL_INJECTION = "tengu_anti_distill_fake_tool_injection"
    ATTRIBUTION_HEADER = "tengu_attribution_header"

    # ── Agent/background ──────────────────────────────────────────────
    AUTO_BACKGROUND_AGENTS = "tengu_auto_background_agents"
    AUTO_MODE_CONFIG = "tengu_auto_mode_config"

    # ── Codename series (obfuscated) ──────────────────────────────────
    BASALT_3KR = "tengu_basalt_3kr"
    BIRCH_TRELLIS = "tengu_birch_trellis"
    BRAMBLE_LINTEL = "tengu_bramble_lintel"

    # ── Bridge (IDE/extension integration) ────────────────────────────
    BRIDGE_INITIAL_HISTORY_CAP = "tengu_bridge_initial_history_cap"
    BRIDGE_POLL_INTERVAL_CONFIG = "tengu_bridge_poll_interval_config"
    BRIDGE_REPL_V2 = "tengu_bridge_repl_v2"
    BRIDGE_REPL_V2_CONFIG = "tengu_bridge_repl_v2_config"
    BRIDGE_REPL_V2_CSE_SHIM_ENABLED = "tengu_bridge_repl_v2_cse_shim_enabled"
    BRIDGE_SYSTEM_INIT = "tengu_bridge_system_init"

    # ── CCR (context/caching/recovery) ────────────────────────────────
    CCR_BRIDGE = "tengu_ccr_bridge"
    CCR_BUNDLE_MAX_BYTES = "tengu_ccr_bundle_max_bytes"
    CCR_MIRROR = "tengu_ccr_mirror"

    # ── Codename series ───────────────────────────────────────────────
    CHAIR_SERMON = "tengu_chair_sermon"
    CHOMP_INFLECTION = "tengu_chomp_inflection"
    CHROME_AUTO_ENABLE = "tengu_chrome_auto_enable"
    CICADA_NAP_MS = "tengu_cicada_nap_ms"

    # ── Cobalt series ─────────────────────────────────────────────────
    COBALT_FROST = "tengu_cobalt_frost"
    COBALT_HARBOR = "tengu_cobalt_harbor"
    COBALT_LANTERN = "tengu_cobalt_lantern"
    COBALT_RACCOON = "tengu_cobalt_raccoon"

    # ── Compaction ────────────────────────────────────────────────────
    COLLAGE_KALEIDOSCOPE = "tengu_collage_kaleidoscope"
    COMPACT_CACHE_PREFIX = "tengu_compact_cache_prefix"
    COMPACT_LINE_PREFIX_KILLSWITCH = "tengu_compact_line_prefix_killswitch"
    COMPACT_STREAMING_RETRY = "tengu_compact_streaming_retry"

    # ── Copper series ─────────────────────────────────────────────────
    COPPER_BRIDGE = "tengu_copper_bridge"
    COPPER_PANDA = "tengu_copper_panda"
    CORAL_FERN = "tengu_coral_fern"
    CORK_M4Q = "tengu_cork_m4q"

    # ── Security/permissions ──────────────────────────────────────────
    DESTRUCTIVE_COMMAND_WARNING = "tengu_destructive_command_warning"
    DISABLE_BYPASS_PERMISSIONS_MODE = "tengu_disable_bypass_permissions_mode"
    DISABLE_KEEPALIVE_ON_ECONNRESET = "tengu_disable_keepalive_on_econnreset"
    DISABLE_STREAMING_TO_NON_STREAMING_FALLBACK = "tengu_disable_streaming_to_non_streaming_fallback"

    # ── Settings/sync ─────────────────────────────────────────────────
    ENABLE_SETTINGS_SYNC_PUSH = "tengu_enable_settings_sync_push"
    FGTS = "tengu_fgts"

    # ── Codename series ───────────────────────────────────────────────
    GLACIER_2XR = "tengu_glacier_2xr"
    GREY_STEP2 = "tengu_grey_step2"

    # ── Harbor (permissions/ledger) ───────────────────────────────────
    HARBOR = "tengu_harbor"
    HARBOR_LEDGER = "tengu_harbor_ledger"
    HARBOR_PERMISSIONS = "tengu_harbor_permissions"

    # ── Codename series ───────────────────────────────────────────────
    HAWTHORN_STEEPLE = "tengu_hawthorn_steeple"
    HAWTHORN_WINDOW = "tengu_hawthorn_window"
    HERRING_CLOCK = "tengu_herring_clock"
    HIVE_EVIDENCE = "tengu_hive_evidence"

    # ── Model ─────────────────────────────────────────────────────────
    IMMEDIATE_MODEL_COMMAND = "tengu_immediate_model_command"
    IRON_GATE_CLOSED = "tengu_iron_gate_closed"
    JADE_ANVIL_4 = "tengu_jade_anvil_4"

    # ── KAIROS (proactive suggestion engine) ──────────────────────────
    KAIROS_BRIEF = "tengu_kairos_brief"
    KAIROS_BRIEF_CONFIG = "tengu_kairos_brief_config"
    KAIROS_CRON = "tengu_kairos_cron"
    KAIROS_CRON_CONFIG = "tengu_kairos_cron_config"
    KAIROS_CRON_DURABLE = "tengu_kairos_cron_durable"

    # ── UI/keybindings ────────────────────────────────────────────────
    KEYBINDING_CUSTOMIZATION_RELEASE = "tengu_keybinding_customization_release"

    # ── Codename series ───────────────────────────────────────────────
    LAPIS_FINCH = "tengu_lapis_finch"
    LODESTONE_ENABLED = "tengu_lodestone_enabled"
    MARBLE_FOX = "tengu_marble_fox"
    MARBLE_SANDCASTLE = "tengu_marble_sandcastle"
    MIRACULO_THE_BARD = "tengu_miraculo_the_bard"
    MOTH_COPSE = "tengu_moth_copse"
    ONYX_PLOVER = "tengu_onyx_plover"

    # ── Session/token management ──────────────────────────────────────
    OTK_SLOT_V1 = "tengu_otk_slot_v1"
    PAPER_HALYARD = "tengu_paper_halyard"
    PASSPORT_QUAIL = "tengu_passport_quail"
    PEBBLE_LEAF_PRUNE = "tengu_pebble_leaf_prune"
    PENGUINS_OFF = "tengu_penguins_off"
    PEWTER_LEDGER = "tengu_pewter_ledger"
    PID_BASED_VERSION_LOCKING = "tengu_pid_based_version_locking"

    # ── Plan mode ─────────────────────────────────────────────────────
    PLAN_MODE_INTERVIEW_PHASE = "tengu_plan_mode_interview_phase"

    # ── Plugin ────────────────────────────────────────────────────────
    PLUGIN_OFFICIAL_MKT_GIT_FALLBACK = "tengu_plugin_official_mkt_git_fallback"

    # ── Codename series ───────────────────────────────────────────────
    PLUM_VX3 = "tengu_plum_vx3"

    # ── Prompt cache ──────────────────────────────────────────────────
    PROMPT_CACHE_1H_CONFIG = "tengu_prompt_cache_1h_config"

    # ── Codename series ───────────────────────────────────────────────
    QUARTZ_LANTERN = "tengu_quartz_lantern"
    QUIET_FERN = "tengu_quiet_fern"

    # ── Read dedup ────────────────────────────────────────────────────
    READ_DEDUP_KILLSWITCH = "tengu_read_dedup_killswitch"

    # ── Remote ────────────────────────────────────────────────────────
    REMOTE_BACKEND = "tengu_remote_backend"
    SAGE_COMPASS = "tengu_sage_compass"

    # ── Sandbox ───────────────────────────────────────────────────────
    SANDBOX_DISABLED_COMMANDS = "tengu_sandbox_disabled_commands"
    SCRATCH = "tengu_scratch"

    # ── Codename series ───────────────────────────────────────────────
    SEDGE_LANTERN = "tengu_sedge_lantern"

    # ── Session memory ────────────────────────────────────────────────
    SESSION_MEMORY = "tengu_session_memory"

    # ── Slate series ──────────────────────────────────────────────────
    SLATE_HERON = "tengu_slate_heron"
    SLATE_PRISM = "tengu_slate_prism"
    SLATE_THIMBLE = "tengu_slate_thimble"

    # ── Subagent ──────────────────────────────────────────────────────
    SLIM_SUBAGENT_CLAUDEMD = "tengu_slim_subagent_claudemd"
    SM_COMPACT = "tengu_sm_compact"

    # ── Codename series ───────────────────────────────────────────────
    STRAP_FOYER = "tengu_strap_foyer"

    # ── Streaming ─────────────────────────────────────────────────────
    STREAMING_TOOL_EXECUTION2 = "tengu_streaming_tool_execution2"
    SURREAL_DALI = "tengu_surreal_dali"

    # ── Terminal ──────────────────────────────────────────────────────
    TERMINAL_PANEL = "tengu_terminal_panel"
    TERMINAL_SIDEBAR = "tengu_terminal_sidebar"

    # ── Codename series ───────────────────────────────────────────────
    TERN_ALLOY = "tengu_tern_alloy"
    THINKBACK = "tengu_thinkback"
    TIDE_ELM = "tengu_tide_elm"
    TIMBER_LARK = "tengu_timber_lark"

    # ── Tool ──────────────────────────────────────────────────────────
    TOOL_PEAR = "tengu_tool_pear"
    TOOL_SEARCH_UNSUPPORTED_MODELS = "tengu_tool_search_unsupported_models"
    TOOLREF_DEFER_J8M = "tengu_toolref_defer_j8m"

    # ── Telemetry ─────────────────────────────────────────────────────
    TRACE_LANTERN = "tengu_trace_lantern"
    TURTLE_CARBON = "tengu_turtle_carbon"

    # ── Model ─────────────────────────────────────────────────────────
    ULTRAPLAN_MODEL = "tengu_ultraplan_model"

    # ── VS Code ───────────────────────────────────────────────────────
    VSCODE_CC_AUTH = "tengu_vscode_cc_auth"
    VSCODE_ONBOARDING = "tengu_vscode_onboarding"
    VSCODE_REVIEW_UPSELL = "tengu_vscode_review_upsell"

    # ── Willow mode ───────────────────────────────────────────────────
    WILLOW_MODE = "tengu_willow_mode"


# ── Category mapping ──────────────────────────────────────────────────
# Maps flag → category for operational grouping and dashboards
FLAG_CATEGORIES: dict[FlagCatalog, FlagCategory] = {
    FlagCatalog.DATADOG_GATE_NAME: FlagCategory.TELEMETRY,
    FlagCatalog.MEMORY_SURVEY_GATE: FlagCategory.SESSION,
    FlagCatalog.POST_COMPACT_SURVEY_GATE: FlagCategory.COMPACTION,
    FlagCatalog.TRUSTED_DEVICE_GATE: FlagCategory.SECURITY,
    FlagCatalog.ENHANCED_TELEMETRY_BETA: FlagCategory.TELEMETRY,
    FlagCatalog.ANT_MODEL_OVERRIDE: FlagCategory.MODEL,
    FlagCatalog.ANTI_DISTILL_FAKE_TOOL_INJECTION: FlagCategory.SECURITY,
    FlagCatalog.DESTRUCTIVE_COMMAND_WARNING: FlagCategory.SECURITY,
    FlagCatalog.DISABLE_BYPASS_PERMISSIONS_MODE: FlagCategory.SECURITY,
    FlagCatalog.HARBOR: FlagCategory.SECURITY,
    FlagCatalog.HARBOR_LEDGER: FlagCategory.SECURITY,
    FlagCatalog.HARBOR_PERMISSIONS: FlagCategory.SECURITY,
    FlagCatalog.IRON_GATE_CLOSED: FlagCategory.SECURITY,
    FlagCatalog.COMPACT_CACHE_PREFIX: FlagCategory.COMPACTION,
    FlagCatalog.COMPACT_LINE_PREFIX_KILLSWITCH: FlagCategory.COMPACTION,
    FlagCatalog.COMPACT_STREAMING_RETRY: FlagCategory.COMPACTION,
    FlagCatalog.SM_COMPACT: FlagCategory.COMPACTION,
    FlagCatalog.COLLAGE_KALEIDOSCOPE: FlagCategory.COMPACTION,
    FlagCatalog.CCR_BRIDGE: FlagCategory.COMPACTION,
    FlagCatalog.CCR_BUNDLE_MAX_BYTES: FlagCategory.COMPACTION,
    FlagCatalog.CCR_MIRROR: FlagCategory.COMPACTION,
    FlagCatalog.BRIDGE_INITIAL_HISTORY_CAP: FlagCategory.BRIDGE,
    FlagCatalog.BRIDGE_POLL_INTERVAL_CONFIG: FlagCategory.BRIDGE,
    FlagCatalog.BRIDGE_REPL_V2: FlagCategory.BRIDGE,
    FlagCatalog.BRIDGE_REPL_V2_CONFIG: FlagCategory.BRIDGE,
    FlagCatalog.BRIDGE_REPL_V2_CSE_SHIM_ENABLED: FlagCategory.BRIDGE,
    FlagCatalog.BRIDGE_SYSTEM_INIT: FlagCategory.BRIDGE,
    FlagCatalog.KAIROS_BRIEF: FlagCategory.KAIROS,
    FlagCatalog.KAIROS_BRIEF_CONFIG: FlagCategory.KAIROS,
    FlagCatalog.KAIROS_CRON: FlagCategory.KAIROS,
    FlagCatalog.KAIROS_CRON_CONFIG: FlagCategory.KAIROS,
    FlagCatalog.KAIROS_CRON_DURABLE: FlagCategory.KAIROS,
    FlagCatalog.ULTRAPLAN_MODEL: FlagCategory.MODEL,
    FlagCatalog.IMMEDIATE_MODEL_COMMAND: FlagCategory.MODEL,
    FlagCatalog.ATTRIBUTION_HEADER: FlagCategory.MODEL,
    FlagCatalog.TRACE_LANTERN: FlagCategory.TELEMETRY,
    FlagCatalog.TURTLE_CARBON: FlagCategory.TELEMETRY,
    FlagCatalog.TERMINAL_PANEL: FlagCategory.UI,
    FlagCatalog.TERMINAL_SIDEBAR: FlagCategory.UI,
    FlagCatalog.KEYBINDING_CUSTOMIZATION_RELEASE: FlagCategory.UI,
    FlagCatalog.VSCODE_CC_AUTH: FlagCategory.UI,
    FlagCatalog.VSCODE_ONBOARDING: FlagCategory.UI,
    FlagCatalog.VSCODE_REVIEW_UPSELL: FlagCategory.UI,
    FlagCatalog.TOOL_PEAR: FlagCategory.TOOL,
    FlagCatalog.TOOL_SEARCH_UNSUPPORTED_MODELS: FlagCategory.TOOL,
    FlagCatalog.TOOLREF_DEFER_J8M: FlagCategory.TOOL,
    FlagCatalog.STREAMING_TOOL_EXECUTION2: FlagCategory.TOOL,
    FlagCatalog.PLUGIN_OFFICIAL_MKT_GIT_FALLBACK: FlagCategory.PLUGIN,
    FlagCatalog.SESSION_MEMORY: FlagCategory.SESSION,
    FlagCatalog.READ_DEDUP_KILLSWITCH: FlagCategory.SESSION,
    FlagCatalog.PLAN_MODE_INTERVIEW_PHASE: FlagCategory.SESSION,
    FlagCatalog.SANDBOX_DISABLED_COMMANDS: FlagCategory.SECURITY,
    FlagCatalog.REMOTE_BACKEND: FlagCategory.BRIDGE,
    FlagCatalog.PROMPT_CACHE_1H_CONFIG: FlagCategory.COMPACTION,
    FlagCatalog.SLIM_SUBAGENT_CLAUDEMD: FlagCategory.SESSION,
    FlagCatalog.CHROME_AUTO_ENABLE: FlagCategory.UI,
    FlagCatalog.AUTO_BACKGROUND_AGENTS: FlagCategory.SESSION,
    FlagCatalog.AUTO_MODE_CONFIG: FlagCategory.SESSION,
    FlagCatalog.PID_BASED_VERSION_LOCKING: FlagCategory.SECURITY,
    # ── Batch 6 decoded flags (2026-05-04) ────────────────────────────
    FlagCatalog.TIDE_ELM: FlagCategory.UI,  # Effort level upsell A/B test
    FlagCatalog.TERN_ALLOY: FlagCategory.SESSION,  # Subagent fanout A/B test
    FlagCatalog.TIMBER_LARK: FlagCategory.KAIROS,  # /loop command scheduling A/B test
    FlagCatalog.ENABLE_SETTINGS_SYNC_PUSH: FlagCategory.BRIDGE,  # CLI sync gate
    FlagCatalog.STRAP_FOYER: FlagCategory.COMPACTION,  # CCR download gate
    FlagCatalog.TEAMMEM: FlagCategory.SESSION,  # Gates team memory sync + extractMemories
}


# ── Hardcoded overrides ──────────────────────────────────────────────
# Flags that are forced ON or OFF locally, bypassing GrowthBook remote.
# Mirrors the CLAUDE_INTERNAL_FC_OVERRIDES env-var pattern from
# src/services/analytics/growthbook.ts.
HARDCODED_OVERRIDES: dict[str, bool | int | str] = {
    # ── Security: all ON ──────────────────────────────────────────────
    FlagCatalog.DESTRUCTIVE_COMMAND_WARNING: True,
    FlagCatalog.DISABLE_BYPASS_PERMISSIONS_MODE: True,
    FlagCatalog.HARBOR: True,
    FlagCatalog.HARBOR_PERMISSIONS: True,
    FlagCatalog.IRON_GATE_CLOSED: True,
    FlagCatalog.PID_BASED_VERSION_LOCKING: True,
    FlagCatalog.SANDBOX_DISABLED_COMMANDS: True,
    FlagCatalog.TRUSTED_DEVICE_GATE: True,
    # ── Anti-distillation: OFF (we're not Anthropic) ──────────────────
    FlagCatalog.ANTI_DISTILL_FAKE_TOOL_INJECTION: False,
    FlagCatalog.ANT_MODEL_OVERRIDE: False,
    # ── KAIROS: all ON ────────────────────────────────────────────────
    FlagCatalog.KAIROS_BRIEF: True,
    FlagCatalog.KAIROS_CRON: True,
    FlagCatalog.KAIROS_CRON_DURABLE: True,
    # ── Compaction: all ON ────────────────────────────────────────────
    FlagCatalog.COMPACT_CACHE_PREFIX: True,
    FlagCatalog.COMPACT_STREAMING_RETRY: True,
    FlagCatalog.SM_COMPACT: True,
    FlagCatalog.CCR_BRIDGE: True,
    # ── Session: ON ───────────────────────────────────────────────────
    FlagCatalog.SESSION_MEMORY: True,
    FlagCatalog.AUTO_BACKGROUND_AGENTS: True,
    FlagCatalog.PLAN_MODE_INTERVIEW_PHASE: True,
    FlagCatalog.SLIM_SUBAGENT_CLAUDEMD: True,
    # ── Read dedup: ON (collapse read/search) ─────────────────────────
    FlagCatalog.READ_DEDUP_KILLSWITCH: False,  # Killswitch OFF = dedup ON
    # ── Tool streaming: ON ────────────────────────────────────────────
    FlagCatalog.STREAMING_TOOL_EXECUTION2: True,
    # ── Telemetry: OFF (per doctrine) ─────────────────────────────────
    FlagCatalog.DATADOG_GATE_NAME: False,
    FlagCatalog.ENHANCED_TELEMETRY_BETA: False,
    FlagCatalog.MEMORY_SURVEY_GATE: False,
    FlagCatalog.POST_COMPACT_SURVEY_GATE: False,
}


def is_flag_enabled(flag: str | FlagCatalog, default: bool = False) -> bool:
    """Check if a feature flag is enabled.

    Resolution order:
    1. HARDCODED_OVERRIDES (local, highest priority)
    2. Environment variable override (AGNT_FLAG_<NAME>=1|0)
    3. GrowthBookRemoteCache (if populated)
    4. default

    Args:
        flag: Flag name (string or FlagCatalog enum).
        default: Fallback value if flag is not found anywhere.

    Returns:
        bool: Whether the flag is enabled.
    """
    flag_str = str(flag)

    # 1. Hardcoded override
    if flag_str in HARDCODED_OVERRIDES:
        val = HARDCODED_OVERRIDES[flag_str]
        return bool(val)

    # 2. Environment variable
    env_key = f"AGNT_FLAG_{flag_str.upper().replace('-', '_')}"
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val.lower() in ("1", "true", "yes", "on")

    # 3. GrowthBook cache (import lazily to avoid circular)
    try:
        from packages.feature_flags.growthbook_cache import GrowthBookRemoteCache

        # Use module-level singleton if it exists
        _cache = getattr(GrowthBookRemoteCache, "_singleton", None)
        if _cache is not None:
            cached_val = _cache.get(flag_str)
            if cached_val is not None:
                return bool(cached_val)
    except ImportError:
        pass

    # 4. Default
    return default


def get_flag_value(
    flag: str | FlagCatalog,
    default: bool | int | str | None = None,
) -> bool | int | str | None:
    """Get the raw value of a feature flag (not just bool).

    Same resolution order as is_flag_enabled but returns the raw value.
    """
    flag_str = str(flag)

    if flag_str in HARDCODED_OVERRIDES:
        return HARDCODED_OVERRIDES[flag_str]

    env_key = f"AGNT_FLAG_{flag_str.upper().replace('-', '_')}"
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val

    return default


def flag_summary() -> dict[str, dict[str, str | bool]]:
    """Get a summary of all flags with their current effective values.

    Returns a dict of flag_name → {value, source, category}.
    """
    result: dict[str, dict[str, str | bool]] = {}
    for flag in FlagCatalog:
        flag_str = str(flag)
        source = "default"
        value: bool | int | str | None = False

        if flag_str in HARDCODED_OVERRIDES:
            source = "hardcoded"
            value = HARDCODED_OVERRIDES[flag_str]
        else:
            env_key = f"AGNT_FLAG_{flag_str.upper().replace('-', '_')}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                source = "env"
                value = env_val

        category = FLAG_CATEGORIES.get(flag, FlagCategory.UNKNOWN)
        result[flag_str] = {
            "value": bool(value) if isinstance(value, bool) else str(value),
            "source": source,
            "category": str(category),
        }

    return result
