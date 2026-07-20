import csv
import datetime
import html
import io
import json
import os
import urllib.parse
from collections import Counter
from typing import Any

import altair as alt
import pandas as pd
import re
import requests
import streamlit as st
import streamlit.components.v1 as components

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Recruitment Copilot", page_icon="🤖", layout="wide")

# Flat line-style nav icons (base64 SVG), two tones per mode: muted (inactive) and blue (active)
ICONS = {
    "dashboard": {
        "light": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIzIiB5PSIzIiB3aWR0aD0iNyIgaGVpZ2h0PSI5IiByeD0iMS41Ii8+PHJlY3QgeD0iMTQiIHk9IjMiIHdpZHRoPSI3IiBoZWlnaHQ9IjUiIHJ4PSIxLjUiLz48cmVjdCB4PSIxNCIgeT0iMTIiIHdpZHRoPSI3IiBoZWlnaHQ9IjkiIHJ4PSIxLjUiLz48cmVjdCB4PSIzIiB5PSIxNiIgd2lkdGg9IjciIGhlaWdodD0iNSIgcng9IjEuNSIvPjwvc3ZnPg==",
        "dark": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM5NGEzYjgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIzIiB5PSIzIiB3aWR0aD0iNyIgaGVpZ2h0PSI5IiByeD0iMS41Ii8+PHJlY3QgeD0iMTQiIHk9IjMiIHdpZHRoPSI3IiBoZWlnaHQ9IjUiIHJ4PSIxLjUiLz48cmVjdCB4PSIxNCIgeT0iMTIiIHdpZHRoPSI3IiBoZWlnaHQ9IjkiIHJ4PSIxLjUiLz48cmVjdCB4PSIzIiB5PSIxNiIgd2lkdGg9IjciIGhlaWdodD0iNSIgcng9IjEuNSIvPjwvc3ZnPg==",
        "light_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMyNTYzZWIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIzIiB5PSIzIiB3aWR0aD0iNyIgaGVpZ2h0PSI5IiByeD0iMS41Ii8+PHJlY3QgeD0iMTQiIHk9IjMiIHdpZHRoPSI3IiBoZWlnaHQ9IjUiIHJ4PSIxLjUiLz48cmVjdCB4PSIxNCIgeT0iMTIiIHdpZHRoPSI3IiBoZWlnaHQ9IjkiIHJ4PSIxLjUiLz48cmVjdCB4PSIzIiB5PSIxNiIgd2lkdGg9IjciIGhlaWdodD0iNSIgcng9IjEuNSIvPjwvc3ZnPg==",
        "dark_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2MGE1ZmEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIzIiB5PSIzIiB3aWR0aD0iNyIgaGVpZ2h0PSI5IiByeD0iMS41Ii8+PHJlY3QgeD0iMTQiIHk9IjMiIHdpZHRoPSI3IiBoZWlnaHQ9IjUiIHJ4PSIxLjUiLz48cmVjdCB4PSIxNCIgeT0iMTIiIHdpZHRoPSI3IiBoZWlnaHQ9IjkiIHJ4PSIxLjUiLz48cmVjdCB4PSIzIiB5PSIxNiIgd2lkdGg9IjciIGhlaWdodD0iNSIgcng9IjEuNSIvPjwvc3ZnPg==",
    },
    "file": {
        "light": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTQgMkg2YTIgMiAwIDAgMC0yIDJ2MTZhMiAyIDAgMCAwIDIgMmgxMmEyIDIgMCAwIDAgMi0yVjh6Ii8+PHBhdGggZD0iTTE0IDJ2Nmg2Ii8+PHBhdGggZD0iTTkgMTNoNiIvPjxwYXRoIGQ9Ik05IDE3aDYiLz48L3N2Zz4=",
        "dark": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM5NGEzYjgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTQgMkg2YTIgMiAwIDAgMC0yIDJ2MTZhMiAyIDAgMCAwIDIgMmgxMmEyIDIgMCAwIDAgMi0yVjh6Ii8+PHBhdGggZD0iTTE0IDJ2Nmg2Ii8+PHBhdGggZD0iTTkgMTNoNiIvPjxwYXRoIGQ9Ik05IDE3aDYiLz48L3N2Zz4=",
        "light_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMyNTYzZWIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTQgMkg2YTIgMiAwIDAgMC0yIDJ2MTZhMiAyIDAgMCAwIDIgMmgxMmEyIDIgMCAwIDAgMi0yVjh6Ii8+PHBhdGggZD0iTTE0IDJ2Nmg2Ii8+PHBhdGggZD0iTTkgMTNoNiIvPjxwYXRoIGQ9Ik05IDE3aDYiLz48L3N2Zz4=",
        "dark_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2MGE1ZmEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTQgMkg2YTIgMiAwIDAgMC0yIDJ2MTZhMiAyIDAgMCAwIDIgMmgxMmEyIDIgMCAwIDAgMi0yVjh6Ii8+PHBhdGggZD0iTTE0IDJ2Nmg2Ii8+PHBhdGggZD0iTTkgMTNoNiIvPjxwYXRoIGQ9Ik05IDE3aDYiLz48L3N2Zz4=",
    },
    "users": {
        "light": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTcgMjF2LTJhNCA0IDAgMCAwLTQtNEg1YTQgNCAwIDAgMC00IDR2MiIvPjxjaXJjbGUgY3g9IjkiIGN5PSI3IiByPSI0Ii8+PHBhdGggZD0iTTIzIDIxdi0yYTQgNCAwIDAgMC0zLTMuODciLz48cGF0aCBkPSJNMTYgMy4xM2E0IDQgMCAwIDEgMCA3Ljc1Ii8+PC9zdmc+",
        "dark": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM5NGEzYjgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTcgMjF2LTJhNCA0IDAgMCAwLTQtNEg1YTQgNCAwIDAgMC00IDR2MiIvPjxjaXJjbGUgY3g9IjkiIGN5PSI3IiByPSI0Ii8+PHBhdGggZD0iTTIzIDIxdi0yYTQgNCAwIDAgMC0zLTMuODciLz48cGF0aCBkPSJNMTYgMy4xM2E0IDQgMCAwIDEgMCA3Ljc1Ii8+PC9zdmc+",
        "light_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMyNTYzZWIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTcgMjF2LTJhNCA0IDAgMCAwLTQtNEg1YTQgNCAwIDAgMC00IDR2MiIvPjxjaXJjbGUgY3g9IjkiIGN5PSI3IiByPSI0Ii8+PHBhdGggZD0iTTIzIDIxdi0yYTQgNCAwIDAgMC0zLTMuODciLz48cGF0aCBkPSJNMTYgMy4xM2E0IDQgMCAwIDEgMCA3Ljc1Ii8+PC9zdmc+",
        "dark_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2MGE1ZmEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTcgMjF2LTJhNCA0IDAgMCAwLTQtNEg1YTQgNCAwIDAgMC00IDR2MiIvPjxjaXJjbGUgY3g9IjkiIGN5PSI3IiByPSI0Ii8+PHBhdGggZD0iTTIzIDIxdi0yYTQgNCAwIDAgMC0zLTMuODciLz48cGF0aCBkPSJNMTYgMy4xM2E0IDQgMCAwIDEgMCA3Ljc1Ii8+PC9zdmc+",
    },
    "briefcase": {
        "light": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIyIiB5PSI3IiB3aWR0aD0iMjAiIGhlaWdodD0iMTQiIHJ4PSIyIi8+PHBhdGggZD0iTTE2IDIxVjVhMiAyIDAgMCAwLTItMmgtNGEyIDIgMCAwIDAtMiAydjE2Ii8+PHBhdGggZD0iTTIgMTNoMjAiLz48L3N2Zz4=",
        "dark": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM5NGEzYjgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIyIiB5PSI3IiB3aWR0aD0iMjAiIGhlaWdodD0iMTQiIHJ4PSIyIi8+PHBhdGggZD0iTTE2IDIxVjVhMiAyIDAgMCAwLTItMmgtNGEyIDIgMCAwIDAtMiAydjE2Ii8+PHBhdGggZD0iTTIgMTNoMjAiLz48L3N2Zz4=",
        "light_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMyNTYzZWIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIyIiB5PSI3IiB3aWR0aD0iMjAiIGhlaWdodD0iMTQiIHJ4PSIyIi8+PHBhdGggZD0iTTE2IDIxVjVhMiAyIDAgMCAwLTItMmgtNGEyIDIgMCAwIDAtMiAydjE2Ii8+PHBhdGggZD0iTTIgMTNoMjAiLz48L3N2Zz4=",
        "dark_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2MGE1ZmEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIyIiB5PSI3IiB3aWR0aD0iMjAiIGhlaWdodD0iMTQiIHJ4PSIyIi8+PHBhdGggZD0iTTE2IDIxVjVhMiAyIDAgMCAwLTItMmgtNGEyIDIgMCAwIDAtMiAydjE2Ii8+PHBhdGggZD0iTTIgMTNoMjAiLz48L3N2Zz4=",
    },
    "barchart": {
        "light": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMyAzdjE4aDE4Ii8+PHJlY3QgeD0iNyIgeT0iMTIiIHdpZHRoPSIzIiBoZWlnaHQ9IjYiIHJ4PSIwLjUiLz48cmVjdCB4PSIxMyIgeT0iOCIgd2lkdGg9IjMiIGhlaWdodD0iMTAiIHJ4PSIwLjUiLz48cmVjdCB4PSIxOSIgeT0iNSIgd2lkdGg9IjMiIGhlaWdodD0iMTMiIHJ4PSIwLjUiLz48L3N2Zz4=",
        "dark": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM5NGEzYjgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMyAzdjE4aDE4Ii8+PHJlY3QgeD0iNyIgeT0iMTIiIHdpZHRoPSIzIiBoZWlnaHQ9IjYiIHJ4PSIwLjUiLz48cmVjdCB4PSIxMyIgeT0iOCIgd2lkdGg9IjMiIGhlaWdodD0iMTAiIHJ4PSIwLjUiLz48cmVjdCB4PSIxOSIgeT0iNSIgd2lkdGg9IjMiIGhlaWdodD0iMTMiIHJ4PSIwLjUiLz48L3N2Zz4=",
        "light_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMyNTYzZWIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMyAzdjE4aDE4Ii8+PHJlY3QgeD0iNyIgeT0iMTIiIHdpZHRoPSIzIiBoZWlnaHQ9IjYiIHJ4PSIwLjUiLz48cmVjdCB4PSIxMyIgeT0iOCIgd2lkdGg9IjMiIGhlaWdodD0iMTAiIHJ4PSIwLjUiLz48cmVjdCB4PSIxOSIgeT0iNSIgd2lkdGg9IjMiIGhlaWdodD0iMTMiIHJ4PSIwLjUiLz48L3N2Zz4=",
        "dark_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2MGE1ZmEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMyAzdjE4aDE4Ii8+PHJlY3QgeD0iNyIgeT0iMTIiIHdpZHRoPSIzIiBoZWlnaHQ9IjYiIHJ4PSIwLjUiLz48cmVjdCB4PSIxMyIgeT0iOCIgd2lkdGg9IjMiIGhlaWdodD0iMTAiIHJ4PSIwLjUiLz48cmVjdCB4PSIxOSIgeT0iNSIgd2lkdGg9IjMiIGhlaWdodD0iMTMiIHJ4PSIwLjUiLz48L3N2Zz4=",
    },
    "gear": {
        "light": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIzIi8+PHBhdGggZD0iTTE5LjQgMTVhMS42NSAxLjY1IDAgMCAwIC4zMyAxLjgybC4wNi4wNmEyIDIgMCAxIDEtMi44MyAyLjgzbC0uMDYtLjA2YTEuNjUgMS42NSAwIDAgMC0xLjgyLS4zMyAxLjY1IDEuNjUgMCAwIDAtMSAxLjUxVjIxYTIgMiAwIDAgMS00IDB2LS4wOUExLjY1IDEuNjUgMCAwIDAgOSAxOS40YTEuNjUgMS42NSAwIDAgMC0xLjgyLjMzbC0uMDYuMDZhMiAyIDAgMSAxLTIuODMtMi44M2wuMDYtLjA2YTEuNjUgMS42NSAwIDAgMCAuMzMtMS44MiAxLjY1IDEuNjUgMCAwIDAtMS41MS0xSDNhMiAyIDAgMCAxIDAtNGguMDlBMS42NSAxLjY1IDAgMCAwIDQuNiA5YTEuNjUgMS42NSAwIDAgMC0uMzMtMS44MmwtLjA2LS4wNmEyIDIgMCAxIDEgMi44My0yLjgzbC4wNi4wNmExLjY1IDEuNjUgMCAwIDAgMS44Mi4zM0g5YTEuNjUgMS42NSAwIDAgMCAxLTEuNTFWM2EyIDIgMCAwIDEgNCAwdi4wOWExLjY1IDEuNjUgMCAwIDAgMSAxLjUxIDEuNjUgMS42NSAwIDAgMCAxLjgyLS4zM2wuMDYtLjA2YTIgMiAwIDEgMSAyLjgzIDIuODNsLS4wNi4wNmExLjY1IDEuNjUgMCAwIDAtLjMzIDEuODJWOWExLjY1IDEuNjUgMCAwIDAgMS41MSAxSDIxYTIgMiAwIDAgMSAwIDRoLS4wOWExLjY1IDEuNjUgMCAwIDAtMS41MSAxeiIvPjwvc3ZnPg==",
        "dark": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM5NGEzYjgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIzIi8+PHBhdGggZD0iTTE5LjQgMTVhMS42NSAxLjY1IDAgMCAwIC4zMyAxLjgybC4wNi4wNmEyIDIgMCAxIDEtMi44MyAyLjgzbC0uMDYtLjA2YTEuNjUgMS42NSAwIDAgMC0xLjgyLS4zMyAxLjY1IDEuNjUgMCAwIDAtMSAxLjUxVjIxYTIgMiAwIDAgMS00IDB2LS4wOUExLjY1IDEuNjUgMCAwIDAgOSAxOS40YTEuNjUgMS42NSAwIDAgMC0xLjgyLjMzbC0uMDYuMDZhMiAyIDAgMSAxLTIuODMtMi44M2wuMDYtLjA2YTEuNjUgMS42NSAwIDAgMCAuMzMtMS44MiAxLjY1IDEuNjUgMCAwIDAtMS41MS0xSDNhMiAyIDAgMCAxIDAtNGguMDlBMS42NSAxLjY1IDAgMCAwIDQuNiA5YTEuNjUgMS42NSAwIDAgMC0uMzMtMS44MmwtLjA2LS4wNmEyIDIgMCAxIDEgMi44My0yLjgzbC4wNi4wNmExLjY1IDEuNjUgMCAwIDAgMS44Mi4zM0g5YTEuNjUgMS42NSAwIDAgMCAxLTEuNTFWM2EyIDIgMCAwIDEgNCAwdi4wOWExLjY1IDEuNjUgMCAwIDAgMSAxLjUxIDEuNjUgMS42NSAwIDAgMCAxLjgyLS4zM2wuMDYtLjA2YTIgMiAwIDEgMSAyLjgzIDIuODNsLS4wNi4wNmExLjY1IDEuNjUgMCAwIDAtLjMzIDEuODJWOWExLjY1IDEuNjUgMCAwIDAgMS41MSAxSDIxYTIgMiAwIDAgMSAwIDRoLS4wOWExLjY1IDEuNjUgMCAwIDAtMS41MSAxeiIvPjwvc3ZnPg==",
        "light_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMyNTYzZWIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIzIi8+PHBhdGggZD0iTTE5LjQgMTVhMS42NSAxLjY1IDAgMCAwIC4zMyAxLjgybC4wNi4wNmEyIDIgMCAxIDEtMi44MyAyLjgzbC0uMDYtLjA2YTEuNjUgMS42NSAwIDAgMC0xLjgyLS4zMyAxLjY1IDEuNjUgMCAwIDAtMSAxLjUxVjIxYTIgMiAwIDAgMS00IDB2LS4wOUExLjY1IDEuNjUgMCAwIDAgOSAxOS40YTEuNjUgMS42NSAwIDAgMC0xLjgyLjMzbC0uMDYuMDZhMiAyIDAgMSAxLTIuODMtMi44M2wuMDYtLjA2YTEuNjUgMS42NSAwIDAgMCAuMzMtMS44MiAxLjY1IDEuNjUgMCAwIDAtMS41MS0xSDNhMiAyIDAgMCAxIDAtNGguMDlBMS42NSAxLjY1IDAgMCAwIDQuNiA5YTEuNjUgMS42NSAwIDAgMC0uMzMtMS44MmwtLjA2LS4wNmEyIDIgMCAxIDEgMi44My0yLjgzbC4wNi4wNmExLjY1IDEuNjUgMCAwIDAgMS44Mi4zM0g5YTEuNjUgMS42NSAwIDAgMCAxLTEuNTFWM2EyIDIgMCAwIDEgNCAwdi4wOWExLjY1IDEuNjUgMCAwIDAgMSAxLjUxIDEuNjUgMS42NSAwIDAgMCAxLjgyLS4zM2wuMDYtLjA2YTIgMiAwIDEgMSAyLjgzIDIuODNsLS4wNi4wNmExLjY1IDEuNjUgMCAwIDAtLjMzIDEuODJWOWExLjY1IDEuNjUgMCAwIDAgMS41MSAxSDIxYTIgMiAwIDAgMSAwIDRoLS4wOWExLjY1IDEuNjUgMCAwIDAtMS41MSAxeiIvPjwvc3ZnPg==",
        "dark_active": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNyIgaGVpZ2h0PSIxNyIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2MGE1ZmEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIzIi8+PHBhdGggZD0iTTE5LjQgMTVhMS42NSAxLjY1IDAgMCAwIC4zMyAxLjgybC4wNi4wNmEyIDIgMCAxIDEtMi44MyAyLjgzbC0uMDYtLjA2YTEuNjUgMS42NSAwIDAgMC0xLjgyLS4zMyAxLjY1IDEuNjUgMCAwIDAtMSAxLjUxVjIxYTIgMiAwIDAgMS00IDB2LS4wOUExLjY1IDEuNjUgMCAwIDAgOSAxOS40YTEuNjUgMS42NSAwIDAgMC0xLjgyLjMzbC0uMDYuMDZhMiAyIDAgMSAxLTIuODMtMi44M2wuMDYtLjA2YTEuNjUgMS42NSAwIDAgMCAuMzMtMS44MiAxLjY1IDEuNjUgMCAwIDAtMS41MS0xSDNhMiAyIDAgMCAxIDAtNGguMDlBMS42NSAxLjY1IDAgMCAwIDQuNiA5YTEuNjUgMS42NSAwIDAgMC0uMzMtMS44MmwtLjA2LS4wNmEyIDIgMCAxIDEgMi44My0yLjgzbC4wNi4wNmExLjY1IDEuNjUgMCAwIDAgMS44Mi4zM0g5YTEuNjUgMS42NSAwIDAgMCAxLTEuNTFWM2EyIDIgMCAwIDEgNCAwdi4wOWExLjY1IDEuNjUgMCAwIDAgMSAxLjUxIDEuNjUgMS42NSAwIDAgMCAxLjgyLS4zM2wuMDYtLjA2YTIgMiAwIDEgMSAyLjgzIDIuODNsLS4wNi4wNmExLjY1IDEuNjUgMCAwIDAtLjMzIDEuODJWOWExLjY1IDEuNjUgMCAwIDAgMS41MSAxSDIxYTIgMiAwIDAgMSAwIDRoLS4wOWExLjY1IDEuNjUgMCAwIDAtMS41MSAxeiIvPjwvc3ZnPg==",
    },
}

