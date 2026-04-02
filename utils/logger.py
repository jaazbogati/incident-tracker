import logging
import json
from datetime import datetime, UTC
from flask import g, request, has_request_context

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if has_request_context():
            log_record.update({
                "request_id": getattr(g, "request_id", None),
                "method": request.method,
                "path": request.path,
            })

        if hasattr(record, "status"):
            log_record["status"] = record.status

        if hasattr(record, "duration"):
            log_record["duration_ms"] = record.duration

        return json.dumps(log_record)