"""Baseline benchmark for the endpoints COMP-932 touches.

Measures what the ticket is actually about: how many SQL statements each path
emits, how long the database spends on them, and how many EPIC.track HTTP calls
are made. Serialization is included in the measurement because lazy loads fire
at dump time, not query time.

Run before and after the change:

    . venv/bin/activate
    python tests/perf/bench_overfetch.py --out before.json
    python tests/perf/bench_overfetch.py --out after.json --compare before.json

Uses the test database (DATABASE_TEST_* in .env) and drops its public schema.
"""
import argparse
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest import mock

from flask import g
from flask_migrate import Migrate, upgrade
from sqlalchemy import event, text

os.environ["FLASK_ENV"] = "testing"

from compliance_api import create_app  # noqa: E402
from compliance_api.config import get_named_config  # noqa: E402
from compliance_api.models import db  # noqa: E402
from tests.utilities.factory_scenario import TokenJWTClaims  # noqa: E402

CONFIG = get_named_config("testing")
CLAIMS = TokenJWTClaims.super_user.value

# Seed size. Small enough to build quickly, large enough that a per-row cost
# separates from a per-request one.
CASE_FILES = 200
INSPECTIONS = 200
COMPLAINTS = 200
STAFF = 20
PROJECTS = 20


class Counter:
    """Count and time every statement the connection executes."""

    def __init__(self):
        """Start with an empty tally."""
        self.count = 0
        self.seconds = 0.0
        self.statements = []
        self.max_joins = 0
        self.max_columns = 0
        self._start = None

    def _before(self, conn, cursor, statement, params, context, executemany):
        self._start = time.perf_counter()

    def _after(self, conn, cursor, statement, params, context, executemany):
        self.count += 1
        self.seconds += time.perf_counter() - self._start
        flat = " ".join(statement.split())
        self.statements.append(flat[:160])
        # Width of the widest SELECT: how many tables it joins and how many
        # columns it drags back. This is what the eager-load changes move.
        if flat.upper().startswith("SELECT"):
            joins = flat.upper().count(" JOIN ")
            head = flat[: flat.upper().find(" FROM ")] if " FROM " in flat.upper() else flat
            columns = head.count(",") + 1
            if joins > self.max_joins:
                self.max_joins = joins
            if columns > self.max_columns:
                self.max_columns = columns

    @contextmanager
    def watching(self, engine):
        """Attach to `engine` for the duration of the block."""
        event.listen(engine, "before_cursor_execute", self._before)
        event.listen(engine, "after_cursor_execute", self._after)
        try:
            yield self
        finally:
            event.remove(engine, "before_cursor_execute", self._before)
            event.remove(engine, "after_cursor_execute", self._after)


def reset_schema(app):
    """Drop and rebuild the test schema, then run the migrations."""
    with app.app_context():
        session = db.session()
        session.execute(
            text(
                f"DROP SCHEMA IF EXISTS public CASCADE;"
                f"CREATE SCHEMA public;"
                f"GRANT ALL ON SCHEMA public TO {CONFIG.DB_USER};"
                f"GRANT ALL ON SCHEMA public TO public;"
            )
        )
        session.commit()
        Migrate(app, db)
        upgrade()


