"""Apollo/UiPath design tokens and global CSS injection for Streamlit.

Light theme by default. Tokens mirror:
  apollo-wind/src/styles/tailwind.consumer.css  (body.light block)
  apollo-core statuses.css (pill colours)
"""

from __future__ import annotations
from typing import Literal, TypedDict
import streamlit as st
from pathlib import Path
import base64


# ── Palette (Apollo light theme) ─────────────────────────────────────────────
PALETTE: dict[str, str] = {
    # Surfaces
    "surface": "#ffffff",  # --surface (background)
    "surface_raised": "#ffffff",  # --surface-raised (cards)
    "surface_overlay": "#f4f5f7",  # --surface-overlay (inputs, tabs)
    "surface_hover": "#e9f1fa",  # --surface-hover
    "surface_muted": "#f4f5f7",  # --surface-muted (badges)
    # Text / foreground
    "foreground": "#182027",  # --foreground (primary text)
    "foreground_emp": "#09090a",  # --foreground-emp (strong headings)
    "foreground_muted": "#526069",  # --foreground-muted (secondary text)
    "foreground_subtle": "#8a97a0",  # --foreground-subtle (captions)
    # Brand
    "brand": "#2a44d4",  # --brand / --color-primary (light)
    "brand_hover": "#1e35a8",  # darker on hover
    "brand_soft": "#e9f1fa",  # --surface-hover (light brand bg)
    # Border
    "border": "#c9d1d9",  # --ap-wind-border (light)
    "border_subtle": "#e5e9ed",  # --border-subtle
    # Status colours (from statuses.css)
    "error": "#c34242",  # understocked / danger
    "error_bg": "#f9ecec",
    "warning": "#d97706",  # overstocked / caution
    "warning_bg": "#fffbeb",
    "success": "#38703f",  # on-target / fast mover
    "success_bg": "#eff8f0",
    "info": "#2a44d4",  # brand blue
    "info_bg": "#eaecfb",
    "neutral": "#526069",  # muted
    "neutral_bg": "#f4f5f7",
}


class ColourPair(TypedDict):
    primary: str
    soft: str
    ink: str


_INSIGHT_COLOURS: dict[str, ColourPair] = {
    "DEAD_STOCK": {
        "primary": PALETTE["neutral"],
        "soft": PALETTE["neutral_bg"],
        "ink": PALETTE["surface"],
    },
    "STORE_ISSUE": {
        "primary": PALETTE["error"],
        "soft": PALETTE["error_bg"],
        "ink": PALETTE["surface"],
    },
    "SLOW_MOVER": {
        "primary": PALETTE["neutral"],
        "soft": PALETTE["neutral_bg"],
        "ink": PALETTE["foreground"],
    },
    "FAST_MOVER": {
        "primary": PALETTE["success"],
        "soft": PALETTE["success_bg"],
        "ink": PALETTE["surface"],
    },
    "MEDIUM_MOVEMENT": {
        "primary": PALETTE["warning"],
        "soft": PALETTE["warning_bg"],
        "ink": PALETTE["foreground"],
    },
    "RANGE_GAP": {
        "primary": PALETTE["error"],
        "soft": PALETTE["error_bg"],
        "ink": PALETTE["surface"],
    },
    "MEDIUM_RANGE_GAP": {
        "primary": PALETTE["warning"],
        "soft": PALETTE["warning_bg"],
        "ink": PALETTE["foreground"],
    },
    "LOW_RANGE_GAP": {
        "primary": PALETTE["warning"],
        "soft": PALETTE["warning_bg"],
        "ink": PALETTE["foreground"],
    },
    "NO_ONLINE_SIGNAL": {
        "primary": PALETTE["neutral"],
        "soft": PALETTE["neutral_bg"],
        "ink": PALETTE["surface"],
    },
    "BALANCED": {
        "primary": PALETTE["success"],
        "soft": PALETTE["success_bg"],
        "ink": PALETTE["surface"],
    },
    "SEASON_MISMATCH": {
        "primary": PALETTE["error"],
        "soft": PALETTE["error_bg"],
        "ink": PALETTE["surface"],
    },
    "MID_MISMATCH": {
        "primary": PALETTE["warning"],
        "soft": PALETTE["warning_bg"],
        "ink": PALETTE["foreground"],
    },
    "SEASONAL_OK": {
        "primary": PALETTE["success"],
        "soft": PALETTE["success_bg"],
        "ink": PALETTE["surface"],
    },
    "NO_SIGNAL": {
        "primary": PALETTE["neutral"],
        "soft": PALETTE["neutral_bg"],
        "ink": PALETTE["foreground"],
    },
    "CATEGORY_DIVERGENCE": {
        "primary": PALETTE["error"],
        "soft": PALETTE["error_bg"],
        "ink": PALETTE["surface"],
    },
    "MEDIUM_DIVERGENCE": {
        "primary": PALETTE["warning"],
        "soft": PALETTE["warning_bg"],
        "ink": PALETTE["foreground"],
    },
    "ALIGNED": {
        "primary": PALETTE["success"],
        "soft": PALETTE["success_bg"],
        "ink": PALETTE["surface"],
    },
    "OVER_INDEXING": {
        "primary": PALETTE["neutral"],
        "soft": PALETTE["neutral_bg"],
        "ink": PALETTE["surface"],
    },
    "STOCK_OVERSTOCK": {
        "primary": PALETTE["error"],
        "soft": PALETTE["error_bg"],
        "ink": PALETTE["surface"],
    },
    "STOCK_UNDERSTOCK": {
        "primary": PALETTE["warning"],
        "soft": PALETTE["warning_bg"],
        "ink": PALETTE["foreground"],
    },
    "NO_PEER_DATA": {
        "primary": PALETTE["neutral"],
        "soft": PALETTE["neutral_bg"],
        "ink": PALETTE["foreground"],
    },
}