# label -> icon key. Icons are attached to buttons by matching the button's
# visible text at runtime (see inject_nav_icons below), not by DOM position,
# so this keeps working no matter how Streamlit nests/wraps button elements.
NAV_ITEMS = [
    ("Dashboard", "dashboard"),
    ("Resume Upload", "file"),
    ("Candidates", "users"),
    ("Job Postings", "briefcase"),
    ("Analytics", "barchart"),
    ("Settings", "gear"),
]


def inject_nav_icons(theme: str) -> None:
    """Attach the flat SVG icons to sidebar nav buttons by matching each
    button's visible label text (robust across Streamlit versions/DOM
    changes, unlike nth-of-type CSS selectors)."""
    mode = "dark" if theme == "dark" else "light"
    icon_map = {
        label: {
            "normal": ICONS[key][mode],
            "active": ICONS[key][mode + "_active"],
        }
        for label, key in NAV_ITEMS
    }
    js_map = json.dumps(icon_map)
    widget_html = f"""
    <script>
    (function() {{
        const iconMap = {js_map};
        function applyIcons() {{
            try {{
                const doc = window.parent.document;
                const buttons = doc.querySelectorAll('section[data-testid="stSidebar"] button');
                buttons.forEach(function(btn) {{
                    const label = (btn.innerText || "").trim();
                    if (iconMap[label]) {{
                        const isActive = btn.getAttribute('kind') === 'primary';
                        const src = 'data:image/svg+xml;base64,' + (isActive ? iconMap[label].active : iconMap[label].normal);
                        let img = btn.querySelector('img.nav-icon-injected');
                        if (!img) {{
                            img = doc.createElement('img');
                            img.className = 'nav-icon-injected';
                            img.style.width = '17px';
                            img.style.height = '17px';
                            img.style.flexShrink = '0';
                            btn.insertBefore(img, btn.firstChild);
                        }}
                        if (img.getAttribute('src') !== src) {{
                            img.setAttribute('src', src);
                        }}
                    }}
                }});
            }} catch (e) {{ /* no-op */ }}
        }}
        applyIcons();
        try {{
            const observer = new MutationObserver(applyIcons);
            observer.observe(window.parent.document.body, {{ childList: true, subtree: true, attributes: true }});
        }} catch (e) {{ /* no-op */ }}
        setInterval(applyIcons, 400);
    }})();
    </script>
    """
    components.html(widget_html, height=0)


def inject_theme_toggle_style() -> None:
    """Style the sun/moon theme-toggle buttons as small circular icon
    buttons wherever they appear (header + settings page), matched by their
    visible glyph rather than DOM position so it survives reruns."""
    widget_html = """
    <script>
    (function() {
        function styleToggles() {
            try {
                const doc = window.parent.document;
                const buttons = doc.querySelectorAll('button');
                buttons.forEach(function(btn) {
                    const label = (btn.innerText || "").trim();
                    if (label === "☀️" || label === "🌙") {
                        btn.style.width = "42px";
                        btn.style.height = "42px";
                        btn.style.minHeight = "42px";
                        btn.style.borderRadius = "50%";
                        btn.style.padding = "0";
                        btn.style.display = "flex";
                        btn.style.alignItems = "center";
                        btn.style.justifyContent = "center";
                        btn.style.fontSize = "1.15rem";
                        btn.style.lineHeight = "1";
                        btn.style.border = "1px solid rgba(148,163,184,0.35)";
                        btn.style.background = label === "☀️" ? "#fff7ed" : "#1e293b";
                        btn.style.boxShadow = "0 2px 6px rgba(15,23,42,0.12)";
                    }
                });
            } catch (e) { /* no-op */ }
        }
        styleToggles();
        try {
            const observer = new MutationObserver(styleToggles);
            observer.observe(window.parent.document.body, { childList: true, subtree: true, attributes: true });
        } catch (e) { /* no-op */ }
        setInterval(styleToggles, 400);
    })();
    </script>
    """
    components.html(widget_html, height=0)


def inject_sidebar_flatten_style(theme: str) -> None:
    """Belt-and-suspenders fix for the sidebar nav: strip any card-like box
    (border/radius/shadow/background) around the sidebar's own layout
    wrappers - only the dashboard's real content cards should have boxes -
    and force a single, consistent, theme-correct text color on every nav
    label. Uses inline-style overrides since some default chrome can come
    from styles with high specificity that plain CSS can't beat."""
    muted = "#94a3b8" if theme == "dark" else "#475569"
    active_color = "#93c5fd" if theme == "dark" else "#2563eb"
    widget_html = f"""
    <script>
    (function() {{
        const MUTED = "{muted}";
        const ACTIVE = "{active_color}";
        function flattenSidebar() {{
            try {{
                const doc = window.parent.document;
                const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
                if (!sidebar) return;

                sidebar.querySelectorAll('div').forEach(function(el) {{
                    el.style.boxShadow = 'none';
                    el.style.border = 'none';
                    el.style.borderRadius = '0px';
                    const testid = el.getAttribute('data-testid') || '';
                    if (testid.indexOf('VerticalBlock') !== -1) {{
                        el.style.background = 'transparent';
                        el.style.margin = '0px';
                        el.style.padding = '0px';
                    }}
                }});

                sidebar.querySelectorAll('button').forEach(function(btn) {{
                    const isActive = btn.getAttribute('kind') === 'primary';
                    const color = isActive ? ACTIVE : MUTED;
                    btn.style.color = color;
                    btn.style.textDecoration = 'none';
                    btn.querySelectorAll('*').forEach(function(child) {{
                        child.style.color = color;
                        child.style.textDecoration = 'none';
                    }});
                }});
            }} catch (e) {{ /* no-op */ }}
        }}
        flattenSidebar();
        try {{
            const observer = new MutationObserver(flattenSidebar);
            observer.observe(window.parent.document.body, {{ childList: true, subtree: true, attributes: true }});
        }} catch (e) {{ /* no-op */ }}
        setInterval(flattenSidebar, 400);
    }})();
    </script>
    """
    components.html(widget_html, height=0)


def inject_card_style(theme: str) -> None:
    """Force every 'card' section (identified by its exact visible <h3>
    title, the same reliable text-matching technique the nav-icon and
    theme-toggle injectors above already use) to render as a visible box:
    background, border, rounded corners, soft shadow, padding.

    This intentionally does NOT depend on Streamlit's border=True container
    feature or its internal data-testid at all (that approach silently
    failed to match in some environments/versions). Instead it finds the
    <h3> by its text, then walks up to the nearest ancestor block
    (data-testid="stVerticalBlock" - the single most stable, universal
    Streamlit container marker) and boxes that."""
    dark = theme == "dark"
    card_bg = "#111827" if dark else "#ffffff"
    border_col = "#334155" if dark else "#e2e8f0"
    shadow = (
        "0 1px 3px rgba(15,23,42,0.35), 0 1px 2px rgba(15,23,42,0.3)"
        if dark
        else "0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04)"
    )
    card_titles = [
        "Upload Resume",
        "Parsing Progress",
        "Recently Processed Candidates",
        "Resume Processing Overview",
        "Top Skills Extracted",
        "Recent Activity",
        "Recent Candidates",
        "Profile Completeness Distribution",
    ]
    titles_json = json.dumps(card_titles)
    widget_html = f"""
    <script>
    (function() {{
        const CARD_BG = "{card_bg}";
        const BORDER = "1px solid {border_col}";
        const SHADOW = "{shadow}";
        const TITLES = {titles_json};
        function styleCards() {{
            try {{
                const doc = window.parent.document;
                doc.querySelectorAll('h3').forEach(function(h) {{
                    const text = (h.textContent || "").trim();
                    if (TITLES.indexOf(text) === -1) return;
                    if (h.closest('section[data-testid="stSidebar"]')) return;
                    const block = h.closest('div[data-testid="stVerticalBlock"]');
                    if (!block) return;
                    block.style.setProperty('background', CARD_BG, 'important');
                    block.style.setProperty('border', BORDER, 'important');
                    block.style.setProperty('border-radius', '14px', 'important');
                    block.style.setProperty('padding', '1.25rem 1.4rem', 'important');
                    block.style.setProperty('box-shadow', SHADOW, 'important');
                    block.style.setProperty('box-sizing', 'border-box', 'important');
                    block.style.setProperty('overflow', 'hidden', 'important');
                    block.style.setProperty('position', 'relative', 'important');
                }});
            }} catch (e) {{ /* no-op */ }}
        }}
        styleCards();
        try {{
            const observer = new MutationObserver(styleCards);
            observer.observe(window.parent.document.body, {{ childList: true, subtree: true, attributes: true }});
        }} catch (e) {{ /* no-op */ }}
        setInterval(styleCards, 400);
    }})();
    </script>
    """
    components.html(widget_html, height=0)


def inject_uploader_style(theme: str) -> None:
    """Restyle the REAL native st.file_uploader dropzone (icon + copy) to
    match the target design, instead of layering a second fake dropzone on
    top of it. This keeps native drag-and-drop fully working while giving
    full control over the look. Matches on stable data-testid attributes
    (not text or DOM position), so it survives Streamlit version changes."""
    accent = "#3b82f6" if theme == "dark" else "#2563eb"
    widget_html = f"""
    <script>
    (function() {{
        const ACCENT = "{accent}";
        function styleDropzones() {{
            try {{
                const doc = window.parent.document;
                const dropzones = doc.querySelectorAll('section[data-testid="stFileUploaderDropzone"]');
                dropzones.forEach(function(zone) {{
                    if (zone.dataset.recruitmentStyled === "1") return;
                    zone.dataset.recruitmentStyled = "1";

                    const instructions = zone.querySelector('div[data-testid="stFileUploaderDropzoneInstructions"]');
                    if (instructions) {{
                        const svg = instructions.querySelector('svg');
                        if (svg) svg.style.display = 'none';

                        if (!instructions.querySelector('.custom-upload-icon')) {{
                            const badge = doc.createElement('div');
                            badge.className = 'custom-upload-icon';
                            badge.style.width = '48px';
                            badge.style.height = '48px';
                            badge.style.borderRadius = '50%';
                            badge.style.display = 'flex';
                            badge.style.alignItems = 'center';
                            badge.style.justifyContent = 'center';
                            badge.style.margin = '0 auto 0.85rem';
                            badge.style.background = 'linear-gradient(135deg,' + ACCENT + ',#60a5fa)';
                            badge.style.color = '#fff';
                            badge.style.fontSize = '1.4rem';
                            badge.textContent = '\\u2191';
                            instructions.insertBefore(badge, instructions.firstChild);
                        }}

                        const span = instructions.querySelector('span');
                        if (span) span.textContent = 'Drag and drop resumes or click to browse';
                        const small = instructions.querySelector('small');
                        if (small) small.textContent = 'Supported formats: PDF, DOCX';
                    }}

                    const browseBtn = zone.querySelector('button');
                    if (browseBtn) {{
                        browseBtn.style.background = ACCENT;
                        browseBtn.style.color = '#fff';
                        browseBtn.style.border = 'none';
                        browseBtn.style.borderRadius = '8px';
                        browseBtn.style.fontWeight = '600';
                    }}
                }});
            }} catch (e) {{ /* no-op */ }}
        }}
        styleDropzones();
        try {{
            const observer = new MutationObserver(styleDropzones);
            observer.observe(window.parent.document.body, {{ childList: true, subtree: true }});
        }} catch (e) {{ /* no-op */ }}
        setInterval(styleDropzones, 400);
    }})();
    </script>
    """
    components.html(widget_html, height=0)


def inject_hide_chart_toolbar() -> None:
    """Hide Streamlit's own built-in 'View fullscreen' toolbar BUTTON that
    appears on hover in the top-right corner of charts/dataframes/images in
    recent Streamlit versions. Matches by the button's title/aria-label text
    (robust across Streamlit versions, since the data-testid names for this
    have changed release to release) - the same text-matching technique used
    by inject_nav_icons/inject_card_style above.

    IMPORTANT: this only ever hides the matched button element itself
    (opacity/pointer-events, not display:none on any ancestor). An earlier
    version of this walked up to the nearest '[data-testid="stElementToolbar"]'
    or fell back to '.parentElement' and hid that instead - in some
    Streamlit versions that wrapping element also contains the chart's own
    render target, so the whole chart disappeared along with the button.
    Never repeat that mistake: only touch the button node."""
    widget_html = """
    <script>
    (function() {
        function hideToolbarButtons() {
            try {
                const doc = window.parent.document;
                doc.querySelectorAll('button, [role="button"]').forEach(function(btn) {
                    const label = ((btn.getAttribute('title') || '') + ' ' + (btn.getAttribute('aria-label') || '')).toLowerCase();
                    if (label.indexOf('fullscreen') !== -1) {
                        btn.style.setProperty('display', 'none', 'important');
                    }
                });
            } catch (e) { /* no-op */ }
        }
        hideToolbarButtons();
        try {
            const observer = new MutationObserver(hideToolbarButtons);
            observer.observe(window.parent.document.body, { childList: true, subtree: true, attributes: true });
        } catch (e) { /* no-op */ }
        setInterval(hideToolbarButtons, 400);
    })();
    </script>
    """
    components.html(widget_html, height=0)


def set_theme(theme: str) -> None:
    st.session_state["theme"] = theme