def seed(app):
    """Insert enough rows that per-row costs are visible."""
    from compliance_api.models import CaseFile, StaffUser
    from compliance_api.models.complaint import Complaint, ComplaintStatusEnum
    from compliance_api.models.complaint.complaint_option import ComplaintSource
    from compliance_api.models.inspection import Inspection, InspectionType
    from compliance_api.models.inspection.inspection_enum import InspectionAttendanceOptionEnum
    from compliance_api.models.project import Project

    with app.app_context():
        g.jwt_oidc_token_info = CLAIMS
        session = db.session

        # Migrations seed some lookup data already; top up rather than collide.
        projects = Project.query.all()
        missing = PROJECTS - len(projects)
        if missing > 0:
            fresh = [Project(name=f"Bench Project {i}") for i in range(missing)]
            session.add_all(fresh)
            session.flush()
            projects = projects + fresh
        projects = projects[:PROJECTS]

        from compliance_api.models.position import Position

        position_id = session.query(Position.id).order_by(Position.id).limit(1).scalar()
        staff = [
            StaffUser(
                first_name=f"Officer{i}",
                last_name=f"Test{i}",
                position_id=position_id,
                auth_user_guid=f"officer{i}@test",
            )
            for i in range(STAFF)
        ]
        session.add_all(staff)
        session.flush()

        from compliance_api.models.case_file import CaseFileInitiationOption
        from compliance_api.models.inspection.inspection_option import (
            InspectionInitiationOption, InspectionTypeOption)

        case_file_initiation_id = session.query(CaseFileInitiationOption.id).order_by(
            CaseFileInitiationOption.id).limit(1).scalar()
        inspection_initiation_id = session.query(InspectionInitiationOption.id).order_by(
            InspectionInitiationOption.id).limit(1).scalar()
        type_ids = [row[0] for row in session.query(InspectionTypeOption.id).order_by(
            InspectionTypeOption.id).limit(3).all()]

        case_files = [
            CaseFile(
                project_id=projects[i % PROJECTS].id,
                date_created=datetime.utcnow() - timedelta(days=i),
                primary_officer_id=staff[i % STAFF].id,
                initiation_id=case_file_initiation_id,
                case_file_number=f"CF-{i:05d}",
            )
            for i in range(CASE_FILES)
        ]
        session.add_all(case_files)
        session.flush()

        inspections = [
            Inspection(
                case_file_id=case_files[i % CASE_FILES].id,
                project_id=projects[i % PROJECTS].id,
                primary_officer_id=staff[i % STAFF].id,
                initiation_id=inspection_initiation_id,
                start_date=datetime.utcnow() - timedelta(days=i),
                end_date=datetime.utcnow() - timedelta(days=i) + timedelta(hours=4),
                ir_number=f"IR-{i:05d}",
            )
            for i in range(INSPECTIONS)
        ]
        session.add_all(inspections)
        session.flush()

        session.add_all(
            [
                InspectionType(inspection_id=inspection.id, type_id=type_ids[i % len(type_ids)])
                for i, inspection in enumerate(inspections)
            ]
        )

        # One requirement per inspection so the grid and its export have rows.
        from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
        from compliance_api.models.topic import Topic

        topic_id = session.query(Topic.id).order_by(Topic.id).limit(1).scalar()
        session.add_all(
            [
                InspectionRequirement(
                    inspection_id=inspection.id,
                    summary=f"Bench requirement {i}",
                    topic_id=topic_id,
                    sort_order=i,
                )
                for i, inspection in enumerate(inspections)
            ]
        )

        # First Nations attendance on the first inspection drives the item 1 path.
        from compliance_api.models.inspection.inspection_attendance import InspectionAttendance

        session.add(
            InspectionAttendance(
                inspection_id=inspections[0].id,
                attendance_option_id=InspectionAttendanceOptionEnum.FIRSTNATIONS.value,
            )
        )

        source_type_id = session.query(ComplaintSource.id).order_by(
            ComplaintSource.id).limit(1).scalar()
        session.add_all(
            [
                Complaint(
                    case_file_id=case_files[i % CASE_FILES].id,
                    primary_officer_id=staff[i % STAFF].id,
                    complaint_number=f"CM-{i:05d}",
                    date_received=datetime.utcnow() - timedelta(days=i),
                    status=ComplaintStatusEnum.OPEN,
                    concern_description=f"Bench complaint {i}",
                    source_type_id=source_type_id,
                )
                for i in range(COMPLAINTS)
            ]
        )
        session.commit()


def measure(app, name, fn):
    """Measure one path with the statement counters attached."""
    counter = Counter()
    with app.app_context():
        g.jwt_oidc_token_info = CLAIMS
        db.session.expire_all()
        with counter.watching(db.engine):
            started = time.perf_counter()
            rows = fn()
            wall = time.perf_counter() - started
    duplicates = len(counter.statements) - len(set(counter.statements))
    return {
        "name": name,
        "queries": counter.count,
        "repeated_queries": duplicates,
        "joins": counter.max_joins,
        "columns": counter.max_columns,
        "db_ms": round(counter.seconds * 1000, 1),
        "wall_ms": round(wall * 1000, 1),
        "rows": rows,
    }


def paths(page_size):
    """Return the paths the ticket changes, serialized the way the resource does."""
    from compliance_api.schemas import CaseFileSchema, ComplaintSchema, InspectionSchema
    from compliance_api.services import (
        CaseFileService, ComplaintService, InspectionRequirementService, InspectionService)

    args = {"page_no": "1", "page_size": str(page_size)}

    def inspection_list():
        items, _ = InspectionService.get_inspections_paginated(dict(args))
        return len(InspectionSchema(many=True).dump(items))

    def case_file_list():
        items, _ = CaseFileService.get_all_with_pagination(dict(args))
        return len(CaseFileSchema(many=True).dump(items))

    def complaint_list():
        items, _ = ComplaintService.get_complaints_paginated(dict(args))
        return len(ComplaintSchema(many=True).dump(items))

    def requirement_grid():
        items, _ = InspectionRequirementService.get_all_inspection_requirements(dict(args))
        return len(items)

    def inspection_export():
        return len(InspectionService.generate_inspections_excel({}).getvalue())

    def complaint_export():
        return len(ComplaintService.generate_complaints_excel({}).getvalue())

    return [
        (f"GET /inspections (page_size={page_size})", inspection_list),
        (f"GET /case-files (page_size={page_size})", case_file_list),
        (f"GET /complaints (page_size={page_size})", complaint_list),
        (f"GET /inspection-requirements (page_size={page_size})", requirement_grid),
        ("POST /inspections/export (all rows)", inspection_export),
        ("POST /complaints/export (all rows)", complaint_export),
    ]


