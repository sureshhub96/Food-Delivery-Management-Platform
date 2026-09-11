from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.audit_log import AuditLog


async def audit_middleware(request: Request, call_next):
    start_time = datetime.now(timezone.utc)

    response = await call_next(request)

    end_time = datetime.now(timezone.utc)

    db: Session = SessionLocal()

    try:
        user_id = None

        # Try to get the authenticated user
        try:
            if hasattr(request.state, "user") and request.state.user:
                user_id = request.state.user.id
        except Exception:
            user_id = None

        audit = AuditLog(
            user_id=user_id,
            action=request.method,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            ip_address=request.client.host if request.client else None,
            created_at=end_time,
        )

        db.add(audit)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Audit log error: {e}")

    finally:
        db.close()

    return response