DARK_CSS = """
<style>
.stApp { background: #0b1120; color: #e2e8f0; }
.block-container { background: #0b1120; color: #e2e8f0; padding: 1.5rem 1.5rem 2rem 1.5rem; }
section[data-testid="stSidebar"] { background: #111827; color: #f8fafc; padding-top: 1rem; border-right: 1px solid #1f2937; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #f8fafc !important; }
.stApp p, .stApp span, .stApp div { color: #e2e8f0 !important; }
div[data-testid="stAppViewContainer"] .stButton>button { background-color: #2563eb; color: white; border-radius: 10px; border: none; }
div[data-testid="stAppViewContainer"] .stButton>button:hover { background-color: #1d4ed8; }
div[data-testid="stAppViewContainer"] .stButton>button:disabled { background-color: #334155; color: #64748b; }
div[data-testid="stForm"] div[data-testid="InputInstructions"] { display: none !important; }
div[data-testid="stFormSubmitButton"] > button { background: #2563eb !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important; }
div[data-testid="stFormSubmitButton"] > button:hover { background: #1d4ed8 !important; }
div[data-testid="stFormSubmitButton"] > button p,
div[data-testid="stFormSubmitButton"] > button span,
div[data-testid="stFormSubmitButton"] > button div { color: #ffffff !important; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #111827; color: #e2e8f0; caret-color: #ffffff; border: 1px solid #334155; }
.stSelectbox>div>div>div { background-color: #111827; color: #e2e8f0; }

.sidebar-brand { display:flex; align-items:center; gap:0.6rem; padding: 0.25rem 1rem 1rem 1rem; }
.sidebar-brand .logo-badge {
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg,#6366f1,#2563eb);
    color: #fff; display:flex; align-items:center; justify-content:center;
    font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
}
.sidebar-brand h2 { margin:0; font-size: 1.1rem; font-weight: 700; color:#f8fafc !important; }

/* Flat nav rows built from st.button, no native widget chrome */
section[data-testid="stSidebar"] div[data-testid="stButton"] { margin-bottom: 0.15rem; }
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    display: flex; align-items: center; gap: 0.65rem;
    width: 100%; justify-content: flex-start;
    padding: 0.55rem 0.75rem; border-radius: 8px;
    font-size: 0.95rem; font-weight: 500; text-align: left;
    background: transparent !important; border: none !important;
    color: #cbd5e1 !important; box-shadow: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
    color: inherit !important; margin: 0; font-weight: inherit;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button img.nav-icon-injected {
    margin-right: 0.55rem;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover { background: #1f2937 !important; }
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
    background: #1e3a8a !important; color: #93c5fd !important; font-weight: 600;
}

.candidate-card, .upload-card, .metrics-card, .summary-box, .upload-panel, .progress-card, .recent-panel { background: #111827; border: 1px solid #334155; border-radius: 18px; padding: 1.25rem; }
.candidate-card h3, .upload-card h3, .metrics-card h3, .upload-panel h3, .progress-card h3, .recent-panel h3 { color: #f8fafc; margin-top:0; }
.candidate-list-table { width: 100%; border-collapse: collapse; margin-top: 1rem; overflow: hidden; border-radius: 20px; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08); background: #111827; }
.candidate-list-table th, .candidate-list-table td { padding: 1rem 1.1rem; text-align: left; }
.candidate-list-table th { background: #111827; color: #e2e8f0; font-weight: 700; border-bottom: 1px solid #1f2937; }
.candidate-list-table tr { border-bottom: 1px solid #1f2937; }
.candidate-list-table tr:last-child { border-bottom: none; }
.candidate-link { color: #60a5fa; font-weight: 600; text-decoration: none; }
.candidate-link:hover { text-decoration: underline; }
.download-link { display: inline-flex; align-items: center; justify-content: center; padding: 0.4rem 0.85rem; border-radius: 999px; background: #eff6ff; color: #1d4ed8; font-size: 0.95rem; text-decoration: none; }
.detail-panel { background: #111827; border: 1px solid #1f2937; border-radius: 22px; padding: 1.5rem; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.35); margin-top: 1rem; }
.detail-panel h2 { margin: 0; font-size: 2rem; color: #f8fafc; }
.detail-panel .detail-meta { color: #94a3b8; margin-top: 0.35rem; }
.detail-panel .detail-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem; }
.detail-panel .detail-actions a { display: inline-flex; align-items: center; justify-content: center; padding: 0.85rem 1.1rem; border-radius: 999px; text-decoration: none; font-weight: 600; }
.detail-panel .back-button { background: #2563eb; color: white; }
.detail-panel .download-button { background: #1e3a8a; color: #eff6ff; }
.resume-text-panel { margin-top: 1.5rem; }
.resume-text-panel pre { white-space: pre-wrap; word-break: break-word; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #e2e8f0; line-height: 1.7; font-size: 0.95rem; }
/* Native file uploader, restyled to match the design (no fake duplicate dropzone) */
section[data-testid="stFileUploaderDropzone"] {
    background: #0f172a !important;
    border: 2px dashed #334155 !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
}
section[data-testid="stFileUploaderDropzone"]:hover { border-color: #60a5fa !important; background: #111827 !important; }
div[data-testid="stFileUploaderDropzoneInstructions"] { text-align: center !important; width: 100%; }
div[data-testid="stFileUploaderDropzoneInstructions"] span { color: #f8fafc !important; font-weight: 600; font-size: 1.05rem; }
div[data-testid="stFileUploaderDropzoneInstructions"] small { color: #94a3b8 !important; }
div[data-testid="stFileUploader"] section > button { margin-top: 0.85rem; }
div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] { display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }

.upload-file-card { display: flex; align-items: center; justify-content: space-between; background: #111827; border: 1px solid #334155; border-radius: 16px; padding: 1rem 1rem; margin-top: 1rem; }
.upload-file-card span { color: #e2e8f0 !important; font-weight: 600; }
.upload-file-card .file-status { color: #38bdf8 !important; font-weight: 600; }
.progress-bar { width: 100%; height: 0.9rem; background: #1f2937; border-radius: 999px; overflow: hidden; margin: 0.6rem 0 1.25rem; }
.progress-bar-fill { height: 100%; background: #22c55e; border-radius: 999px; width: 0%; transition: width 0.4s ease; }
.progress-heading-row { display: flex; justify-content: space-between; align-items: baseline; }
.progress-heading-row span:first-child { color: #cbd5e1 !important; font-weight: 600; }
.progress-heading-row span:last-child { color: #4ade80 !important; font-weight: 700; }
.metric-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.9rem; margin-top: 1rem; }
.metric-card { background: #0f172a; border: 1px solid #334155; border-radius: 16px; padding: 1rem; }
.metric-card h4 { margin: 0; font-size: 0.85rem; color: #94a3b8 !important; font-weight: 600; }
.metric-card p { margin: 0.55rem 0 0; font-size: 1.7rem; font-weight: 700; color: #f8fafc !important; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem 1.5rem; margin-top: 1.1rem; }
.detail-row { color: #dbeafe !important; }
.detail-label { color: #94a3b8 !important; font-weight: 600; display:block; font-size:0.85rem; }
.detail-value { color: #f1f5f9 !important; font-weight: 500; }
.tag-pill { display: inline-flex; align-items: center; margin: 0 0.35rem 0.35rem 0; padding: 0.35rem 0.75rem; border-radius: 999px; background: #1f2937; color: #cbd5e1 !important; font-size: 0.82rem; }
.recent-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.recent-table th, .recent-table td { padding: 0.88rem 0.9rem; text-align: left; color: #e2e8f0 !important; }
.recent-table th { color: #cbd5e1 !important; font-weight: 700; background: #0f172a; }
.recent-table tr { border-bottom: 1px solid #334155; }
.recent-table tr:last-child { border-bottom: none; }
.status-processed { color: #4ade80 !important; font-weight: 600; }
header, footer, #MainMenu { visibility: hidden !important; height: 0px !important; margin: 0 !important; padding: 0 !important; }

div[data-testid="stDownloadButton"] button {
    background: #2563eb !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.9rem !important;
    border: none !important;
    font-weight: 600 !important;
}
div[data-testid="stDownloadButton"] button:hover { background: #1d4ed8 !important; }
div[data-testid="stDownloadButton"] button p,
div[data-testid="stDownloadButton"] button span,
div[data-testid="stDownloadButton"] button div {
    color: #ffffff !important;
}

.detail-action-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.detail-action-row div[data-testid="stButton"] { margin-bottom: 0 !important; }
.detail-action-row div[data-testid="stButton"] button {
    background: #1f2937 !important; color: #e2e8f0 !important;
    border: 1px solid #334155 !important; border-radius: 8px !important;
    font-weight: 600 !important; padding: 0.5rem 1rem !important;
}
.detail-action-row div[data-testid="stButton"] button:hover { background: #334155 !important; }
.detail-action-row div[data-testid="stButton"] button p,
.detail-action-row div[data-testid="stButton"] button span {
    color: inherit !important;
}
.download-button-link {
    display: inline-flex; align-items: center; justify-content: center;
    background: #2563eb; color: #ffffff !important; text-decoration: none;
    border-radius: 8px; font-weight: 600; padding: 0.55rem 1.1rem;
    font-size: 0.95rem; height: 2.5rem; box-sizing: border-box;
}
.download-button-link:hover { background: #1d4ed8; }
.resume-section-header {
    color: #93c5fd !important; margin: 1.25rem 0 0.5rem 0; font-size: 1.05rem;
    font-weight: 700; border-bottom: 1px solid #334155; padding-bottom: 0.35rem;
}
.resume-line { color: #e2e8f0 !important; margin: 0.35rem 0; line-height: 1.65; font-size: 0.95rem; }
.resume-bullet { color: #e2e8f0 !important; margin: 0.3rem 0 0.3rem 1rem; line-height: 1.6; font-size: 0.95rem; }

.candidate-row-header { display: grid; grid-template-columns: 1.2fr 1.4fr 0.9fr 0.7fr 1.5fr 0.8fr; gap: 0.5rem; padding: 0.85rem 1.1rem; background: #111827; border: 1px solid #1f2937; border-radius: 16px 16px 0 0; font-weight: 700; color: #e2e8f0 !important; margin-top: 1rem; }
.candidate-row { background: #111827; border-left: 1px solid #1f2937; border-right: 1px solid #1f2937; border-bottom: 1px solid #1f2937; padding: 0.35rem 1.1rem; display: flex; align-items: center; }
.candidate-row:last-child { border-radius: 0 0 16px 16px; }
.candidate-row-cell { color: #e2e8f0 !important; padding: 0.55rem 0; }

.resume-download-cell div[data-testid="stDownloadButton"] button {
    padding: 0.3rem 0.75rem !important;
    font-size: 0.85rem !important;
    border-radius: 999px !important;
    background: #1e3a8a !important;
}
</style>
"""

LIGHT_CSS = """
<style>
.stApp { background: linear-gradient(135deg, #eef2ff 0%, #ffffff 100%); color: #0f172a; }
.block-container { background: #ffffff; color: #0f172a; padding: 1.5rem 1.5rem 2rem 1.5rem; }
section[data-testid="stSidebar"] { background: #ffffff; color: #0f172a; padding-top: 1rem; border-right: 1px solid #e2e8f0; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #0f172a !important; }
.stApp p, .stApp span, .stApp div { color: #0f172a !important; }
div[data-testid="stAppViewContainer"] .stButton>button { background-color: #2563eb; color: white; border-radius: 10px; border: none; }
div[data-testid="stAppViewContainer"] .stButton>button:hover { background-color: #1d4ed8; }
div[data-testid="stAppViewContainer"] .stButton>button:disabled { background-color: #e2e8f0; color: #94a3b8; }
div[data-testid="stForm"] div[data-testid="InputInstructions"] { display: none !important; }
div[data-testid="stFormSubmitButton"] > button { background: #2563eb !important; color: #ffffff !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important; }
div[data-testid="stFormSubmitButton"] > button:hover { background: #1d4ed8 !important; }
div[data-testid="stFormSubmitButton"] > button p,
div[data-testid="stFormSubmitButton"] > button span,
div[data-testid="stFormSubmitButton"] > button div { color: #ffffff !important; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #f8fafc; color: #0f172a; caret-color: #0f172a; border: 1px solid #cbd5e1; }
.stSelectbox>div>div>div { background-color: #f8fafc; color: #0f172a; }

.sidebar-brand { display:flex; align-items:center; gap:0.6rem; padding: 0.25rem 1rem 1rem 1rem; }
.sidebar-brand .logo-badge {
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg,#6366f1,#2563eb);
    color: #fff; display:flex; align-items:center; justify-content:center;
    font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
}
.sidebar-brand h2 { margin:0; font-size: 1.1rem; font-weight: 700; color:#0f172a !important; }

section[data-testid="stSidebar"] div[data-testid="stButton"] { margin-bottom: 0.15rem; }
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    display: flex; align-items: center; gap: 0.65rem;
    width: 100%; justify-content: flex-start;
    padding: 0.55rem 0.75rem; border-radius: 8px;
    font-size: 0.95rem; font-weight: 500; text-align: left;
    background: transparent !important; border: none !important;
    color: #475569 !important; box-shadow: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
    color: inherit !important; margin: 0; font-weight: inherit;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button img.nav-icon-injected {
    margin-right: 0.55rem;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover { background: #f1f5f9 !important; }
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
    background: #eff6ff !important; color: #2563eb !important; font-weight: 600;
}

.candidate-card, .upload-card, .metrics-card, .summary-box, .upload-panel, .progress-card, .recent-panel { background: #f8fafc; border: 1px solid #d1d5db; border-radius: 18px; padding: 1.25rem; }
.candidate-card h3, .upload-card h3, .metrics-card h3, .upload-panel h3, .progress-card h3, .recent-panel h3 { color: #0f172a; margin-top:0; }
.candidate-list-table { width: 100%; border-collapse: collapse; margin-top: 1rem; overflow: hidden; border-radius: 20px; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08); background: #ffffff; }
.candidate-list-table th, .candidate-list-table td { padding: 1rem 1.1rem; text-align: left; }
.candidate-list-table th { background: #f8fafc; color: #0f172a; font-weight: 700; border-bottom: 1px solid #e2e8f0; }
.candidate-list-table tr { border-bottom: 1px solid #e2e8f0; }
.candidate-list-table tr:last-child { border-bottom: none; }
.candidate-link { color: #2563eb; font-weight: 600; text-decoration: none; }
.candidate-link:hover { text-decoration: underline; }
.download-link { display: inline-flex; align-items: center; justify-content: center; padding: 0.4rem 0.85rem; border-radius: 999px; background: #eff6ff; color: #1d4ed8; font-size: 0.95rem; text-decoration: none; }
.detail-panel { background: #ffffff; border: 1px solid #d1d5db; border-radius: 22px; padding: 1.5rem; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12); margin-top: 1rem; }
.detail-panel h2 { margin: 0; font-size: 2rem; color: #0f172a; }
.detail-panel .detail-meta { color: #64748b; margin-top: 0.35rem; }
.detail-panel .detail-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem; }
.detail-panel .detail-actions a { display: inline-flex; align-items: center; justify-content: center; padding: 0.85rem 1.1rem; border-radius: 999px; text-decoration: none; font-weight: 600; }
.detail-panel .back-button { background: #2563eb; color: white; }
.detail-panel .download-button { background: #1d4ed8; color: #eff6ff; }
.resume-text-panel { margin-top: 1.5rem; }
.resume-text-panel pre { white-space: pre-wrap; word-break: break-word; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #0f172a; line-height: 1.7; font-size: 0.95rem; }

section[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 16px !important;
    padding: 1.25rem !important;
}
section[data-testid="stFileUploaderDropzone"]:hover { border-color: #60a5fa !important; background: #eff6ff !important; }
div[data-testid="stFileUploaderDropzoneInstructions"] { text-align: center !important; width: 100%; }
div[data-testid="stFileUploaderDropzoneInstructions"] span { color: #1d4ed8 !important; font-weight: 600; font-size: 1.05rem; }
div[data-testid="stFileUploaderDropzoneInstructions"] small { color: #64748b !important; }
div[data-testid="stFileUploader"] section > button { margin-top: 0.85rem; }
div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] { display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }

.upload-file-card { display: flex; align-items: center; justify-content: space-between; background: #ffffff; border: 1px solid #d1d5db; border-radius: 16px; padding: 1rem 1rem; margin-top: 1rem; }
.upload-file-card span { color: #0f172a !important; font-weight: 600; }
.upload-file-card .file-status { color: #2563eb !important; font-weight: 600; }
.progress-bar { width: 100%; height: 0.9rem; background: #e2e8f0; border-radius: 999px; overflow: hidden; margin: 0.6rem 0 1.25rem; }
.progress-bar-fill { height: 100%; background: #22c55e; border-radius: 999px; width: 0%; transition: width 0.4s ease; }
.progress-heading-row { display: flex; justify-content: space-between; align-items: baseline; }
.progress-heading-row span:first-child { color: #334155 !important; font-weight: 600; }
.progress-heading-row span:last-child { color: #16a34a !important; font-weight: 700; }
.metric-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.9rem; margin-top: 1rem; }
.metric-card { background: #ffffff; border: 1px solid #d1d5db; border-radius: 16px; padding: 1rem; }
.metric-card h4 { margin: 0; font-size: 0.85rem; color: #64748b !important; font-weight: 600; }
.metric-card p { margin: 0.55rem 0 0; font-size: 1.7rem; font-weight: 700; color: #0f172a !important; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem 1.5rem; margin-top: 1.1rem; }
.detail-row { color: #334155 !important; }
.detail-label { color: #64748b !important; font-weight: 600; display:block; font-size:0.85rem; }
.detail-value { color: #0f172a !important; font-weight: 500; }
.tag-pill { display: inline-flex; align-items: center; margin: 0 0.35rem 0.35rem 0; padding: 0.35rem 0.75rem; border-radius: 999px; background: #e2e8f0; color: #0f172a !important; font-size: 0.82rem; }
.recent-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.recent-table th, .recent-table td { padding: 0.88rem 0.9rem; text-align: left; color: #0f172a !important; }
.recent-table th { color: #475569 !important; font-weight: 700; background: #f8fafc; }
.recent-table tr { border-bottom: 1px solid #e2e8f0; }
.recent-table tr:last-child { border-bottom: none; }
.status-processed { color: #16a34a !important; font-weight: 600; }
header, footer, #MainMenu { visibility: hidden !important; height: 0px !important; margin: 0 !important; padding: 0 !important; }

div[data-testid="stDownloadButton"] button {
    background: #2563eb !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.9rem !important;
    border: none !important;
    font-weight: 600 !important;
}
div[data-testid="stDownloadButton"] button:hover { background: #1d4ed8 !important; }
div[data-testid="stDownloadButton"] button p,
div[data-testid="stDownloadButton"] button span,
div[data-testid="stDownloadButton"] button div {
    color: #ffffff !important;
}

.detail-action-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.detail-action-row div[data-testid="stButton"] { margin-bottom: 0 !important; }
.detail-action-row div[data-testid="stButton"] button {
    background: #f1f5f9 !important; color: #0f172a !important;
    border: 1px solid #d1d5db !important; border-radius: 8px !important;
    font-weight: 600 !important; padding: 0.5rem 1rem !important;
}
.detail-action-row div[data-testid="stButton"] button:hover { background: #e2e8f0 !important; }
.detail-action-row div[data-testid="stButton"] button p,
.detail-action-row div[data-testid="stButton"] button span {
    color: inherit !important;
}
.download-button-link {
    display: inline-flex; align-items: center; justify-content: center;
    background: #2563eb; color: #ffffff !important; text-decoration: none;
    border-radius: 8px; font-weight: 600; padding: 0.55rem 1.1rem;
    font-size: 0.95rem; height: 2.5rem; box-sizing: border-box;
}
.download-button-link:hover { background: #1d4ed8; }
.resume-section-header {
    color: #1d4ed8 !important; margin: 1.25rem 0 0.5rem 0; font-size: 1.05rem;
    font-weight: 700; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.35rem;
}
.resume-line { color: #0f172a !important; margin: 0.35rem 0; line-height: 1.65; font-size: 0.95rem; }
.resume-bullet { color: #0f172a !important; margin: 0.3rem 0 0.3rem 1rem; line-height: 1.6; font-size: 0.95rem; }

.candidate-row-header { display: grid; grid-template-columns: 1.2fr 1.4fr 0.9fr 0.7fr 1.5fr 0.8fr; gap: 0.5rem; padding: 0.85rem 1.1rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px 16px 0 0; font-weight: 700; color: #0f172a !important; margin-top: 1rem; }
.candidate-row { background: #ffffff; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; padding: 0.35rem 1.1rem; display: flex; align-items: center; }
.candidate-row:last-child { border-radius: 0 0 16px 16px; }
.candidate-row-cell { color: #0f172a !important; padding: 0.55rem 0; }

.resume-download-cell div[data-testid="stDownloadButton"] button {
    padding: 0.3rem 0.75rem !important;
    font-size: 0.85rem !important;
    border-radius: 999px !important;
    background: #eff6ff !important;
    color: #1d4ed8 !important;
}
.resume-download-cell div[data-testid="stDownloadButton"] button p,
.resume-download-cell div[data-testid="stDownloadButton"] button span {
    color: #1d4ed8 !important;
}
</style>
"""