def measure_first_nations(app):
    """Count EPIC.track HTTP calls on the attendance path (ticket item 1)."""
    nations = [{"id": i, "name": f"Nation {i}"} for i in range(1, 6)]

    with app.app_context():
        g.jwt_oidc_token_info = CLAIMS
        from compliance_api.models.inspection.inspection_attendance import InspectionAttendance
        from compliance_api.models.inspection.inspection_firstnation import InspectionFirstnation

        attendance = InspectionAttendance.query.first()
        inspection_id = attendance.inspection_id
        existing = InspectionFirstnation.query.filter_by(inspection_id=inspection_id).count()
        if existing == 0:
            db.session.add_all(
                [
                    InspectionFirstnation(inspection_id=inspection_id, firstnation_id=n["id"])
                    for n in nations
                ]
            )
            db.session.commit()
        has_option = attendance is not None

    target = "compliance_api.services.epic_track_service.track_service.TrackService"
    with app.app_context():
        g.jwt_oidc_token_info = CLAIMS
        from compliance_api.services import InspectionService

        with mock.patch(f"{target}.get_first_nation_by_id") as by_id, mock.patch(
            f"{target}.get_first_nations"
        ) as all_nations:
            by_id.side_effect = lambda i: {"id": i, "name": f"Nation {i}"}
            all_nations.return_value = nations
            started = time.perf_counter()
            InspectionService.get_attendance_options(inspection_id)
            wall = time.perf_counter() - started
            return {
                "name": "GET /inspections/<id>/attendance-options (5 first nations)",
                "track_calls_by_id": by_id.call_count,
                "track_calls_list": all_nations.call_count,
                "http_requests": by_id.call_count + all_nations.call_count,
                "wall_ms": round(wall * 1000, 1),
                "attendance_option_seeded": has_option,
            }


def render(results, baseline=None):
    """Print one line per measured path, with the baseline alongside if given."""
    width = max(len(r["name"]) for r in results) + 2
    header = (
        f"{'path':<{width}}{'queries':>9}{'repeat':>8}{'joins':>7}{'cols':>7}"
        f"{'db ms':>9}{'wall ms':>9}{'rows':>9}"
    )
    print(header)
    print("-" * len(header))
    for row in results:
        if "queries" not in row:
            continue
        line = (
            f"{row['name']:<{width}}{row['queries']:>9}{row['repeated_queries']:>8}"
            f"{row['joins']:>7}{row['columns']:>7}"
            f"{row['db_ms']:>9}{row['wall_ms']:>9}{row['rows']:>9}"
        )
        if baseline:
            before = next((b for b in baseline if b["name"] == row["name"]), None)
            if before and "queries" in before:
                line += (
                    f"   (was {before['queries']} q / {before.get('joins', '?')} joins"
                    f" / {before.get('columns', '?')} cols / {before['db_ms']} ms)"
                )
        print(line)


def main():
    """Seed if asked, measure every path, print and optionally save the results."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="write results as JSON")
    parser.add_argument("--compare", help="baseline JSON to diff against")
    parser.add_argument("--page-size", type=int, default=15)
    parser.add_argument("--skip-seed", action="store_true", help="reuse the existing test DB")
    args = parser.parse_args()

    app = create_app(run_mode="testing")
    if not args.skip_seed:
        reset_schema(app)
        seed(app)

    results = [measure(app, name, fn) for name, fn in paths(args.page_size)]
    first_nations = measure_first_nations(app)

    render(results, json.load(open(args.compare)) if args.compare else None)
    print()
    print(
        f"{first_nations['name']}: {first_nations['http_requests']} EPIC.track HTTP calls "
        f"({first_nations['track_calls_by_id']} by-id, {first_nations['track_calls_list']} list), "
        f"{first_nations['wall_ms']} ms"
    )

    if args.out:
        with open(args.out, "w") as handle:
            json.dump(results + [first_nations], handle, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
