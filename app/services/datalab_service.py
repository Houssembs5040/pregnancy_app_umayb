"""
datalab_service.py
~~~~~~~~~~~~~~~~~~
Converts uploaded files (PDFs, images, DOCX, …) to Markdown using the
Datalab API (https://documentation.datalab.to/docs/welcome/api).

Flow
----
1. POST  /api/v1/convert  → returns { request_id, request_check_url }
2. Poll  GET <request_check_url> every POLL_INTERVAL seconds until
         status == "complete" or "failed"
3. Return result["markdown"] to the caller

Files are processed in-memory and never written to disk.
"""

import os
import time
import requests

DATALAB_API_KEY = os.getenv("DATALAB_API_KEY", "")
DATALAB_CONVERT_URL = "https://www.datalab.to/api/v1/convert"

POLL_INTERVAL = 2      # seconds between status checks
POLL_TIMEOUT  = 120    # give up after this many seconds


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def convert_file_to_markdown(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    mode: str = "balanced",
) -> str:
    """
    Submit *file_bytes* to Datalab and block until conversion is done.

    Parameters
    ----------
    file_bytes : bytes
        Raw content of the uploaded file.
    filename   : str
        Original filename (used for the multipart upload name).
    mime_type  : str
        MIME type, e.g. ``"application/pdf"`` or ``"image/png"``.
    mode       : str
        Datalab processing mode: ``"fast"`` | ``"balanced"`` | ``"accurate"``.

    Returns
    -------
    str
        The converted Markdown text.

    Raises
    ------
    RuntimeError
        If the API returns an error or conversion fails / times out.
    """
    if not DATALAB_API_KEY:
        raise RuntimeError(
            "DATALAB_API_KEY is not set. Add it to your .env file."
        )

    headers = {"X-Api-Key": DATALAB_API_KEY}

    # ------------------------------------------------------------------
    # Step 1 – submit the document
    # ------------------------------------------------------------------
    submit_resp = requests.post(
        DATALAB_CONVERT_URL,
        headers=headers,
        files={"file": (filename, file_bytes, mime_type)},
        data={"output_format": "markdown", "mode": mode},
        timeout=60,
    )

    if not submit_resp.ok:
        raise RuntimeError(
            f"Datalab submit failed [{submit_resp.status_code}]: "
            f"{submit_resp.text}"
        )

    submit_data = submit_resp.json()
    if not submit_data.get("success"):
        raise RuntimeError(
            f"Datalab submit unsuccessful: {submit_data.get('error', submit_data)}"
        )

    check_url: str = submit_data["request_check_url"]

    # ------------------------------------------------------------------
    # Step 2 – poll until complete
    # ------------------------------------------------------------------
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        poll_resp = requests.get(check_url, headers=headers, timeout=30)
        if not poll_resp.ok:
            raise RuntimeError(
                f"Datalab poll failed [{poll_resp.status_code}]: {poll_resp.text}"
            )

        result = poll_resp.json()
        status = result.get("status")

        if status == "complete":
            if not result.get("success"):
                raise RuntimeError(
                    f"Datalab conversion failed: {result.get('error', result)}"
                )
            markdown = result.get("markdown", "")
            if not markdown:
                # Fallback: some responses wrap it differently
                markdown = result.get("output", {}).get("markdown", "")
            return markdown

        if status == "failed":
            raise RuntimeError(
                f"Datalab conversion failed: {result.get('error', result)}"
            )

        time.sleep(POLL_INTERVAL)

    raise RuntimeError(
        f"Datalab conversion timed out after {POLL_TIMEOUT} seconds "
        f"(check_url={check_url})"
    )