def get_theme_css(theme: str) -> str:
    return DARK_CSS if theme == "dark" else LIGHT_CSS


def greeting_text() -> str:
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def api_call(method: str, path: str, payload: dict[str, Any] | None = None, files: dict[str, Any] | None = None) -> requests.Response:
    if method == "get":
        return requests.get(f"{BACKEND_URL}{path}", timeout=20)
    if method == "post":
        if files:
            return requests.post(f"{BACKEND_URL}{path}", files=files, timeout=60)
        return requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=20)
    if method == "put":
        return requests.put(f"{BACKEND_URL}{path}", json=payload, timeout=20)
    if method == "delete":
        return requests.delete(f"{BACKEND_URL}{path}", timeout=20)
    raise ValueError("Unsupported method")


def fetch_resume_file(candidate_id: str) -> tuple[bytes, str, str] | None:
    """Fetch the raw resume file bytes from the backend so downloads work
    entirely through Streamlit's own server-side request - the browser
    never needs to reach BACKEND_URL directly."""
    if not candidate_id:
        return None
    try:
        resp = requests.get(f"{BACKEND_URL}/public/candidate/{candidate_id}/resume", timeout=20)
    except requests.RequestException:
        return None
    if not resp.ok:
        return None
    content_type = resp.headers.get("Content-Type", "application/octet-stream")
    disposition = resp.headers.get("Content-Disposition", "")
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', disposition)
    filename = match.group(1) if match else f"resume_{candidate_id}"
    return resp.content, filename, content_type


def get_cached_resume_file(candidate_id: str) -> tuple[bytes, str, str] | None:
    """Session-scoped cache so we don't re-fetch the same resume bytes on
    every rerun (Streamlit reruns the whole script on every interaction)."""
    if not candidate_id:
        return None
    cache = st.session_state.setdefault("resume_cache", {})
    if candidate_id not in cache:
        cache[candidate_id] = fetch_resume_file(candidate_id)
    return cache[candidate_id]


def normalize_skill_values(skills: Any) -> list[str]:
    if not skills:
        return []
    if isinstance(skills, str):
        return [item.strip() for item in re.split(r"[,;\n]+", skills) if item.strip()]
    if isinstance(skills, dict):
        values: list[str] = []
        for key, value in skills.items():
            if isinstance(value, str):
                values.extend([item.strip() for item in re.split(r"[,;\n]+", value) if item.strip()])
            elif isinstance(value, list):
                values.extend(normalize_skill_values(value))
            elif value:
                values.append(str(value))
        return values
    if isinstance(skills, list):
        result: list[str] = []
        for item in skills:
            if isinstance(item, str):
                result.extend([s.strip() for s in re.split(r"[,;\n]+", item) if s.strip()])
            elif isinstance(item, dict):
                result.extend(normalize_skill_values(item.get("skill_name") or item.get("name") or item))
            elif item:
                result.append(str(item))
        return result
    return [str(skills)]


def format_skills(skills: Any) -> str:
    tags = normalize_skill_values(skills)
    if not tags:
        return "-"
    return "".join([f"<span class='skill-pill'>{html.escape(tag)}</span>" for tag in tags])


def format_skill_tags(skills: Any) -> str:
    tags = normalize_skill_values(skills)
    if not tags:
        return "-"
    return "".join([f"<span class='tag-pill'>{html.escape(tag)}</span>" for tag in tags])


def format_candidate_skill_text(skills: Any) -> str:
    tags = normalize_skill_values(skills)
    return ", ".join(tags) if tags else "-"


def format_education(education: Any) -> str:
    if not education:
        return "-"
    if isinstance(education, str):
        return education
    if isinstance(education, dict):
        parts = []
        if education.get("degree"):
            parts.append(str(education["degree"]))
        if education.get("college"):
            parts.append(str(education["college"]))
        if education.get("year"):
            parts.append(str(education["year"]))
        return " | ".join(parts) if parts else str(education)
    if isinstance(education, list):
        items = []
        for item in education:
            if isinstance(item, dict):
                item_parts = []
                if item.get("degree"):
                    item_parts.append(str(item["degree"]))
                if item.get("college"):
                    item_parts.append(str(item["college"]))
                if item.get("year"):
                    item_parts.append(str(item["year"]))
                items.append(" | ".join(item_parts) if item_parts else str(item))
            else:
                items.append(str(item))
        return ", ".join(items)
    return str(education)


def format_projects(projects: list[dict[str, Any]] | None) -> str:
    if not projects:
        return "<p style='margin:0;color:#64748b;'>No project details found.</p>"
    items = "".join([f"<li>{proj.get('title') or 'Project'}: {proj.get('description') or ''}</li>" for proj in projects])
    return f"<ul style='margin:0.4rem 0 0 1rem; padding-left: 1rem;'>{items}</ul>"


def performance_accuracy(candidates: list[dict[str, Any]]) -> int:
    if not candidates:
        return 0
    valid = 0
    for candidate in candidates:
        if candidate.get("name") and candidate.get("email"):
            valid += 1
    return round(valid / len(candidates) * 100)


def normalize_phone(phone: str | None) -> str:
    if not phone:
        return "-"
    digits = re.sub(r"\D", "", phone.strip())
    if digits.startswith("91") and len(digits) > 10:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10:
        return digits
    return phone.strip()


