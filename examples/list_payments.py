"""Lista pagos con filtros, orden y paginación.

Reemplazá ``COLLECTOR_ID`` por el identificador de tu comercio.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from examples._client import build_client
from pagotic import format_filter_datetime

COLLECTOR_ID = "00000000-0000-0000-0000-000000000000"


def main() -> None:
    since = format_filter_datetime(datetime.now(timezone.utc) - timedelta(days=30))

    with build_client() as sdk:
        result = sdk.payments.list(
            page=1,
            limit=20,
            sorts={"request_date": "descending"},
            filters=[
                {"field": "collector_id", "operation": "EQUAL", "value": COLLECTOR_ID},
                {
                    "field": "request_date",
                    "operation": "GREATER_THAN_OR_EQUAL_TO",
                    "value": since,
                },
            ],
        )

        for payment in result.get("results", []):
            print(payment["id"], payment["status"], payment.get("final_amount"))


if __name__ == "__main__":
    main()
