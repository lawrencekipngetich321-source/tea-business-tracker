"""
S&L TEA VENTURES — Tea Leaf Business Dashboard
Run locally: streamlit run app.py

Required packages:
    streamlit
    pandas
    numpy
    plotly
    python-docx

The app stores records in sl_tea_records.csv beside this file.
For Streamlit Community Cloud, note that local files may be reset when
the app is redeployed or its container restarts. Use a database or
persistent cloud storage for long-term multi-user production storage.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import calendar
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ---------------------------------------------------------------------
# APP CONFIGURATION & BRAND
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="S&L Tea Ventures | Business Dashboard",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded",
)

BRAND = "S&L TEA VENTURES"
NAVY = "#102A4C"
NAVY_DARK = "#071B34"
BLUE = "#2474C6"
SKY = "#47A9E8"
TEAL = "#19A7A0"
GREEN = "#35A853"
ORANGE = "#F39C35"
RED = "#E05260"
PURPLE = "#8662C7"
PINK = "#D65B9E"
GOLD = "#D6A52B"
INK = "#20334D"
MUTED = "#6B7C93"
BG = "#F3F6FA"
BORDER = "#E3EAF2"
WHITE = "#FFFFFF"

MONTHS = list(calendar.month_name)[1:]
MONTH_INDEX = {month: i + 1 for i, month in enumerate(MONTHS)}
DATA_PATH = Path(__file__).with_name("sl_tea_records.csv")

COLUMNS = [
    "Year",
    "Month",
    "Buying Price (KES/kg)",
    "Selling Price (KES/kg)",
    "Total Kgs",
    "Expenses (KES)",
    "Net Profit Target (KES)",
]

# The initial values below are taken from the supplied 2026 report.
# September's buying price is derived from buying cost / total kg:
# 29,148 / 1,388 = 21.00 KES/kg.
STARTER_DATA = pd.DataFrame(
    [
        {
            "Year": 2026,
            "Month": "September",
            "Buying Price (KES/kg)": 21.00,
            "Selling Price (KES/kg)": 24.00,
            "Total Kgs": 1388.00,
