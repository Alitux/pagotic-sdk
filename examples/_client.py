"""Cliente compartido por los ejemplos.

Carga ``.env`` (ignorado por git) y acepta tanto ``PAGOTIC_*`` como las
variables genéricas ``USERNAME``, ``PASSWORD``, ``CLIENT_ID`` y ``CLIENT_SECRET``.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from pagotic import PagoTIC

load_dotenv()


def build_client() -> PagoTIC:
    return PagoTIC(
        username=os.getenv("PAGOTIC_USERNAME") or os.getenv("USERNAME"),
        password=os.getenv("PAGOTIC_PASSWORD") or os.getenv("PASSWORD"),
        client_id=os.getenv("PAGOTIC_CLIENT_ID") or os.getenv("CLIENT_ID"),
        client_secret=os.getenv("PAGOTIC_CLIENT_SECRET") or os.getenv("CLIENT_SECRET"),
    )