_INSIGHT_SEVERITY: dict[str, Literal["high", "med", "low", "neutral"]] = {
    "DEAD_STOCK": "high",
    "STORE_ISSUE": "high",
    "RANGE_GAP": "high",
    "SEASON_MISMATCH": "high",
    "CATEGORY_DIVERGENCE": "high",
    "STOCK_OVERSTOCK": "high",
    "MEDIUM_RANGE_GAP": "med",
    "MEDIUM_MOVEMENT": "med",
    "MID_MISMATCH": "med",
    "MEDIUM_DIVERGENCE": "med",
    "STOCK_UNDERSTOCK": "med",
    "SLOW_MOVER": "low",
    "LOW_RANGE_GAP": "low",
    "FAST_MOVER": "neutral",
    "BALANCED": "neutral",
    "SEASONAL_OK": "neutral",
    "ALIGNED": "neutral",
    "NO_ONLINE_SIGNAL": "neutral",
    "NO_SIGNAL": "neutral",
    "OVER_INDEXING": "neutral",
    "NO_PEER_DATA": "neutral",
}


def colour_for(insight_type: str | None) -> ColourPair:
    if insight_type and insight_type in _INSIGHT_COLOURS:
        return _INSIGHT_COLOURS[insight_type]
    return {
        "primary": PALETTE["neutral"],
        "soft": PALETTE["neutral_bg"],
        "ink": PALETTE["foreground"],
    }


def severity_for(insight_type: str | None) -> str:
    return _INSIGHT_SEVERITY.get(insight_type or "", "neutral")


def logo_b64() -> str:
    path = Path(__file__).parent / "assets" / "uipath-logo.svg"
    return base64.b64encode(path.read_bytes()).decode()


# ── Global CSS ────────────────────────────────────────────────────────────────
_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inconsolata:wght@400;500;600&display=swap');