def candidates_to_csv(candidates: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Phone", "Experience", "Skills", "Projects", "Resume URL"])
    for candidate in candidates:
        skills = []
        for s in candidate.get("skills") or []:
            if isinstance(s, dict):
                skills.append(s.get("skill_name") or "")
            else:
                skills.append(str(s))
        projects = []
        for p in candidate.get("projects") or []:
            if isinstance(p, dict):
                projects.append(p.get("title") or "")
            else:
                projects.append(str(p))
        _cid = get_candidate_id(candidate)
        resume_url = f"{BACKEND_URL}/public/candidate/{_cid}/resume" if _cid else ""
        writer.writerow([
            candidate.get("name") or "",
            candidate.get("email") or "",
            normalize_phone(candidate.get("phone")),
            candidate.get("experience_years") or "",
            "; ".join(skills),
            "; ".join(projects),
            resume_url,
        ])
    return output.getvalue()


def get_candidate_id(candidate: dict[str, Any]) -> str:
    """Different backends name the candidate's unique id differently."""
    if not candidate:
        return ""
    for key in ("candidate_id", "id", "_id", "candidateId", "candidate_uuid", "uuid"):
        value = candidate.get(key)
        if value:
            return str(value)
    return ""


def dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse duplicate records (same email, or same name if no email) so
    re-uploading the same resume doesn't spam the recent list with repeats."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for c in candidates:
        key = (c.get("email") or "").strip().lower() or (c.get("name") or "").strip().lower()
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        unique.append(c)
    return unique


def candidate_completeness(candidate: dict[str, Any]) -> int:
    """How complete a candidate's extracted profile is (0-100), based on
    whether key fields were successfully parsed. This is NOT a measure of
    resume quality - it's purely 'how many of the fields we look for did
    we manage to fill in for this candidate'."""
    fields = [
        bool(candidate.get("name")),
        bool(candidate.get("email")),
        bool(candidate.get("phone")),
        bool(candidate.get("experience_years")),
        bool(normalize_skill_values(candidate.get("skills"))),
        bool(candidate.get("education") or candidate.get("educations")),
    ]
    return round(sum(fields) / len(fields) * 100)


def compute_top_skills(candidates: list[dict[str, Any]], top_n: int = 5) -> tuple[list[tuple[str, int]], int]:
    """Aggregate real skill counts across all candidates."""
    counter: Counter = Counter()
    for c in candidates:
        for s in normalize_skill_values(c.get("skills")):
            if s:
                counter[s.strip()] += 1
    total = sum(counter.values())
    if total == 0:
        return [], 0
    top = counter.most_common(top_n)
    shown = sum(v for _, v in top)
    others = total - shown
    result = list(top)
    if others > 0:
        result.append(("Others", others))
    return result, total


def score_distribution(candidates: list[dict[str, Any]]) -> dict[str, int]:
    buckets = {"0-20%": 0, "21-40%": 0, "41-60%": 0, "61-80%": 0, "81-100%": 0}
    for c in candidates:
        score = candidate_completeness(c)
        if score <= 20:
            buckets["0-20%"] += 1
        elif score <= 40:
            buckets["21-40%"] += 1
        elif score <= 60:
            buckets["41-60%"] += 1
        elif score <= 80:
            buckets["61-80%"] += 1
        else:
            buckets["81-100%"] += 1
    return buckets


DONUT_COLORS = ["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#94a3b8"]

# Flat line-icon paths (Lucide-style) used for the dashboard metric cards.
# Rendered as inline SVG (not emoji) so they look like crisp vector icons
# rather than platform-dependent emoji glyphs.
METRIC_ICON_PATHS = {
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
            '<path d="M14 2v6h6"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.2"/>'
              '<circle cx="12" cy="12" r="1.4" fill="{color}" stroke="none"/>',
    "person": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
              '<circle cx="12" cy="7" r="4"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/>'
                 '<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
                 '<path d="M2 13h20"/>',
}


def metric_icon_svg(name: str, color: str) -> str:
    body = METRIC_ICON_PATHS[name].format(color=color)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


# Small icon set used in card headers (e.g. "📄 Upload Resume"), matching
# the reference design's icon-next-to-title style.
SECTION_ICON_PATHS = {
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
            '<path d="M14 2v6h6"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    "chart": '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6" rx="0.5"/>'
             '<rect x="13" y="8" width="3" height="10" rx="0.5"/>'
             '<rect x="19" y="5" width="3" height="13" rx="0.5"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
             '<circle cx="9" cy="7" r="4"/>'
             '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
             '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
}


def section_header_svg(name: str, color: str) -> str:
    body = SECTION_ICON_PATHS[name]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


def render_section_header(icon: str, title: str, color: str) -> str:
    return (
        "<div style='display:flex; align-items:center; gap:0.55rem; margin-bottom:0.9rem;'>"
        f"<span style='display:inline-flex; margin-left:-0.35rem;'>{section_header_svg(icon, color)}</span>"
        f"<h3 style='margin:0;'>{html.escape(title)}</h3>"
        "</div>"
    )


def render_donut_chart(skill_counts: list[tuple[str, int]], total: int) -> str:
    if not skill_counts or total == 0:
        return "<p style='margin:0;color:#94a3b8;'>No skills extracted yet.</p>"
    gradient_parts = []
    legend_parts = []
    start = 0.0
    for i, (name, count) in enumerate(skill_counts):
        pct = count / total * 100
        color = DONUT_COLORS[i % len(DONUT_COLORS)]
        end = start + pct
        gradient_parts.append(f"{color} {start:.2f}% {end:.2f}%")
        legend_parts.append(
            f"<div class='donut-legend-item'><span class='donut-dot' style='background:{color};'></span>"
            f"<span class='donut-legend-label'>{html.escape(name)}</span>"
            f"<span class='donut-legend-value'>{pct:.0f}%</span></div>"
        )
        start = end
    gradient_css = ", ".join(gradient_parts)
    return (
        f"<div class='donut-wrap'>"
        f"<div class='donut-chart' style='background: conic-gradient({gradient_css});'></div>"
        f"<div class='donut-legend'>{''.join(legend_parts)}</div>"
        f"</div>"
    )


# Section headers we recognise inside the raw extracted resume text. Longer
# headers are matched first so "Technical Skills" isn't clobbered by a
# generic "Skills" match, etc.
RESUME_SECTION_HEADERS = [
    "Technical Skills",
    "Professional Summary",
    "Work Experience",
    "Additional Information",
    "Areas of Interest",
    "Soft Skills",
    "Certifications",
    "Achievements",
    "Experience",
    "Education",
    "Projects",
    "Skills",
    "Languages",
]


def format_resume_text(raw_text: str) -> str:
    if not raw_text or not raw_text.strip():
        return "<p class='resume-line'>No extracted text available.</p>"

    text = raw_text.strip()
    headers_sorted = sorted(RESUME_SECTION_HEADERS, key=len, reverse=True)
    header_pattern = r"(?<![A-Za-z])(" + "|".join(re.escape(h) for h in headers_sorted) + r")(?![A-Za-z])"
    text = re.sub(header_pattern, r"\n§§SECTION§§\1§§\n", text)
    text = re.sub(r"\.\s+[–-]\s+", ".\n• ", text)
    text = text.replace(" | ", "\n")

    blocks = [b for b in text.split("\n") if b.strip()]

    html_parts: list[str] = []
    for block in blocks:
        block = block.strip()
        match = re.match(r"^§§SECTION§§(.+?)§§$", block)
        if match:
            html_parts.append(f"<div class='resume-section-header'>{html.escape(match.group(1))}</div>")
            continue
        if block.startswith("•"):
            html_parts.append(f"<div class='resume-bullet'>{html.escape(block)}</div>")
        else:
            html_parts.append(f"<div class='resume-line'>{html.escape(block)}</div>")

    return "".join(html_parts) if html_parts else "<p class='resume-line'>No extracted text available.</p>"


# --- Query-param helpers (compatible with both the modern st.query_params
# mapping and the older st.experimental_get/set_query_params API) ---------
def get_query_param(name: str) -> str | None:
    try:
        return st.query_params.get(name)
    except Exception:
        params = st.experimental_get_query_params()
        val = params.get(name)
        if isinstance(val, list):
            return val[0] if val else None
        return val


def clear_query_param(name: str) -> None:
    try:
        if name in st.query_params:
            del st.query_params[name]
    except Exception:
        try:
            params = st.experimental_get_query_params()
            params.pop(name, None)
            st.experimental_set_query_params(**params)
        except Exception:
            pass


if "theme" not in st.session_state:
    st.session_state["theme"] = "light"
if "page" not in st.session_state:
    st.session_state["page"] = "Dashboard"
if "selected_candidate_id" not in st.session_state:
    st.session_state["selected_candidate_id"] = None

# Pick up a candidate selection made by clicking a plain link (?candidate=...)
_qp_candidate = get_query_param("candidate")
if _qp_candidate:
    st.session_state["selected_candidate_id"] = _qp_candidate
    st.session_state["page"] = "Candidates"

header_col, right_col = st.columns([3, 1])
with header_col:
    st.markdown("<div style='display:flex; align-items:center; gap:0.75rem; margin-bottom:0.2rem;'><h1 style='margin:0; font-size:2.75rem;'>Recruitment Copilot</h1></div>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Your resume parsing assistant for candidate extraction and talent matching.</p>", unsafe_allow_html=True)
with right_col:
    greet_col, toggle_col = st.columns([4, 1], gap="small")
    with greet_col:
        st.markdown(f"<p style='margin:0; font-size:1.1rem; text-align:right; padding-top:0.55rem;'>{greeting_text()}, Recruiter 👋</p>", unsafe_allow_html=True)
    with toggle_col:
        _header_icon = "🌙" if st.session_state["theme"] == "light" else "☀️"
        if st.button(_header_icon, key="theme_toggle_header", help="Switch to " + ("dark" if st.session_state["theme"] == "light" else "light") + " mode"):
            st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
            st.rerun()

st.markdown(get_theme_css(st.session_state["theme"]), unsafe_allow_html=True)
inject_theme_toggle_style()

_dark = st.session_state["theme"] == "dark"
_accent = "#60a5fa" if _dark else "#2563eb"
_card_bg = "#111827" if _dark else "#ffffff"
_border_col = "#334155" if _dark else "#e2e8f0"
_text_col = "#e2e8f0" if _dark else "#0f172a"
_muted_col = "#94a3b8" if _dark else "#64748b"

st.markdown(f"""
<style>
/* Native resume uploader: force a vertical, centered layout
   (icon on top, text below, button below that) instead of the
   default horizontal row. */
section[data-testid="stFileUploaderDropzone"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}}
section[data-testid="stFileUploaderDropzone"] > div {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    width: 100% !important;
}}
div[data-testid="stFileUploaderDropzoneInstructions"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
}}
div[data-testid="stFileUploader"] section > button {{
    margin-top: 0.85rem !important;
    margin-left: 0 !important;
    align-self: center !important;
}}

/* Dashboard/upload cards are boxed via inject_card_style() (JS, matched by
   each card's visible <h3> title) rather than CSS here - see that function
   for why: relying on Streamlit's border-container testid/CSS :has()
   turned out to be unreliable across environments. h3 margins for card
   titles are still set globally here for consistent spacing. */
h3 {{ margin-top: 0; margin-bottom: 0; font-size: 1.02rem; font-weight: 700; }}

/* Streamlit's native alert boxes (st.info/success/error/warning) ship with
   negative left/right margins by default, meant to bleed edge-to-edge in
   the page's default padding. Once nested inside our own padded card,
   that negative margin makes them stick out past the card's border. Reset
   it here so alerts stay contained. Also cap every descendant of a
   VerticalBlock at 100% width with border-box sizing as a safety net, so
   nothing (charts, uploaders, alerts, etc.) can overflow a card's edge. */
div[data-testid="stAlert"] {{
    margin-left: 0 !important;
    margin-right: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
}}
div[data-testid="stVerticalBlock"] {{ max-width: 100%; box-sizing: border-box; }}
div[data-testid="stVerticalBlock"] > div {{ max-width: 100%; box-sizing: border-box; }}
/* Streamlit bakes an explicit pixel `width` onto each element-container /
   markdown wrapper at initial render, measured from the container's width
   at that moment. Because our card padding is added afterwards (via JS,
   to work around border-container detection issues across Streamlit
   versions), those fixed pixel widths don't shrink to match the now
   slightly-narrower padded content area, and content bleeds past the
   card's edge. Force these wrappers to always be fluid (100% of whatever
   space is actually available) instead of a frozen pixel value. */
div[data-testid="element-container"],
div[data-testid="stMarkdownContainer"],
div[data-testid="stMarkdown"] {{
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}}

/* Hide Streamlit's own built-in "View fullscreen" toolbar BUTTON that
   appears on hover in the top-right corner of charts/dataframes/images in
   recent Streamlit versions. IMPORTANT: only the button itself is hidden
   here (not any surrounding toolbar/container element) - in some Streamlit
   versions the wrapping element also contains the chart's own overlay
   region, so hiding the wrapper hid the whole chart, not just the button. */
[data-testid="stElementToolbarButton"] {{
    display: none !important;
}}
button[title="View fullscreen"] {{
    display: none !important;
}}
/* Belt-and-suspenders: also hide Vega-Lite's own "..." action menu, in case
   it's ever shown alongside Streamlit's toolbar. */
.vega-embed summary {{
    display: none !important;
}}
.vega-embed .vega-actions {{
    display: none !important;
}}

.skill-chip {{
    display: inline-flex; align-items: center; margin: 0 0.35rem 0.35rem 0;
    padding: 0.3rem 0.7rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600;
    background: {"#1e3a8a" if _dark else "#eff6ff"} !important;
    color: {"#93c5fd" if _dark else "#2563eb"} !important;
}}

.metric-icon-card {{
    background: {_card_bg}; border: 1px solid {_border_col}; border-radius: 16px;
    padding: 1rem 1.1rem;
}}
.metric-icon {{
    width: 34px; height: 34px; border-radius: 10px;
    display:flex; align-items:center; justify-content:center;
    font-size: 1.05rem; margin-bottom: 0.6rem;
}}
.metric-icon-label {{ color: {_muted_col}; font-size: 0.85rem; font-weight: 600; }}
.metric-icon-value {{ color: {_text_col}; font-size: 1.6rem; font-weight: 700; margin-top: 0.2rem; }}
.metric-icon-sub {{ color: {_muted_col}; font-size: 0.75rem; margin-top: 0.15rem; }}
.donut-wrap {{ display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap; }}
.donut-chart {{
    width:110px; height:110px; border-radius:50%; flex-shrink:0;
    mask: radial-gradient(farthest-side, transparent calc(100% - 18px), #000 calc(100% - 18px));
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 18px), #000 calc(100% - 18px));
}}
.donut-legend {{ display:flex; flex-direction:column; gap:0.4rem; }}
.donut-legend-item {{ display:flex; align-items:center; gap:0.5rem; font-size:0.85rem; color:{_text_col} !important; }}
.donut-dot {{ width:9px; height:9px; border-radius:50%; flex-shrink:0; }}
.donut-legend-label {{ flex:1; }}
.donut-legend-value {{ font-weight:700; color:{_muted_col} !important; }}
.activity-item {{ display:flex; gap:0.6rem; align-items:flex-start; padding:0.5rem 0; border-bottom:1px solid {_border_col}; }}
.activity-item:last-child {{ border-bottom:none; }}
.activity-icon {{ width:28px; height:28px; border-radius:50%; background:#eef2ff; color:#6366f1; display:flex; align-items:center; justify-content:center; font-size:0.85rem; flex-shrink:0; }}
.activity-title {{ font-size:0.85rem; font-weight:600; color:{_text_col} !important; }}
.activity-sub {{ font-size:0.78rem; color:{_muted_col} !important; }}
.mini-row {{ display:flex; align-items:center; gap:0.75rem; padding:0.5rem 0; border-bottom:1px solid {_border_col}; }}
.mini-row:last-child {{ border-bottom:none; }}
.mini-name {{ width:35%; font-size:0.85rem; font-weight:600; color:{_text_col} !important; }}
.mini-bar-wrap {{ flex:1; height:0.5rem; background:{_border_col}; border-radius:999px; overflow:hidden; }}
.mini-bar-fill {{ height:100%; background: linear-gradient(90deg,#6366f1,{_accent}); border-radius:999px; }}
.mini-score {{ width:45px; text-align:right; font-size:0.8rem; font-weight:700; color:{_muted_col} !important; }}

.candidate-skills-cell {{ display:flex; flex-wrap:wrap; gap:0.3rem; align-items:center; }}
.candidate-skills-cell .tag-pill {{ margin: 0 0 0 0; }}
.candidate-skills-more {{ font-size:0.78rem; color:{_muted_col} !important; font-weight:600; }}

/* Sidebar nav: no box/border at all - flat like the reference. */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] * {{
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] [data-testid^="stVerticalBlock"] {{
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}
</style>
""", unsafe_allow_html=True)

inject_sidebar_flatten_style(st.session_state["theme"])
inject_card_style(st.session_state["theme"])
inject_hide_chart_toolbar()

response = api_call("get", "/public/candidates")
if response.ok:
    candidates = response.json()
else:
    candidates = []

candidates = dedupe_candidates(candidates)

processed = len(candidates)
accuracy = performance_accuracy(candidates)

with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'><div class='logo-badge'>RC</div>"
        "<h2>Recruitment Copilot</h2></div>",
        unsafe_allow_html=True,
    )
    section = st.session_state["page"]

    for item, icon_key in NAV_ITEMS:
        is_active = section == item
        if st.button(
            item,
            key=f"nav_{item}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            section = item
            st.session_state["page"] = section
            st.rerun()

    inject_nav_icons(st.session_state["theme"])

if section == "Dashboard":
    st.header("Dashboard")
    st.subheader("Your recruitment command center")

    top_skills, total_skill_count = compute_top_skills(candidates, top_n=5)
    completeness_scores = [candidate_completeness(c) for c in candidates]
    avg_completeness = round(sum(completeness_scores) / len(completeness_scores)) if completeness_scores else 0
    dist = score_distribution(candidates)

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1:
        st.markdown(
            "<div class='metric-icon-card'>"
            "<div class='metric-icon' style='background:#eef2ff;'>"
            f"{metric_icon_svg('file', '#6366f1')}</div>"
            "<div class='metric-icon-label'>Resumes Processed</div>"
            f"<div class='metric-icon-value'>{processed}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            "<div class='metric-icon-card'>"
            "<div class='metric-icon' style='background:#ecfdf5;'>"
            f"{metric_icon_svg('target', '#10b981')}</div>"
            "<div class='metric-icon-label'>Extraction Accuracy</div>"
            f"<div class='metric-icon-value'>{accuracy}%</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            "<div class='metric-icon-card'>"
            "<div class='metric-icon' style='background:#eff6ff;'>"
            f"{metric_icon_svg('person', '#3b82f6')}</div>"
            "<div class='metric-icon-label'>Profiles Created</div>"
            f"<div class='metric-icon-value'>{processed}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            "<div class='metric-icon-card'>"
            "<div class='metric-icon' style='background:#fff7ed;'>"
            f"{metric_icon_svg('briefcase', '#f59e0b')}</div>"
            "<div class='metric-icon-label'>Job Postings</div>"
            "<div class='metric-icon-value'>—</div>"
            "<div class='metric-icon-sub'>Not tracked yet</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

    chart_col, skills_col, activity_col = st.columns([1.3, 1, 1], gap="large")
    with chart_col:
        with st.container():
            st.markdown(render_section_header("chart", "Resume Processing Overview", _accent), unsafe_allow_html=True)
            if processed:
                # Real per-candidate completeness scores, in upload order -
                # unlike a plain resume-index-vs-itself plot (which is a
                # guaranteed straight diagonal line no matter what the data
                # is), this actually reflects extraction quality over time.
                ordered_candidates = list(reversed(candidates))
                chart_df = pd.DataFrame({
                    "Resume #": list(range(1, processed + 1)),
                    "Completeness %": [candidate_completeness(c) for c in ordered_candidates],
                })
                line_color = "#6366f1"
                # Give the x domain a little headroom on both ends and force
                # whole-number ticks (Resume # is always an integer), so the
                # axis doesn't show fractional ticks like 1.0/1.1/1.2 on a
                # tiny 1-2 point domain, and the line/points don't butt up
                # right against the card's edge.
                x_domain_max = max(processed, 2)
                x_encoding = alt.X(
                    "Resume #:Q",
                    axis=alt.Axis(grid=False, tickMinStep=1, format="d", labelColor=_muted_col, titleColor=_muted_col),
                    scale=alt.Scale(domain=[1, x_domain_max], nice=False, padding=14),
                )
                area = (
                    alt.Chart(chart_df)
                    .mark_area(
                        interpolate="monotone",
                        line={"color": line_color, "size": 3},
                        color=alt.Gradient(
                            gradient="linear",
                            stops=[
                                alt.GradientStop(color=line_color, offset=0),
                                alt.GradientStop(color="rgba(99,102,241,0.03)", offset=1),
                            ],
                            x1=1, x2=1, y1=1, y2=0,
                        ),
                        opacity=0.35,
                    )
                    .encode(
                        x=x_encoding,
                        y=alt.Y("Completeness %:Q", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(gridColor=_border_col, labelColor=_muted_col, titleColor=_muted_col)),
                    )
                )
                points = (
                    alt.Chart(chart_df)
                    .mark_circle(color=line_color, size=55)
                    .encode(
                        x=x_encoding,
                        y="Completeness %:Q",
                        tooltip=["Resume #", "Completeness %"],
                    )
                )
                combined_chart = (
                    (area + points)
                    .properties(
                        height=200,
                        padding={"top": 12, "right": 16, "bottom": 6, "left": 6},
                        background="transparent",
                    )
                    .configure_view(strokeWidth=0)
                )
                st.altair_chart(combined_chart, use_container_width=True)
            else:
                st.markdown("<p style='color:#94a3b8;'>No resumes processed yet.</p>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='progress-heading-row' style='margin-top:0.5rem;'>"
                f"<span>Total Resumes</span><span>{processed}</span></div>"
                f"<div class='progress-heading-row'>"
                f"<span>Avg. Completeness</span><span>{avg_completeness}%</span></div>",
                unsafe_allow_html=True,
            )
    with skills_col:
        with st.container():
            st.markdown(render_section_header("chart", "Top Skills Extracted", _accent), unsafe_allow_html=True)
            st.markdown(render_donut_chart(top_skills, total_skill_count), unsafe_allow_html=True)
    with activity_col:
        with st.container():
            st.markdown(render_section_header("clock", "Recent Activity", _accent), unsafe_allow_html=True)
            recent_for_activity = dedupe_candidates(list(reversed(candidates)))[:5]
            if recent_for_activity:
                items = "".join(
                    [
                        "<div class='activity-item'><span class='activity-icon'>⬆</span>"
                        "<div><div class='activity-title'>Resume uploaded</div>"
                        f"<div class='activity-sub'>{html.escape(c.get('name') or c.get('resume_file') or 'Unknown')}</div></div></div>"
                        for c in recent_for_activity
                    ]
                )
                st.markdown(items, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#94a3b8;'>No recent activity.</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

    table_col, dist_col = st.columns([1.4, 1], gap="large")
    with table_col:
        with st.container():
            st.markdown(render_section_header("users", "Recent Candidates", _accent), unsafe_allow_html=True)
            recent_table = dedupe_candidates(list(reversed(candidates)))[:5]
            if recent_table:
                rows = ""
                for c in recent_table:
                    score = candidate_completeness(c)
                    rows += (
                        "<div class='mini-row'>"
                        f"<div class='mini-name'>{html.escape(c.get('name') or '-')}</div>"
                        f"<div class='mini-bar-wrap'><div class='mini-bar-fill' style='width:{score}%;'></div></div>"
                        f"<div class='mini-score'>{score}%</div>"
                        "</div>"
                    )
                st.markdown(rows, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#94a3b8;'>No candidates yet.</p>", unsafe_allow_html=True)
    with dist_col:
        with st.container():
            st.markdown(render_section_header("chart", "Profile Completeness Distribution", _accent), unsafe_allow_html=True)
            if processed:
                bucket_order = list(dist.keys())
                dist_df = pd.DataFrame({"Bucket": bucket_order, "Candidates": list(dist.values())})
                # Give the y-axis extra headroom above the tallest bar so a
                # bucket with all candidates in it doesn't reach the exact
                # top of the plot area (which reads as "cut off" against the
                # card's edge). +1 (and a minimum of 4) leaves clear space
                # above the tallest bar regardless of how many candidates
                # there are.
                y_max = max(4, max(dist.values(), default=0) + 1)
                bar_chart = (
                    alt.Chart(dist_df)
                    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=30)
                    .encode(
                        x=alt.X("Bucket:N", sort=bucket_order, axis=alt.Axis(labelAngle=0, grid=False, title=None, labelColor=_muted_col)),
                        y=alt.Y(
                            "Candidates:Q",
                            axis=alt.Axis(gridColor=_border_col, title=None, labelColor=_muted_col, tickMinStep=1),
                            scale=alt.Scale(domain=[0, y_max], nice=False),
                        ),
                        color=alt.Color("Bucket:N", scale=alt.Scale(domain=bucket_order, range=DONUT_COLORS), legend=None),
                        tooltip=["Bucket", "Candidates"],
                    )
                    .properties(
                        height=200,
                        padding={"top": 12, "right": 8, "bottom": 6, "left": 6},
                        background="transparent",
                    )
                    .configure_view(strokeWidth=0)
                )
                st.altair_chart(bar_chart, use_container_width=True)
            else:
                st.markdown("<p style='color:#94a3b8;'>No data yet.</p>", unsafe_allow_html=True)

elif section == "Resume Upload":
    st.header("Resume Upload")
    st.subheader("Upload a PDF or DOCX resume to create candidate profiles")
    st.markdown("<p class='section-subtitle'>Drag and drop resumes, or browse to select a file. Then click Upload Files to parse and inspect the result.</p>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        with st.container():
            st.markdown(render_section_header("file", "Upload Resume", _accent), unsafe_allow_html=True)

            uploaded_file = st.file_uploader("Upload resume", type=["pdf", "docx"], key="resume_uploader", label_visibility="collapsed")

            if uploaded_file is not None:
                size_kb = len(uploaded_file.getvalue()) / 1024
                size_label = f"{size_kb/1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
                st.markdown(
                    "<div class='upload-file-card'>"
                    f"<span>📄 {html.escape(uploaded_file.name)}</span>"
                    f"<span class='file-status'>{size_label} · Ready to upload</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                if st.button("Upload Files", key="process_resume", use_container_width=True):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    with st.spinner("Parsing resume..."):
                        upload_response = api_call("post", "/public/resume/upload", files=files)
                    if upload_response.ok:
                        candidate = upload_response.json().get("candidate")
                        st.success("Resume uploaded and parsed successfully.")
                        st.session_state["last_candidate"] = candidate
                        st.rerun()
                    else:
                        try:
                            detail = upload_response.json().get("detail", "Unable to process resume")
                        except Exception:
                            detail = "Unable to process resume"
                        st.error(detail)
            else:
                st.info("Select a resume file to begin parsing.")

    with right_col:
        with st.container():
            st.markdown(render_section_header("chart", "Parsing Progress", _accent), unsafe_allow_html=True)
            st.markdown(
                f"<div class='progress-heading-row'><span>Extraction Progress</span><span>{accuracy}%</span></div>"
                f"<div class='progress-bar'><div class='progress-bar-fill' style='width:{accuracy}%;'></div></div>",
                unsafe_allow_html=True,
            )

            candidate = st.session_state.get("last_candidate")
            if candidate:
                st.markdown("<h4 style='margin-top:0.25rem;'>Extracted Information</h4>", unsafe_allow_html=True)
                st.markdown(
                    "<div class='detail-grid'>"
                    f"<div class='detail-row'><span class='detail-label'>Name</span><span class='detail-value'>{html.escape(candidate.get('name') or 'Unknown')}</span></div>"
                    f"<div class='detail-row'><span class='detail-label'>Email</span><span class='detail-value'>{html.escape(candidate.get('email') or '-')}</span></div>"
                    f"<div class='detail-row'><span class='detail-label'>Phone</span><span class='detail-value'>{html.escape(normalize_phone(candidate.get('phone')))}</span></div>"
                    f"<div class='detail-row'><span class='detail-label'>Experience</span><span class='detail-value'>{html.escape(str(candidate.get('experience_years') or 'N/A'))} yrs</span></div>"
                    f"<div class='detail-row'><span class='detail-label'>Education</span><span class='detail-value'>{html.escape(format_education(candidate.get('education')))}</span></div>"
                    f"<div class='detail-row'><span class='detail-label'>Location</span><span class='detail-value'>{html.escape(candidate.get('location') or '-')}</span></div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                skills_tags = normalize_skill_values(candidate.get("skills"))
                skills_html = "".join([f"<span class='skill-chip'>{html.escape(tag)}</span>" for tag in skills_tags]) or "-"
                st.markdown(f"<div style='margin-top:1rem;'><strong>Skills:</strong></div><div style='margin-top:0.5rem;'>{skills_html}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='margin-top:1rem;'>No parsed resume details available yet. Upload a resume to see extracted candidate data.</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown(render_section_header("users", "Recently Processed Candidates", _accent), unsafe_allow_html=True)
        recent_candidates = dedupe_candidates(list(reversed(candidates)))[:5]
        if recent_candidates:
            rows_html = ""
            for c in recent_candidates:
                skills_text = format_candidate_skill_text(c.get("skills"))
                rows_html += (
                    "<tr>"
                    f"<td>{html.escape(c.get('name') or '-')}</td>"
                    f"<td>{html.escape(c.get('email') or '-')}</td>"
                    f"<td>{html.escape(skills_text)}</td>"
                    "<td class='status-processed'>Processed</td>"
                    "</tr>"
                )
            st.markdown(
                f"<table class='recent-table'><thead><tr><th>Candidate Name</th><th>Email</th><th>Key Skills</th><th>Status</th></tr></thead><tbody>{rows_html}</tbody></table>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<p style='margin:0;'>No candidates processed yet. Upload a resume to populate this list.</p>", unsafe_allow_html=True)

    inject_uploader_style(st.session_state["theme"])

elif section == "Candidates":
    st.header("Candidate Profiles")
    st.markdown(f"<p class='section-subtitle'>Showing {processed} candidate(s). Use the list below to review candidate details and download resumes.</p>", unsafe_allow_html=True)

    selected_candidate_id = st.session_state.get("selected_candidate_id")

    if selected_candidate_id:
        detail_path = f"/public/candidate/{selected_candidate_id}/text"
        detail_response = api_call("get", detail_path)
        if detail_response.ok:
            try:
                detail = detail_response.json()
            except Exception:
                st.error(f"Invalid JSON response from server (status {detail_response.status_code}).")
                raw = detail_response.text
                if raw:
                    st.code(raw[:2000])
                detail = None
        else:
            try:
                err = detail_response.json()
                msg = err.get("detail") if isinstance(err, dict) else str(err)
            except Exception:
                msg = detail_response.text[:500] if detail_response.text else None
            if not msg:
                msg = "(no error body returned)"
            st.markdown("<div class='detail-action-row'>", unsafe_allow_html=True)
            err_back_col, err_retry_col, _spacer = st.columns([1.2, 1.2, 3], gap="small")
            with err_back_col:
                if st.button('← Back to candidates', key=f'back_err_{selected_candidate_id}', use_container_width=True):
                    st.session_state['selected_candidate_id'] = None
                    clear_query_param("candidate")
                    st.rerun()
            with err_retry_col:
                if st.button('Try again', key=f'retry_{selected_candidate_id}', use_container_width=True):
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.error(f"Couldn't load candidate details — HTTP {detail_response.status_code} from {BACKEND_URL}{detail_path}")
            st.code(f"Candidate id used: {selected_candidate_id!r}\nResponse body:\n{msg}")
            detail = None

        if detail:
            st.markdown("<div class='detail-action-row'>", unsafe_allow_html=True)
            back_col, download_col, spacer_col = st.columns([1.2, 1.4, 3], gap="small")
            with back_col:
                if st.button('← Back to candidates', key=f'back_{selected_candidate_id}', use_container_width=True):
                    st.session_state['selected_candidate_id'] = None
                    clear_query_param("candidate")
                    st.rerun()
            with download_col:
                resume_file = get_cached_resume_file(selected_candidate_id)
                if resume_file:
                    file_bytes, file_name, file_mime = resume_file
                    st.download_button(
                        "⬇ Download resume",
                        data=file_bytes,
                        file_name=file_name,
                        mime=file_mime,
                        key=f"download_{selected_candidate_id}",
                        use_container_width=True,
                    )
                else:
                    st.button("⬇ Download unavailable", key=f"download_disabled_{selected_candidate_id}", disabled=True, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='detail-panel'>", unsafe_allow_html=True)
            st.markdown(
                f"<div><h2>{html.escape(detail.get('name') or 'Candidate')}</h2>"
                f"<p class='detail-meta'>Candidate ID: {html.escape(detail.get('candidate_id') or '')}</p>"
                f"<p class='detail-meta'>{html.escape(detail.get('email') or '-') } | {html.escape(detail.get('phone') or '-')}</p></div>",
                unsafe_allow_html=True,
            )

            educations = detail.get('educations') or []
            if educations:
                edu_lines = ''.join([f"<li>{html.escape((e.get('degree') or '') + ' | ' + (e.get('college') or '') + ((' | ' + (e.get('graduation_year') or '')) if e.get('graduation_year') else ''))}</li>" for e in educations])
                st.markdown(f"<div style='margin-top:0.8rem;'><strong>Education</strong><ul style='margin:0.4rem 0 0 1rem; padding-left: 1rem;'>{edu_lines}</ul></div>", unsafe_allow_html=True)

            skills = detail.get('skills') or []
            if skills:
                skills_html = ''.join([f"<span class='tag-pill'>{html.escape(s.get('skill_name') if isinstance(s, dict) else str(s))}</span>" for s in skills])
                st.markdown(f"<div style='margin-top:0.6rem;'><strong>Skills</strong><div style='margin-top:0.4rem;'>{skills_html}</div></div>", unsafe_allow_html=True)

            projects = detail.get('projects') or []
            if projects:
                proj_lines = ''.join([f"<li><strong>{html.escape(p.get('title') or 'Project')}</strong>: {html.escape(p.get('description') or '')}</li>" for p in projects])
                st.markdown(f"<div style='margin-top:0.8rem;'><strong>Projects</strong><ul style='margin:0.4rem 0 0 1rem; padding-left: 1rem;'>{proj_lines}</ul></div>", unsafe_allow_html=True)

            raw_text = detail.get('resume_text') or ''
            formatted_resume_html = format_resume_text(raw_text)
            st.markdown(f"<div class='resume-text-panel'><h4 style='margin-bottom:0.5rem;'>Full Resume Text</h4>{formatted_resume_html}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        if processed:
            csv_data = candidates_to_csv(candidates)
            st.download_button("Download candidates CSV", csv_data, file_name="candidates.csv", mime="text/csv")

            st.markdown(
                "<div class='candidate-row-header'>"
                "<div>Name</div><div>Email</div><div>Phone</div><div>Key Skills</div><div>Resume</div>"
                "</div>",
                unsafe_allow_html=True,
            )

            # Each candidate name is a plain anchor link (?candidate=<id>) so
            # clicking it feels invisible/simple - no button chrome at all -
            # and doesn't rely on any Streamlit-version-specific widget API.
            for idx, c in enumerate(candidates):
                candidate_id = get_candidate_id(c)
                cid_quoted = urllib.parse.quote(str(candidate_id or idx))

                st.markdown("<div class='candidate-row'>", unsafe_allow_html=True)
                name_col, email_col, phone_col, skills_col, resume_col = st.columns(
                    [1.2, 1.4, 0.9, 1.6, 0.9], gap="small"
                )
                with name_col:
                    st.markdown(
                        f"<a class='candidate-link' href='?candidate={cid_quoted}' target='_self'>"
                        f"{html.escape(c.get('name') or '-')}</a>",
                        unsafe_allow_html=True,
                    )
                with email_col:
                    st.markdown(f"<div class='candidate-row-cell'>{html.escape(c.get('email') or '-')}</div>", unsafe_allow_html=True)
                with phone_col:
                    st.markdown(f"<div class='candidate-row-cell'>{html.escape(normalize_phone(c.get('phone')))}</div>", unsafe_allow_html=True)
                with skills_col:
                    st.markdown(f"<div class='candidate-row-cell candidate-skills-cell'>{format_skill_tags(c.get('skills'))}</div>", unsafe_allow_html=True)
                with resume_col:
                    st.markdown("<div class='candidate-row-cell resume-download-cell'>", unsafe_allow_html=True)
                    resume_file = get_cached_resume_file(candidate_id)
                    if resume_file:
                        file_bytes, file_name, file_mime = resume_file
                        st.download_button(
                            "Download",
                            data=file_bytes,
                            file_name=file_name,
                            mime=file_mime,
                            key=f"dl_row_{candidate_id or idx}",
                        )
                    else:
                        st.markdown("<span>-</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No candidates available yet. Upload a resume to create profiles.")

elif section == "Job Postings":
    st.header("Job Postings")
    st.markdown(
        "<p class='section-subtitle'>Create and manage open roles.</p>",
        unsafe_allow_html=True,
    )

    with st.form("create_job_form", clear_on_submit=True):
        job_title = st.text_input("Job title *", placeholder="e.g. Python Developer")
        company_name = st.text_input("Company name *", placeholder="e.g. Infosys")
        description = st.text_area(
            "Job description",
            placeholder="Describe responsibilities, required skills, and qualifications.",
        )
        required_skills = st.text_input(
            "Required skills",
            placeholder="e.g. Python, FastAPI, SQL, Docker",
            help="Enter skills separated by commas. These are used for candidate matching.",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            experience = st.text_input("Experience", placeholder="e.g. 2–4 years")
        with col2:
            location = st.text_input("Location", placeholder="e.g. Hyderabad")
        with col3:
            salary = st.text_input("Salary", placeholder="e.g. ₹6–8 LPA")

        submitted = st.form_submit_button("Create job", use_container_width=True)

    if submitted:
        if not job_title.strip() or not company_name.strip():
            st.error("Job title and company name are required.")
        else:
            payload = {
                "job_title": job_title.strip(),
                "company_name": company_name.strip(),
                "description": description.strip() or None,
                "required_skills": required_skills.strip() or None,
                "experience": experience.strip() or None,
                "location": location.strip() or None,
                "salary": salary.strip() or None,
            }

            try:
                response = api_call("post", "/jobs", payload=payload)

                if response.status_code == 201:
                    st.success("Job posting created successfully.")
                    st.rerun()
                else:
                    st.error(f"Could not create job: {response.text}")
            except requests.RequestException as exc:
                st.error(f"Could not reach the backend: {exc}")

    st.subheader("Open Job Postings")

    try:
        response = api_call("get", "/jobs")

        if response.ok:
            jobs = response.json()

            if not jobs:
                st.info("No job postings yet.")
            else:
                if "editing_job_id" not in st.session_state:
                    st.session_state.editing_job_id = None
                if "delete_job_id" not in st.session_state:
                    st.session_state.delete_job_id = None
                if "matching_job_id" not in st.session_state:
                    st.session_state.matching_job_id = None

                for job in jobs:
                    with st.container(border=True):
                        job_info_col, match_col, edit_col, delete_col = st.columns([7, 1, 1, 1])
                        with job_info_col:
                            st.markdown(f"### {html.escape(job['job_title'])}")
                            st.markdown(f"**{html.escape(job['company_name'])}**")
                            st.write(job.get("description") or "No description provided.")
                            st.caption("Required skills: " + (job.get("required_skills") or "Not specified"))
                            st.caption(
                                f"Experience: {job.get('experience') or '-'}  |  "
                                f"Location: {job.get('location') or '-'}  |  "
                                f"Salary: {job.get('salary') or '-'}"
                            )
                        with match_col:
                            if st.button("Open", key=f"open_job_{job['job_id']}", use_container_width=True):
                                st.session_state.selected_job_id = job["job_id"]
                                st.session_state.page = "Job Detail"
                                st.rerun()
                        with edit_col:
                            if st.button("Edit", key=f"edit_job_{job['job_id']}", use_container_width=True):
                                st.session_state.editing_job_id = job["job_id"]
                                st.rerun()
                        with delete_col:
                            if st.button("Delete", key=f"delete_job_{job['job_id']}", use_container_width=True):
                                st.session_state.delete_job_id = job["job_id"]
                                st.rerun()

                    if st.session_state.delete_job_id == job["job_id"]:
                        st.warning(f"Delete '{job['job_title']}'? This cannot be undone.")
                        confirm_col, cancel_col, _ = st.columns([1, 1, 6])
                        with confirm_col:
                            if st.button("Confirm delete", key=f"confirm_delete_{job['job_id']}", type="primary"):
                                try:
                                    delete_response = api_call("delete", f"/jobs/{job['job_id']}")
                                    if delete_response.ok:
                                        if st.session_state.editing_job_id == job["job_id"]:
                                            st.session_state.editing_job_id = None
                                        st.session_state.delete_job_id = None
                                        st.rerun()
                                    else:
                                        st.error(f"Could not delete job: {delete_response.text}")
                                except requests.RequestException as exc:
                                    st.error(f"Could not reach the backend: {exc}")
                        with cancel_col:
                            if st.button("Cancel", key=f"cancel_delete_{job['job_id']}"):
                                st.session_state.delete_job_id = None
                                st.rerun()

                    if st.session_state.matching_job_id == job["job_id"]:
                        st.subheader(f"Candidate matches: {job['job_title']}")
                        try:
                            match_response = api_call("get", f"/jobs/{job['job_id']}/matches")
                            if not match_response.ok:
                                st.error(f"Could not analyse candidates: {match_response.text}")
                            else:
                                match_data = match_response.json()
                                required_skills = match_data.get("required_skills", [])
                                if not required_skills:
                                    st.warning("No recognised skills were found in this job description. Add named skills such as Python, React, SQL, AWS, or Docker, then try again.")
                                else:
                                    st.caption("Required job skills: " + ", ".join(required_skills))
                                    for candidate_match in match_data.get("matches", []):
                                        with st.container(border=True):
                                            score_col, details_col = st.columns([1, 6])
                                            with score_col:
                                                st.metric("Match", f"{candidate_match['match_score']}%")
                                            with details_col:
                                                st.markdown(f"**{html.escape(candidate_match['candidate_name'])}**")
                                                experience_result = candidate_match.get("experience_match")
                                                experience_label = "Yes" if experience_result else "No" if experience_result is False else "Not assessed"
                                                st.caption(
                                                    f"Experience: {candidate_match.get('candidate_experience') or '-'} | "
                                                    f"Experience requirement met: {experience_label}"
                                                )
                                                st.write("Matched skills: " + (", ".join(candidate_match["matched_skills"]) or "None"))
                                                st.write("Missing skills: " + (", ".join(candidate_match["missing_skills"]) or "None"))
                                                st.write("Additional skills: " + (", ".join(candidate_match["additional_skills"]) or "None"))
                                                location_result = candidate_match.get("location_match")
                                                location_label = "Yes" if location_result else "No" if location_result is False else "Not assessed"
                                                st.caption(
                                                    f"Candidate location: {candidate_match.get('candidate_location') or 'Not available'} | "
                                                    f"Job location: {candidate_match.get('job_location') or 'Not specified'} | "
                                                    f"Location match: {location_label}"
                                                )
                                                st.caption("Education: " + (", ".join(candidate_match["education"]) or "Not available"))
                                                st.caption("Certifications: " + (", ".join(candidate_match["certifications"]) or "Not available"))
                        except requests.RequestException as exc:
                            st.error(f"Could not reach the backend: {exc}")

                    if st.session_state.editing_job_id == job["job_id"]:
                        st.subheader(f"Edit {job['job_title']}")
                        with st.form(f"edit_job_form_{job['job_id']}"):
                            edit_title = st.text_input("Job title *", value=job["job_title"], key=f"edit_title_{job['job_id']}")
                            edit_company = st.text_input("Company name *", value=job["company_name"], key=f"edit_company_{job['job_id']}")
                            edit_description = st.text_area(
                                "Job description",
                                value=job.get("description") or "",
                                key=f"edit_description_{job['job_id']}",
                            )
                            edit_required_skills = st.text_input(
                                "Required skills",
                                value=job.get("required_skills") or "",
                                key=f"edit_required_skills_{job['job_id']}",
                            )
                            edit_col1, edit_col2, edit_col3 = st.columns(3)
                            with edit_col1:
                                edit_experience = st.text_input("Experience", value=job.get("experience") or "", key=f"edit_experience_{job['job_id']}")
                            with edit_col2:
                                edit_location = st.text_input("Location", value=job.get("location") or "", key=f"edit_location_{job['job_id']}")
                            with edit_col3:
                                edit_salary = st.text_input("Salary", value=job.get("salary") or "", key=f"edit_salary_{job['job_id']}")
                            save_changes = st.form_submit_button("Save changes", use_container_width=True)

                        if save_changes:
                            if not edit_title.strip() or not edit_company.strip():
                                st.error("Job title and company name are required.")
                            else:
                                update_payload = {
                                    "job_title": edit_title.strip(),
                                    "company_name": edit_company.strip(),
                                    "description": edit_description.strip() or None,
                                    "required_skills": edit_required_skills.strip() or None,
                                    "experience": edit_experience.strip() or None,
                                    "location": edit_location.strip() or None,
                                    "salary": edit_salary.strip() or None,
                                }
                                try:
                                    update_response = api_call("put", f"/jobs/{job['job_id']}", payload=update_payload)
                                    if update_response.ok:
                                        st.session_state.editing_job_id = None
                                        st.success("Job posting updated successfully.")
                                        st.rerun()
                                    else:
                                        st.error(f"Could not update job: {update_response.text}")
                                except requests.RequestException as exc:
                                    st.error(f"Could not reach the backend: {exc}")
        else:
            st.error(f"Could not load jobs: {response.text}")
    except requests.RequestException as exc:
        st.error(f"Could not reach the backend: {exc}")
        
elif section == "Job Detail":
    selected_job_id = st.session_state.get("selected_job_id")
    if not selected_job_id:
        st.session_state.page = "Job Postings"
        st.rerun()

    if st.button("← Back to job postings", key="back_to_job_postings"):
        st.session_state.page = "Job Postings"
        st.session_state.selected_job_id = None
        st.session_state.show_matches_for = None
        st.rerun()

    try:
        job_response = api_call("get", f"/jobs/{selected_job_id}")
        if not job_response.ok:
            st.error("This job posting could not be found.")
        else:
            selected_job = job_response.json()
            st.header(selected_job["job_title"])
            st.markdown(f"### {selected_job['company_name']}")
            st.caption(
                f"Experience: {selected_job.get('experience') or '-'}  |  "
                f"Location: {selected_job.get('location') or '-'}  |  "
                f"Salary: {selected_job.get('salary') or '-'}"
            )
            st.markdown("#### Job description")
            st.write(selected_job.get("description") or "No description provided.")
            st.markdown("#### Required skills")
            st.write(selected_job.get("required_skills") or "Not specified")

            if st.button("Match candidates", key="match_selected_job", type="primary", use_container_width=True):
                st.session_state.show_matches_for = selected_job_id
                st.rerun()

            if st.session_state.get("show_matches_for") == selected_job_id:
                st.markdown("## Candidate match results")
                match_response = api_call("get", f"/jobs/{selected_job_id}/matches")
                if not match_response.ok:
                    st.error(f"Could not analyse candidates: {match_response.text}")
                else:
                    match_data = match_response.json()
                    required = match_data.get("required_skills", [])
                    if not required:
                        st.warning("Add required skills to this job before matching candidates.")
                    else:
                        summary = match_data.get("summary", {})
                        st.caption("Ranking: skills 75% • experience 20% • location 5%. Ties favour stronger skill coverage, fewer gaps, experience, certifications, education, then location.")
                        required_badges = "".join(
                            f"<span style='display:inline-block;margin:0 .3rem 0 0;padding:.18rem .5rem;border:1px solid #c7d2fe;border-radius:999px;background:#eef2ff;color:#3730a3;font-size:.78rem;'>{html.escape(skill)}</span>"
                            for skill in required
                        )
                        st.markdown(
                            f"<div style='color:#475569;font-size:.8rem;margin:.55rem 0 1rem;'>Required skills &nbsp;{required_badges}</div>",
                            unsafe_allow_html=True,
                        )

                        best_names = ", ".join(
                            html.escape(item.get("display_name") or item["candidate_name"])
                            for item in match_data.get("matches", [])
                            if item["match_score"] == summary.get("top_score", 0)
                        ) or "No candidate yet"
                        st.markdown(
                            f"""
                            <div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;margin:1rem 0 1.3rem;'>
                              <div style='background:#fff;border:1px solid #dbe3f5;border-radius:16px;padding:1rem 1.35rem;'><div style='color:#475569;font-size:.76rem;'>Candidates analysed</div><div style='font-family:Georgia,serif;color:#0f172a;font-size:2rem;font-weight:700;line-height:1.25;'>{summary.get('candidate_count', 0)}</div><div style='color:#64748b;font-size:.72rem;'>across this role</div></div>
                              <div style='background:#fff;border:1px solid #dbe3f5;border-radius:16px;padding:1rem 1.35rem;'><div style='color:#475569;font-size:.76rem;'>Best match</div><div style='font-family:Georgia,serif;color:#0f172a;font-size:2rem;font-weight:700;line-height:1.25;'>{summary.get('top_score', 0)}%</div><div style='color:#64748b;font-size:.72rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{best_names}</div></div>
                              <div style='background:#fff;border:1px solid #dbe3f5;border-radius:16px;padding:1rem 1.35rem;'><div style='color:#475569;font-size:.76rem;'>Average match</div><div style='font-family:Georgia,serif;color:#0f172a;font-size:2rem;font-weight:700;line-height:1.25;'>{summary.get('average_score', 0)}%</div><div style='color:#64748b;font-size:.72rem;'>across all candidates</div></div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        match_rows = match_data.get("matches", [])
                        if match_rows:
                            ranking_rows = []
                            for item in match_rows:
                                score = item["match_score"]
                                if score >= 80:
                                    colour = "#16a34a"
                                elif score >= 60:
                                    colour = "#3b5bff"
                                elif score >= 40:
                                    colour = "#f59e0b"
                                else:
                                    colour = "#94a3b8"
                                name = item.get("display_name") or item["candidate_name"]
                                initials = "".join(part[0] for part in name.split()[:2]).upper() or "C"
                                ranking_rows.append(
                                    f"<div style='display:grid;grid-template-columns:2.2rem minmax(9rem,11rem) minmax(8rem,1fr) 3.5rem;gap:.65rem;align-items:center;padding:.65rem 0;border-bottom:1px solid #e2e8f0;'>"
                                    f"<span style='width:1.7rem;height:1.7rem;display:inline-flex;align-items:center;justify-content:center;border-radius:999px;background:{colour};color:#fff;font-size:.64rem;font-weight:700;'>{html.escape(initials)}</span>"
                                    f"<span style='color:#172554;font-size:.88rem;font-weight:700;'>{html.escape(name)}</span>"
                                    f"<span style='height:.68rem;background:#e9edf5;border-radius:999px;overflow:hidden;'><span style='display:block;height:100%;width:{score}%;background:{colour};border-radius:999px;'></span></span>"
                                    f"<span style='text-align:right;color:{colour};font-size:.82rem;font-weight:700;'>{score}%</span></div>"
                                )
                            st.markdown(
                                f"""
                                <div style='background:#fff;border:1px solid #dbe3f5;border-radius:16px;padding:1.2rem 1.7rem;margin:1.2rem 0;'>
                                  <div style='display:flex;justify-content:space-between;gap:1rem;align-items:center;'>
                                    <h3 style='font-family:Georgia,serif;color:#0f172a;margin:0 0 .55rem;'>Candidate ranking</h3>
                                    <span style='font-size:.72rem;color:#475569;white-space:nowrap;'><b style='color:#16a34a;'>●</b> Excellent &nbsp; <b style='color:#3b5bff;'>●</b> Strong &nbsp; <b style='color:#f59e0b;'>●</b> Potential &nbsp; <b style='color:#94a3b8;'>●</b> Limited</span>
                                  </div>
                                  {''.join(ranking_rows)}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        gap_summary = match_data.get("skill_gap_summary", [])
                        if gap_summary:
                            gap_rows = []
                            for item in gap_summary:
                                missing = item["candidates_missing"]
                                gap_percent = round((missing / len(match_rows)) * 100) if match_rows else 0
                                gap_rows.append(
                                    f"<div style='display:grid;grid-template-columns:6.5rem minmax(8rem,1fr) 3.5rem;gap:.7rem;align-items:center;padding:.55rem 0;'>"
                                    f"<span style='color:#172554;font-weight:700;font-size:.84rem;'>{html.escape(item['skill'])}</span>"
                                    f"<span style='height:.58rem;background:#e9edf5;border-radius:999px;overflow:hidden;'><span style='display:block;height:100%;width:{gap_percent}%;background:#f59e0b;border-radius:999px;'></span></span>"
                                    f"<span style='color:#a16207;text-align:right;font-size:.8rem;font-weight:700;'>{missing}/{len(match_rows)}</span></div>"
                                )
                            st.markdown(
                                f"""
                                <div style='background:#fff;border:1px solid #dbe3f5;border-radius:16px;padding:1.2rem 1.7rem;margin:1.2rem 0;'>
                                  <h3 style='font-family:Georgia,serif;color:#0f172a;margin:0 0 .55rem;'>Most common skill gaps</h3>
                                  {''.join(gap_rows)}
                                  <div style='color:#64748b;font-size:.72rem;margin-top:.25rem;'>Candidates missing each required skill, out of {len(match_rows)} analysed.</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        if match_rows:
                            report_buffer = io.StringIO()
                            report_writer = csv.DictWriter(
                                report_buffer,
                                fieldnames=[
                                    "Rank", "Candidate", "Hiring Score", "Skill Match %", "Skill Gap %",
                                    "Matched Skills", "Missing Skills", "Additional Skills",
                                    "Experience Match", "Location Match", "Recommendations",
                                ],
                            )
                            report_writer.writeheader()
                            for item in match_rows:
                                report_writer.writerow({
                                    "Rank": item["rank"],
                                    "Candidate": item.get("display_name") or item["candidate_name"],
                                    "Hiring Score": item["match_score"],
                                    "Skill Match %": item["skill_match_percentage"],
                                    "Skill Gap %": item["skill_gap_percentage"],
                                    "Matched Skills": ", ".join(item["matched_skills"]),
                                    "Missing Skills": ", ".join(item["missing_skills"]),
                                    "Additional Skills": ", ".join(item["additional_skills"]),
                                    "Experience Match": item["experience_match"],
                                    "Location Match": item["location_match"],
                                    "Recommendations": " | ".join(
                                        recommendation["recommendation"]
                                        for recommendation in item["missing_skill_recommendations"]
                                    ),
                                })
                            st.download_button(
                                "Download skill-gap report (CSV)",
                                data=report_buffer.getvalue(),
                                file_name=f"{selected_job['job_title'].lower().replace(' ', '_')}_skill_gap_report.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )

                        for candidate_match in match_rows:
                            with st.container(border=True):
                                score_col, info_col, status_col = st.columns([1, 5, 1])
                                with score_col:
                                    score = candidate_match["match_score"]
                                    st.metric(f"#{candidate_match['rank']}", f"{score}%")
                                    st.progress(score)
                                with info_col:
                                    st.markdown(f"### {html.escape(candidate_match.get('display_name') or candidate_match['candidate_name'])}")
                                    st.caption(
                                        f"Hiring score {candidate_match['match_score']}%: "
                                        f"skills {candidate_match['skill_score_points']}/75, "
                                        f"experience {candidate_match['experience_score_points']}/20, "
                                        f"location {candidate_match['location_score_points']}/5"
                                    )
                                    st.write("**Matched:** " + (", ".join(candidate_match["matched_skills"]) or "None"))
                                    st.write("**Missing:** " + (", ".join(candidate_match["missing_skills"]) or "None"))
                                    with st.expander("View full comparison"):
                                        st.write("**Additional:** " + (", ".join(candidate_match["additional_skills"]) or "None"))
                                        st.write("**Relevant certifications:** " + (", ".join(candidate_match["relevant_certifications"]) or "None"))
                                        st.write("**Education:** " + (", ".join(candidate_match["education"]) or "Not available"))
                                        if candidate_match["missing_skill_recommendations"]:
                                            st.markdown("**Recommendations**")
                                            for recommendation in candidate_match["missing_skill_recommendations"]:
                                                st.write(f"- {recommendation['skill'].title()}: {recommendation['recommendation']}")
                                with status_col:
                                    experience_value = candidate_match.get("experience_match")
                                    location_value = candidate_match.get("location_match")
                                    experience_text = "Yes" if experience_value else "No" if experience_value is False else "Not assessed"
                                    location_text = "Yes" if location_value else "No" if location_value is False else "Not assessed"
                                    st.caption("Experience")
                                    st.write(experience_text)
                                    st.caption(f"Candidate: {candidate_match.get('candidate_experience') or 'Not available'} years")
                                    st.caption("Location")
                                    st.write(location_text)
                                    st.caption(candidate_match.get("candidate_location") or "Candidate location unavailable")
                                    if st.button("View audit", key=f"audit_{selected_job_id}_{candidate_match['candidate_id']}", use_container_width=True):
                                        st.session_state.audit_job_id = selected_job_id
                                        st.session_state.audit_candidate_id = candidate_match["candidate_id"]
                                        st.session_state.page = "Candidate Skill Audit"
                                        st.rerun()
    except requests.RequestException as exc:
        st.error(f"Could not reach the backend: {exc}")

elif section == "Candidate Skill Audit":
    audit_job_id = st.session_state.get("audit_job_id")
    audit_candidate_id = st.session_state.get("audit_candidate_id")
    if not audit_job_id or not audit_candidate_id:
        st.session_state.page = "Job Detail"
        st.rerun()

    if st.button("← Back to candidate matches", key="back_to_candidate_matches"):
        st.session_state.page = "Job Detail"
        st.rerun()

    try:
        audit_job_response = api_call("get", f"/jobs/{audit_job_id}")
        audit_matches_response = api_call("get", f"/jobs/{audit_job_id}/matches")
        if not audit_job_response.ok or not audit_matches_response.ok:
            st.error("The selected job or candidate analysis could not be loaded.")
        else:
            audit_job = audit_job_response.json()
            audit_match_data = audit_matches_response.json()
            audit_candidate = next(
                (item for item in audit_match_data.get("matches", []) if item["candidate_id"] == audit_candidate_id),
                None,
            )
            if not audit_candidate:
                st.error("This candidate is no longer available in the current matching results.")
            else:
                candidate_display_name = audit_candidate.get("display_name") or audit_candidate["candidate_name"]
                st.header(f"{candidate_display_name} — Skill audit")
                st.caption(f"Evaluated against {audit_job['job_title']} at {audit_job['company_name']}")

                report_buffer = io.StringIO()
                report_writer = csv.DictWriter(
                    report_buffer,
                    fieldnames=["Candidate", "Job", "Hiring Score", "Skill Match %", "Skill Gap %", "Matched Skills", "Missing Skills", "Additional Skills", "Recommendations"],
                )
                report_writer.writeheader()
                report_writer.writerow({
                    "Candidate": candidate_display_name,
                    "Job": audit_job["job_title"],
                    "Hiring Score": audit_candidate["match_score"],
                    "Skill Match %": audit_candidate["skill_match_percentage"],
                    "Skill Gap %": audit_candidate["skill_gap_percentage"],
                    "Matched Skills": ", ".join(audit_candidate["matched_skills"]),
                    "Missing Skills": ", ".join(audit_candidate["missing_skills"]),
                    "Additional Skills": ", ".join(audit_candidate["additional_skills"]),
                    "Recommendations": " | ".join(item["recommendation"] for item in audit_candidate["missing_skill_recommendations"]),
                })
                st.download_button(
                    "Download audit report (CSV)",
                    data=report_buffer.getvalue(),
                    file_name=f"{candidate_display_name.lower().replace(' ', '_')}_skill_audit.csv",
                    mime="text/csv",
                )

                with st.container(border=True):
                    hiring_score = audit_candidate["match_score"]
                    st.markdown(
                        f"""
                        <div style="padding:1.1rem 1.25rem 0.8rem 1.25rem;">
                            <div style="display:flex; justify-content:space-between; align-items:end; gap:1rem;">
                                <div style="color:#1e3a8a !important; font-size:0.85rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase;">Overall hiring score</div>
                                <div style="color:#2563eb !important; font-size:3.2rem; font-weight:700; line-height:1;">{hiring_score}<span style="color:#2563eb !important; font-size:1.25rem;">%</span></div>
                            </div>
                            <div style="position:relative; height:1.1rem; margin-top:3rem; background:#dbeafe; border-radius:999px; overflow:visible;">
                                <div style="height:100%; width:{hiring_score}%; background:linear-gradient(90deg,#1d4ed8,#3b82f6); border-radius:999px;"></div>
                                <div style="position:absolute; left:60%; top:-0.45rem; height:2rem; width:2px; background:#1e3a8a;"></div>
                                <div style="position:absolute; left:60%; top:-1.9rem; transform:translateX(-50%); white-space:nowrap; color:#1e3a8a !important; font-size:0.8rem; font-weight:600;">Shortlist line · 60%</div>
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-top:0.55rem; color:#64748b !important; font-size:0.8rem; font-weight:600;">
                                <span style="color:#64748b !important;">0</span><span style="color:#64748b !important;">25</span><span style="color:#64748b !important;">50</span><span style="color:#64748b !important;">75</span><span style="color:#64748b !important;">100</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.divider()
                    st.markdown("#### Score composition")
                    st.write(
                        f"Skills: **{audit_candidate['skill_score_points']}/75**  |  "
                        f"Experience: **{audit_candidate['experience_score_points']}/20**  |  "
                        f"Location: **{audit_candidate['location_score_points']}/5**"
                    )
                    st.caption("Location remains a low-priority factor; skills and experience determine most of the hiring score.")

                required_count = len(audit_match_data.get("required_skills", []))
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                with metric_col1:
                    st.metric("Required skills", required_count)
                with metric_col2:
                    st.metric("Matched", len(audit_candidate["matched_skills"]))
                with metric_col3:
                    st.metric("Missing", len(audit_candidate["missing_skills"]))
                with metric_col4:
                    st.metric("Additional", len(audit_candidate["additional_skills"]))

                st.markdown("### Missing skills")
                if audit_candidate["missing_skill_recommendations"]:
                    for recommendation in audit_candidate["missing_skill_recommendations"]:
                        with st.container(border=True):
                            st.markdown(f"<span style='color:#2563eb !important; font-weight:700;'>{html.escape(recommendation['skill'].title())}</span>", unsafe_allow_html=True)
                            st.write(recommendation["recommendation"])
                else:
                    st.success("No required skills are missing for this job.")

                def audit_skill_tags(skills: list[str], background: str, border: str) -> str:
                    if not skills:
                        return "<span style='color:#64748b !important;'>None</span>"
                    return " ".join(
                        f"<span style='display:inline-block; margin:0.2rem 0.25rem 0.2rem 0; padding:0.3rem 0.6rem; border-radius:999px; background:{background}; border:1px solid {border}; color:#1e3a8a !important; font-size:0.85rem;'>{html.escape(skill)}</span>"
                        for skill in skills
                    )

                st.markdown("### Matched skills")
                st.markdown(audit_skill_tags(audit_candidate["matched_skills"], "#dbeafe", "#93c5fd"), unsafe_allow_html=True)
                st.markdown("### Additional skills")
                st.markdown(audit_skill_tags(audit_candidate["additional_skills"], "#eff6ff", "#bfdbfe"), unsafe_allow_html=True)

                st.markdown("### Candidate context")
                experience_value = audit_candidate.get("experience_match")
                location_value = audit_candidate.get("location_match")
                experience_text = "Meets requirement" if experience_value else "Below requirement" if experience_value is False else "Not assessed"
                location_text = "Matches job location" if location_value else "Different location" if location_value is False else "Not assessed"
                st.write(
                    f"Experience: **{audit_candidate.get('candidate_experience') or 'Not available'} years** — {experience_text}  |  "
                    f"Location: **{audit_candidate.get('candidate_location') or 'Not available'}** — {location_text}"
                )
    except requests.RequestException as exc:
        st.error(f"Could not reach the backend: {exc}")

elif section == "Analytics":
    st.header("Analytics")
    st.markdown("<p class='section-subtitle'>Hiring outcomes, candidate readiness, and skill gaps across your open roles.</p>", unsafe_allow_html=True)

    try:
        jobs_response = api_call("get", "/jobs")
        jobs_for_analytics = jobs_response.json() if jobs_response.ok else []
    except requests.RequestException:
        jobs_for_analytics = []

    if not jobs_for_analytics:
        st.info("Create a job posting with required skills to see hiring analytics.")
    else:
        job_labels = {
            job["job_id"]: f"{job['job_title']} — {job['company_name']}"
            for job in jobs_for_analytics
        }
        selected_analytics_job = st.selectbox(
            "Analyse job",
            options=["All job postings", *job_labels.values()],
            key="analytics_job_filter",
        )
        selected_analytics_job_id = next(
            (job_id for job_id, label in job_labels.items() if label == selected_analytics_job),
            None,
        )

        job_summary_rows: list[dict[str, Any]] = []
        all_match_rows: list[dict[str, Any]] = []
        all_gap_rows: list[dict[str, Any]] = []
        for job in jobs_for_analytics:
            if selected_analytics_job_id and job["job_id"] != selected_analytics_job_id:
                continue
            try:
                match_response = api_call("get", f"/jobs/{job['job_id']}/matches")
            except requests.RequestException:
                continue
            if not match_response.ok:
                continue
            match_data = match_response.json()
            summary = match_data.get("summary", {})
            job_label = job_labels[job["job_id"]]
            job_summary_rows.append({
                "Job": job_label,
                "Average hiring score": summary.get("average_score", 0),
                "Best hiring score": summary.get("top_score", 0),
            })
            for candidate_match in match_data.get("matches", []):
                all_match_rows.append({
                    "Job": job_label,
                    "Candidate": candidate_match.get("display_name") or candidate_match["candidate_name"],
                    "Hiring score": candidate_match["match_score"],
                    "Score band": (
                        "Excellent (80-100)" if candidate_match["match_score"] >= 80 else
                        "Strong (60-79)" if candidate_match["match_score"] >= 60 else
                        "Potential (40-59)" if candidate_match["match_score"] >= 40 else
                        "Limited (0-39)"
                    ),
                })
            for gap in match_data.get("skill_gap_summary", []):
                all_gap_rows.append({
                    "Skill": gap["skill"],
                    "Candidates missing": gap["candidates_missing"],
                })

        if not all_match_rows:
            st.info("Add required skills to a job and upload candidates to generate analytics.")
        else:
            # Compact recruiter dashboard layout: summary cards, then clear
            # progress-based job, readiness-tier, and skill-gap sections.
            average_hiring_score = round(sum(row["Hiring score"] for row in all_match_rows) / len(all_match_rows))
            top_match = max(all_match_rows, key=lambda row: row["Hiring score"])
            strong_matches = [row for row in all_match_rows if 60 <= row["Hiring score"] < 80]
            potential_matches = [row for row in all_match_rows if 40 <= row["Hiring score"] < 60]
            limited_matches = [row for row in all_match_rows if row["Hiring score"] < 40]
            excellent_matches = [row for row in all_match_rows if row["Hiring score"] >= 80]

            st.markdown(
                f"""
                <div style='display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); margin:0.4rem 0 1.8rem 0;'>
                    <div style='padding:0.6rem 1rem 0.6rem 0;'><div style='color:#2563eb !important; font-size:0.68rem; letter-spacing:0.1em; font-weight:700;'>CANDIDATES</div><div style='color:#0f172a !important; font-size:1.6rem; font-weight:700; margin-top:0.35rem;'>{len(candidates)}</div><div style='color:#64748b !important; font-size:0.72rem;'>across analysed postings</div></div>
                    <div style='padding:0.6rem 1rem;'><div style='color:#2563eb !important; font-size:0.68rem; letter-spacing:0.1em; font-weight:700;'>JOBS ANALYSED</div><div style='color:#0f172a !important; font-size:1.6rem; font-weight:700; margin-top:0.35rem;'>{len(job_summary_rows)}</div><div style='color:#64748b !important; font-size:0.72rem;'>selected scope</div></div>
                    <div style='padding:0.6rem 1rem;'><div style='color:#2563eb !important; font-size:0.68rem; letter-spacing:0.1em; font-weight:700;'>AVERAGE HIRING SCORE</div><div style='color:#0f172a !important; font-size:1.6rem; font-weight:700; margin-top:0.35rem;'>{average_hiring_score}%</div><div style='color:#64748b !important; font-size:0.72rem;'>across candidate matches</div></div>
                    <div style='padding:1rem;'><div style='color:#2563eb !important; font-size:0.68rem; letter-spacing:0.1em; font-weight:700;'>TOP CANDIDATE</div><div style='color:#0f172a !important; font-size:1.6rem; font-weight:700; margin-top:0.35rem;'>{top_match['Hiring score']}%</div><div style='color:#64748b !important; font-size:0.72rem;'>{html.escape(top_match['Candidate'])}</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### Hiring score by job")
            for job_row in job_summary_rows:
                matching_for_job = [row for row in all_match_rows if row["Job"] == job_row["Job"]]
                job_top = max(matching_for_job, key=lambda row: row["Hiring score"]) if matching_for_job else None
                average_score = job_row["Average hiring score"]
                # The job bar represents the best available candidate, while the
                # note keeps the overall average visible for context.
                score = job_top["Hiring score"] if job_top else average_score
                job_note = (
                    f"{len(matching_for_job)} candidates  |  Average: {average_score}%  |  "
                    f"Top match: {html.escape(job_top['Candidate'])} ({job_top['Hiring score']}%)"
                    if job_top
                    else "No candidate matches yet."
                )
                st.markdown(
                    f"""
                    <div style='padding:0.45rem 0 1rem; margin-bottom:0.55rem;'>
                        <div style='display:flex; justify-content:space-between; gap:1rem;'><span style='color:#0f172a !important; font-weight:700;'>{html.escape(job_row['Job'])}</span><span style='color:#2563eb !important; font-size:1.1rem; font-weight:700;'>{score}%</span></div>
                        <div style='height:0.55rem; margin-top:0.75rem; background:#e2e8f0; border-radius:999px; overflow:hidden;'><div style='height:100%; width:{score}%; background:linear-gradient(90deg,#2563eb,#60a5fa); border-radius:999px;'></div></div>
                        <div style='margin-top:0.55rem; color:#64748b !important; font-size:0.78rem;'>{job_note}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("### Candidates by relevance tier")
            tier_col1, tier_col2, tier_col3 = st.columns(3, gap="small")
            tiers = [
                (tier_col1, "Strong", strong_matches + excellent_matches, "#2563eb", "#eff6ff"),
                (tier_col2, "Potential", potential_matches, "#d97706", "#fff7ed"),
                (tier_col3, "Limited", limited_matches, "#64748b", "#f1f5f9"),
            ]
            for tier_column, tier_name, tier_matches, color, badge_background in tiers:
                with tier_column:
                    candidate_rows = "".join(
                        f"<div style='margin-top:0.55rem; color:#0f172a !important; font-size:0.9rem;'>{html.escape(tier_match['Candidate'])} <span style='color:#2563eb !important; font-weight:700;'>— {tier_match['Hiring score']}%</span></div>"
                        for tier_match in tier_matches[:3]
                    ) or "<div style='margin-top:0.7rem; color:#64748b !important; font-size:0.85rem;'>No candidates in this tier</div>"
                    st.markdown(
                        f"""
                        <div style='min-height:8.2rem; padding:0.4rem 0.15rem;'>
                            <span style='display:inline-block; padding:0.22rem 0.58rem; border-radius:4px; background:{badge_background}; color:{color} !important; font-size:0.78rem; font-weight:700; text-transform:lowercase;'>• {tier_name}</span>
                            <div style='margin-top:0.7rem; color:#0f172a !important; font-size:1.55rem; font-weight:700;'>{len(tier_matches)}</div>
                            {candidate_rows}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            aggregated_gap_counts: dict[str, int] = {}
            for gap in all_gap_rows:
                aggregated_gap_counts[gap["Skill"]] = aggregated_gap_counts.get(gap["Skill"], 0) + gap["Candidates missing"]
            if aggregated_gap_counts:
                st.markdown("### Most common skill gaps")
                for skill, missing_count in sorted(aggregated_gap_counts.items(), key=lambda item: item[1], reverse=True):
                    gap_percent = round((missing_count / len(all_match_rows)) * 100)
                    st.markdown(
                        f"""
                        <div style='padding:0.45rem 0 1rem; margin-bottom:0.45rem;'>
                            <div style='display:flex; justify-content:space-between; gap:1rem;'><span style='color:#0f172a !important; font-weight:700;'>{html.escape(skill.title())}</span><span style='color:#2563eb !important; font-size:0.82rem; font-weight:700;'>{missing_count} gap{'s' if missing_count != 1 else ''}</span></div>
                            <div style='height:0.55rem; margin-top:0.75rem; background:#e2e8f0; border-radius:999px; overflow:hidden;'><div style='height:100%; width:{gap_percent}%; background:linear-gradient(90deg,#2563eb,#60a5fa); border-radius:999px;'></div></div>
                            <div style='margin-top:0.55rem; color:#64748b !important; font-size:0.78rem;'>{missing_count} of {len(all_match_rows)} candidate matches are missing this skill ({gap_percent}%).</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.stop()

            average_hiring_score = round(sum(row["Hiring score"] for row in all_match_rows) / len(all_match_rows))
            top_match = max(all_match_rows, key=lambda row: row["Hiring score"])
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            with metric_col1:
                st.metric("Candidates", len(candidates))
            with metric_col2:
                st.metric("Jobs analysed", len(job_summary_rows))
            with metric_col3:
                st.metric("Average hiring score", f"{average_hiring_score}%")
            with metric_col4:
                st.metric("Top candidate", f"{top_match['Hiring score']}%", top_match["Candidate"])

            job_chart_col, distribution_chart_col = st.columns(2, gap="large")
            with job_chart_col:
                summary_df = pd.DataFrame(job_summary_rows)
                job_chart = (
                    alt.Chart(summary_df)
                    .mark_bar(color="#2563eb", cornerRadiusEnd=6)
                    .encode(
                        x=alt.X("Average hiring score:Q", scale=alt.Scale(domain=[0, 100]), title="Average hiring score (%)"),
                        y=alt.Y("Job:N", sort="-x", title=None, axis=alt.Axis(labelLimit=220)),
                        tooltip=["Job:N", "Average hiring score:Q", "Best hiring score:Q"],
                    )
                    .properties(height=max(180, len(summary_df) * 46), title="Hiring score by job")
                    .configure(background="#ffffff")
                    .configure_view(fill="#ffffff", stroke="#e2e8f0")
                    .configure_axis(labelColor="#0f172a", titleColor="#0f172a", gridColor="#e2e8f0")
                    .configure_title(color="#0f172a", fontSize=16)
                )
                st.altair_chart(job_chart, use_container_width=True)

            with distribution_chart_col:
                distribution_df = pd.DataFrame(all_match_rows)
                distribution_chart = (
                    alt.Chart(distribution_df)
                    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                    .encode(
                        x=alt.X("Score band:N", sort=["Excellent (80-100)", "Strong (60-79)", "Potential (40-59)", "Limited (0-39)"], title=None),
                        y=alt.Y("count():Q", title="Candidate matches"),
                        color=alt.Color(
                            "Score band:N",
                            scale=alt.Scale(
                                domain=["Excellent (80-100)", "Strong (60-79)", "Potential (40-59)", "Limited (0-39)"],
                                range=["#16a34a", "#2563eb", "#f59e0b", "#94a3b8"],
                            ),
                            legend=None,
                        ),
                        tooltip=["Score band:N", alt.Tooltip("count():Q", title="Candidates")],
                    )
                    .properties(height=220, title="Candidate readiness distribution")
                    .configure(background="#ffffff")
                    .configure_view(fill="#ffffff", stroke="#e2e8f0")
                    .configure_axis(labelColor="#0f172a", titleColor="#0f172a", gridColor="#e2e8f0")
                    .configure_title(color="#0f172a", fontSize=16)
                )
                st.altair_chart(distribution_chart, use_container_width=True)

            aggregated_gaps = pd.DataFrame(all_gap_rows).groupby("Skill", as_index=False)["Candidates missing"].sum() if all_gap_rows else pd.DataFrame()
            if not aggregated_gaps.empty:
                gap_chart = (
                    alt.Chart(aggregated_gaps)
                    .mark_bar(color="#f59e0b", cornerRadiusEnd=6)
                    .encode(
                        x=alt.X("Candidates missing:Q", title="Candidates with this gap"),
                        y=alt.Y("Skill:N", sort="-x", title=None),
                        tooltip=["Skill:N", "Candidates missing:Q"],
                    )
                    .properties(height=max(160, len(aggregated_gaps) * 38), title="Most common skill gaps")
                    .configure(background="#ffffff")
                    .configure_view(fill="#ffffff", stroke="#e2e8f0")
                    .configure_axis(labelColor="#0f172a", titleColor="#0f172a", gridColor="#e2e8f0")
                    .configure_title(color="#0f172a", fontSize=16)
                )
                st.altair_chart(gap_chart, use_container_width=True)

elif section == "Settings":
    st.header("Settings")
    st.markdown("<p class='section-subtitle'>Configure your recruitment workspace and parser preferences.</p>", unsafe_allow_html=True)
    st.markdown("<div class='upload-card' style='margin-top:1rem;'>", unsafe_allow_html=True)
    st.markdown("<h3>Appearance</h3>", unsafe_allow_html=True)
    st.write("Choose how Recruitment Copilot looks for you.")

    _settings_label_col, _settings_btn_col = st.columns([3, 1])
    with _settings_label_col:
        st.markdown(f"<p style='margin-top:0.6rem;'>Currently in <strong>{st.session_state['theme']}</strong> mode.</p>", unsafe_allow_html=True)
    with _settings_btn_col:
        _settings_icon = "🌙" if st.session_state["theme"] == "light" else "☀️"
        if st.button(_settings_icon, key="theme_toggle_settings", help="Switch to " + ("dark" if st.session_state["theme"] == "light" else "light") + " mode"):
            st.session_state["theme"] = "dark" if st.session_state["theme"] == "light" else "light"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