:root {
    --surface:          #ffffff;
    --surface-raised:   #ffffff;
    --surface-overlay:  #f4f5f7;
    --surface-hover:    #e9f1fa;
    --surface-muted:    #f4f5f7;
    --foreground:       #182027;
    --foreground-emp:   #09090a;
    --foreground-muted: #526069;
    --foreground-subtle:#8a97a0;
    --brand:            #2a44d4;
    --brand-hover:      #1e35a8;
    --brand-soft:       #e9f1fa;
    --border:           #c9d1d9;
    --border-subtle:    #e5e9ed;
    --error:            #c34242;
    --error-bg:         #f9ecec;
    --warning:          #d97706;
    --warning-bg:       #fffbeb;
    --success:          #38703f;
    --success-bg:       #eff8f0;
    --neutral:          #526069;
    --neutral-bg:       #f4f5f7;

    --radius-sm:   4px;
    --radius-md:   8px;
    --radius-lg:   12px;
    --radius-pill: 20px;
    --shadow-card: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
    --font-mono:   'Inconsolata', 'SF Mono', Menlo, Consolas, monospace;
    --font-body:   system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* ── Page ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--surface) !important;
    color: var(--foreground);
    font-family: var(--font-body);
}
#MainMenu, [data-testid="stToolbar"], [data-testid="stDecoration"], footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stAppViewContainer"] > .main { padding-top: 1.5rem; }
.main .block-container { max-width: 1380px; padding: 1.5rem 2rem 4rem 2rem; }
[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
[data-testid="stColumn"], [data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important; box-shadow: none !important;
    background: transparent !important; padding: 0 !important;
}

/* ── Typography ── */
h1, h2, h3, h4, h5 {
    font-family: var(--font-body) !important;
    font-weight: 700; color: var(--foreground-emp);
    letter-spacing: -0.01em; line-height: 1.15;
}
h1 { font-size: 2.4rem; } h2 { font-size: 1.7rem; } h3 { font-size: 1.3rem; }
p, span, div, label, li { color: var(--foreground); font-family: var(--font-body); }
.stButton > button p, .stButton > button span, .stButton > button div {
    color: #ffffff !important; font-weight: 600 !important;
}

/* ── Inputs ── */
input, textarea, .stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--foreground) !important;
}
input:focus, textarea:focus {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px var(--brand-soft) !important;
}

/* ── Primary button — Apollo brand blue ── */
.stButton > button,
.stButton > button[kind="primary"],
.stButton > button[kind="secondary"] {
    background: var(--brand) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    height: 44px !important;
    padding: 0 1.75rem !important;
    letter-spacing: 0.01em !important;
    transition: background 160ms ease, transform 160ms ease;
}
.stButton > button:hover { background: var(--brand-hover) !important; transform: translateY(-1px); }
.stButton > button:active, .stButton > button:focus:not(:active) {
    background: var(--brand) !important;
    box-shadow: 0 0 0 3px var(--brand-soft) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] section {
    background: var(--surface-overlay);
    border: 1.5px dashed var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
}
[data-testid="stFileUploader"] section:hover { border-color: var(--brand); }
[data-testid="stFileUploader"] button {
    background: var(--surface) !important;
    color: var(--foreground) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border);
    gap: 1.5rem; padding-bottom: 0;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: var(--foreground-muted) !important;
    font-family: var(--font-body) !important;
    font-weight: 500 !important; font-size: 0.82rem !important;
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 0.85rem 0 !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; height: auto !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: var(--brand) !important;
    border-bottom-color: var(--brand) !important;
}
[data-baseweb="tab-highlight"] { background: transparent !important; }
[data-baseweb="tab-border"] { background: transparent !important; }

/* ── Multiselect ── */
[data-testid="stMultiSelect"] label, [data-testid="stTextInput"] label {
    font-family: var(--font-mono) !important; font-size: 0.68rem !important;
    text-transform: uppercase; letter-spacing: 0.10em;
    color: var(--foreground-muted) !important; margin-bottom: 0.35rem !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    min-height: 38px !important; box-shadow: none !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child:focus-within {
    border-color: var(--brand) !important;
    box-shadow: 0 0 0 3px var(--brand-soft) !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: var(--brand-soft) !important;
    color: var(--brand) !important;
    border-radius: var(--radius-pill) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important; font-weight: 500 !important;
}
/* Dropdown list items — must be dark on white */
[data-baseweb="popover"] ul li,
[data-baseweb="menu"] li,
[data-baseweb="list-item"],
[role="listbox"] li,
[role="option"] {
    color: var(--foreground) !important;
    background: var(--surface) !important;
    font-family: var(--font-body) !important;
    font-size: 0.875rem !important;
}
[data-baseweb="popover"] ul li:hover,
[data-baseweb="menu"] li:hover,
[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: var(--surface-hover) !important;
    color: var(--foreground-emp) !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.10) !important;
}
/* Placeholder text inside the select */
[data-testid="stMultiSelect"] input::placeholder,
[data-testid="stMultiSelect"] [data-baseweb="select"] input {
    color: var(--foreground-subtle) !important;
}

/* ── Spinner / progress ── */
.stSpinner > div { border-color: var(--brand) transparent transparent transparent !important; }
.stProgress > div > div > div { background: var(--brand) !important; }

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md);
}
[data-testid="stDataFrame"] [role="columnheader"] {
    background: var(--surface-overlay) !important;
    color: var(--foreground-subtle) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.70rem !important; text-transform: uppercase;
    letter-spacing: 0.10em; font-weight: 500;
}

/* ── Hero (upload page) ── */
.rm-hero {
    display: grid; grid-template-columns: 4.5fr 5.5fr;
    gap: 3rem; align-items: center;
    padding: 2rem 0 2.5rem 0;
    border-bottom: 1px solid var(--border); margin-bottom: 2rem;
}
.rm-uipath-logo { width: 120px; height: auto; object-fit: contain; margin-bottom: 1rem; display: block; }
.rm-hero-title {
    font-family: var(--font-body); font-size: 2.6rem;
    line-height: 1.05; color: var(--foreground-emp);
    font-weight: 700; letter-spacing: -0.02em;
}
.rm-hero-title em { font-style: normal; color: var(--brand); }
.rm-hero-blurb {
    font-family: var(--font-body); font-size: 1rem;
    line-height: 1.6; color: var(--foreground-muted); max-width: 52ch;
}
.rm-rules-list { display: flex; flex-direction: column; gap: 0.6rem; }
.rm-rule-item {
    display: grid; grid-template-columns: 2rem 10rem 1fr;
    align-items: baseline; gap: 0.75rem;
}
.rm-rule-num {
    font-family: var(--font-mono); font-size: 0.72rem;
    color: var(--foreground-subtle); letter-spacing: 0.04em;
}
.rm-rule-name {
    font-family: var(--font-body); font-size: 0.9rem;
    font-weight: 600; color: var(--foreground-emp);
}
.rm-rule-desc {
    font-family: var(--font-body); font-size: 0.82rem;
    color: var(--foreground-muted); line-height: 1.4;
}

/* ── Section header ── */
.rm-section { margin: 1.5rem 0 0.85rem 0; }
.rm-section-title {
    font-family: var(--font-body); font-size: 1.35rem;
    font-weight: 700; color: var(--foreground-emp);
    letter-spacing: -0.01em; margin-bottom: 0.2rem;
}
.rm-section-subtitle {
    font-family: var(--font-body); font-size: 0.88rem;
    color: var(--foreground-subtle); max-width: 60ch;
}

/* ── KPI card ── */
.rm-kpi-card {
    background: var(--surface-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    border-left: 4px solid var(--border);
    padding: 1.4rem 1.5rem 1.6rem 1.5rem;
    box-shadow: var(--shadow-card);
    transition: transform 280ms ease, box-shadow 280ms ease;
    height: 100%;
    opacity: 0;
    animation: rm-rise 500ms cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}
.rm-kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.10); }
.rm-kpi-card.severity-high    { border-left-color: var(--error); }
.rm-kpi-card.severity-med     { border-left-color: var(--warning); }
.rm-kpi-card.severity-low     { border-left-color: var(--brand); }
.rm-kpi-card.severity-neutral { border-left-color: var(--success); }
.rm-kpi-eyebrow {
    font-family: var(--font-mono); font-size: 0.67rem;
    color: var(--foreground-subtle); text-transform: uppercase;
    letter-spacing: 0.14em; margin-bottom: 0.5rem;
}
.rm-kpi-value {
    font-family: var(--font-body); font-size: 2.6rem;
    line-height: 1; color: var(--foreground-emp);
    font-weight: 700; letter-spacing: -0.02em;
    font-variant-numeric: tabular-nums;
}
.rm-kpi-label {
    font-family: var(--font-body); font-size: 0.83rem;
    color: var(--foreground-subtle); margin-top: 0.6rem; line-height: 1.35;
}
@keyframes rm-rise {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.rm-kpi-card.delay-0 { animation-delay: 40ms; }
.rm-kpi-card.delay-1 { animation-delay: 100ms; }
.rm-kpi-card.delay-2 { animation-delay: 160ms; }
.rm-kpi-card.delay-3 { animation-delay: 220ms; }
.rm-kpi-card.delay-4 { animation-delay: 280ms; }

/* ── Insight pill ── */
.rm-pill {
    display: inline-block;
    padding: 0.2rem 0.75rem 0.25rem 0.75rem;
    font-family: var(--font-mono); font-size: 0.67rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    border-radius: var(--radius-pill); font-weight: 600;
    border: 1px solid transparent; white-space: nowrap;
}

/* ── File slot card ── */
.rm-file-slot {
    border: 1px solid var(--border); border-radius: var(--radius-lg);
    background: var(--surface-raised); padding: 1.1rem 1.2rem 1.2rem 1.2rem;
    height: 100%; box-shadow: var(--shadow-card);
}
.rm-file-slot h5 {
    font-family: var(--font-body); font-size: 1rem;
    font-weight: 600; margin: 0 0 0.25rem 0; color: var(--foreground-emp);
}
.rm-file-slot .rm-required-cols {
    font-family: var(--font-mono); font-size: 0.67rem;
    color: var(--foreground-subtle); margin-top: 0.35rem; line-height: 1.55;
}

/* ── Loader step ── */
.rm-step {
    display: grid; grid-template-columns: 36px 56px 1fr 110px;
    gap: 1rem; align-items: center;
    padding: 0.95rem 0; border-bottom: 1px solid var(--border-subtle);
}
.rm-step:last-child { border-bottom: none; }
.rm-step-marker { font-family: var(--font-mono); font-size: 1.05rem; text-align: center; line-height: 1; }
.rm-step-marker.pending { color: var(--border); }
.rm-step-marker.running { color: var(--brand); animation: rm-spin 1.2s linear infinite; }
.rm-step-marker.done    { color: var(--success); }
.rm-step-marker.skipped { color: var(--foreground-subtle); }
.rm-step-num   { font-family: var(--font-mono); color: var(--foreground-subtle); font-size: 0.83rem; letter-spacing: 0.10em; }
.rm-step-title { font-family: var(--font-body); font-size: 1.05rem; color: var(--foreground-emp); font-weight: 600; }
.rm-step-sub   { font-family: var(--font-body); font-size: 0.82rem; color: var(--foreground-subtle); margin-top: 0.1rem; }
.rm-step-state { font-family: var(--font-mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.14em; text-align: right; }
.rm-step-state.pending { color: var(--foreground-subtle); }
.rm-step-state.running { color: var(--brand); }
.rm-step-state.done    { color: var(--success); }
.rm-step-state.skipped { color: var(--foreground-subtle); }
@keyframes rm-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* ── Exec summary ── */
.rm-exec {
    background: var(--brand-soft); border-left: 4px solid var(--brand);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 1rem 1.4rem; font-family: var(--font-body);
    font-size: 0.97rem; line-height: 1.6; color: var(--foreground);
    margin: 1rem 0 1.5rem 0;
}

/* ── Chart card ── */
.rm-chart-card {
    background: var(--surface-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem 0.25rem 1.5rem;
    margin-bottom: 0;
    box-shadow: var(--shadow-card);
}
.rm-chart-title {
    font-family: var(--font-body); font-size: 1rem;
    color: var(--foreground-emp); font-weight: 600;
    letter-spacing: -0.01em; margin: 0 0 0.1rem 0;
}
.rm-chart-subtitle {
    font-family: var(--font-body); font-size: 0.8rem;
    color: var(--foreground-subtle); margin: 0;
}

/* ── Table card ── */
.rm-tbl-card {
    background: var(--surface-raised);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem 0 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-card);
}
.rm-tbl-header {
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: 1rem; padding-bottom: 0.85rem;
    border-bottom: 1px solid var(--border-subtle);
}
.rm-tbl-title {
    font-family: var(--font-body) !important; font-size: 1rem !important;
    font-weight: 600 !important; color: var(--foreground-emp) !important;
    letter-spacing: -0.01em !important; margin: 0 0 0.1rem 0 !important;
}
.rm-tbl-subtitle {
    font-family: var(--font-body) !important; font-size: 0.8rem !important;
    color: var(--foreground-subtle) !important; margin: 0 !important;
}
.rm-tbl-wrap {
    overflow-x: auto; margin-top: 0.75rem;
    border-top: 1px solid var(--border-subtle);
}
.rm-tbl { width: 100%; border-collapse: collapse; background: var(--surface); }
.rm-th {
    font-family: var(--font-mono); font-size: 0.62rem; text-transform: uppercase;
    letter-spacing: 0.12em; font-weight: 600; color: var(--foreground-subtle);
    background: var(--surface-overlay); border-bottom: 1px solid var(--border);
    padding: 0.6rem 1rem; text-align: left; white-space: nowrap;
}
.rm-td {
    font-family: var(--font-body); font-size: 0.85rem; color: var(--foreground);
    padding: 0.55rem 1rem; border-bottom: 1px solid var(--border-subtle);
    font-variant-numeric: tabular-nums; vertical-align: middle;
}
tr:last-child .rm-td { border-bottom: none; }
tr:hover .rm-td { background: var(--surface-hover); }
.rm-tbl-footer {
    font-family: var(--font-mono); font-size: 0.65rem; color: var(--foreground-subtle);
    text-align: right; padding: 0.5rem 1rem 1rem 1rem; letter-spacing: 0.06em;
}
.rm-dl-link, .rm-dl-link:link, .rm-dl-link:visited {
    font-family: var(--font-mono) !important; font-size: 0.63rem !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important;
    color: var(--brand) !important; border: 1px solid var(--brand) !important;
    border-radius: var(--radius-md) !important; padding: 0.3rem 0.65rem !important;
    text-decoration: none !important; background: var(--brand-soft) !important;
    white-space: nowrap !important; display: inline-block !important;
    transition: border-color 160ms, background 160ms, color 160ms;
    font-weight: 600 !important;
}
.rm-dl-link:hover {
    background: var(--brand) !important; color: #ffffff !important;
    border-color: var(--brand) !important;
}

/* ── Pagination ── */
.rm-pagination {
    border-top: 1px solid var(--border); padding: 0.6rem 1rem 0.75rem 1rem;
    display: flex; align-items: center;
}
.rm-page-indicator {
    font-family: var(--font-mono); font-size: 0.72rem; color: var(--foreground-muted);
    text-align: center; letter-spacing: 0.06em; padding: 0.35rem 0;
}
/* Shrink Streamlit buttons inside pagination to feel compact */
.rm-pagination [data-testid="stButton"] button {
    padding: 0.25rem 0.75rem !important; font-size: 0.75rem !important;
    min-height: 0 !important; height: auto !important;
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    color: var(--foreground) !important; border-radius: var(--radius-md) !important;
}
.rm-pagination [data-testid="stButton"] button:hover:not(:disabled) {
    background: var(--surface-hover) !important; border-color: var(--brand) !important;
    color: var(--brand) !important;
}
.rm-pagination [data-testid="stButton"] button:disabled {
    opacity: 0.35 !important; cursor: not-allowed !important;
}

/* ── Action banner ── */
.rm-action-group { margin: 1.25rem 0 0.5rem 0; }
.rm-action-group-label {
    font-family: var(--font-mono); font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 0.12em; color: var(--foreground-subtle); margin-bottom: 0.5rem;
}
.rm-action-banner {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 0.85rem 1.1rem; border-radius: var(--radius-md);
    border-left: 4px solid var(--border); background: var(--surface-overlay);
    margin-bottom: 0.5rem;
}
.rm-action-banner.action-high   { border-left-color: var(--error);   background: var(--error-bg); }
.rm-action-banner.action-med    { border-left-color: var(--warning);  background: var(--warning-bg); }
.rm-action-banner.action-low    { border-left-color: var(--brand);    background: var(--brand-soft); }
.rm-action-banner.action-good   { border-left-color: var(--success);  background: var(--success-bg); }
.rm-action-icon { font-size: 1.15rem; line-height: 1; flex-shrink: 0; margin-top: 0.05rem; }
.rm-action-body { flex: 1; }
.rm-action-title {
    font-family: var(--font-body); font-size: 0.88rem; font-weight: 600;
    color: var(--foreground-emp); margin-bottom: 0.15rem;
}
.rm-action-desc {
    font-family: var(--font-body); font-size: 0.8rem;
    color: var(--foreground-muted); line-height: 1.45;
}
.rm-action-count {
    font-family: var(--font-mono); font-size: 0.68rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.10em;
    color: var(--foreground-subtle); flex-shrink: 0; align-self: center;
    background: rgba(0,0,0,0.05); border-radius: var(--radius-pill);
    padding: 0.15rem 0.55rem;
}
</style>
"""


def inject_global_css() -> None:
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def section_mark(title: str, subtitle: str = "") -> None:
    sub = f'<div class="rm-section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="rm-section">'
        f'<div class="rm-section-title">{title}</div>'
        f"{sub}</div>",
        unsafe_allow_html=True,
    )
