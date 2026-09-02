# Single-Center Health Screening Platform

Digitizes the BL-006-04 Health Screening Form and the FY25 Summary Report,
scoped to one Center (Region → Center → Facilities → Providers →
Beneficiaries). Advertising and shortlisting of health providers happens
**outside** this platform — the Center Admin registers providers here only
after that external decision is made.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env      # fill in DATABASE_URL, SECRET_KEY, SMTP + Carbone settings
uvicorn main:app --reload
```

On first run, tables are auto-created. **Then, before anything else can
work, create the first Admin account:**

```bash
python seed_admin.py
```

This is deliberately a standalone script, not an API endpoint — an
"create an Admin" HTTP route would be a permanent attack surface sitting
in a deployed system. It's run once, directly against the database, by
whoever has server access during initial setup. It also offers to seed
the Center profile (name/region/contact info) in the same step, since
that's needed as the header on reports. Run it again later if you ever
need a second Admin — it refuses to create a duplicate email but doesn't
otherwise limit how many Admins can exist.

Once that's done, log in as that Admin via `POST /api/v1/auth/login-request`
to get your first token, then use `/user/onboard` to register facilities
and providers as normal.

## Folder structure

```
health_screening_platform/
├── main.py                  # app entrypoint, wires all routers
├── database.py               # SQLAlchemy engine/session
├── requirements.txt
├── .env.example
├── core/
│   ├── config.py              # all settings, env-driven
│   ├── security.py            # password hashing, JWT, OTP, RBAC (require_role, enforce_facility_scope)
│   ├── audit.py                # writes to SecurityAuditLog
│   ├── email_service.py       # SMTP email gateway (vendor-agnostic)
│   └── carbone_service.py     # renders the report matrix into a formatted xlsx/pdf via Carbone
└── screening/
    ├── models/                 # SQLAlchemy tables
    ├── schemas/                 # Pydantic request/response models
    ├── repositories/            # DB queries, no business logic
    ├── services/                 # business logic: BMI, cohort aging, referral rules, report assembly
    └── routers/                   # FastAPI endpoints, one file per resource
```

## Roles (RBAC)

- **Admin** — the Center head. Full access to everything: registers
  facilities and providers, creates/edits beneficiaries, views all
  screenings, manages referral cases, pulls reports.
- **Provider** — a nurse/clinician at one facility. Can only view and
  screen beneficiaries assigned to their own facility (enforced by
  `enforce_facility_scope`, using `facility_id` embedded in their token).

Enforced via `core/security.py`'s `require_role(*roles)` dependency —
declared on each route, not scattered as manual `if` checks.

## Full endpoint reference

### Auth (`/api/v1/auth`)
| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/activate-account` | Public (needs valid code) | First login: exchange emailed access code for a real password |
| POST | `/login-request` | Public | Step 1: verify password, sends OTP |
| POST | `/login-verify-otp` | Public | Step 2: verify OTP, issues session + refresh tokens |
| POST | `/refresh-token` | Public (needs valid refresh token) | Exchange refresh token for new session token |
| POST | `/forgot-password` | Public | Request reset link (generic response either way) |
| POST | `/reset-password` | Public (needs valid token) | Complete reset, blacklists old sessions |
| POST | `/change-password` | Logged in | Change password, knowing current one |
| POST | `/logout` | Logged in | Blacklist current refresh token |

### Provider & User Management (`/api/v1/user`) — Admin only
| Method | Path | Purpose |
|---|---|---|
| POST | `/onboard` | Register a vetted provider under a facility; emails access code |
| POST | `/{id}/resend-access-code` | Re-send a lost/expired access code |
| PUT | `/{id}/toggle-status` | Activate/Revoke a provider account |
| GET | `/{id}` | View one provider's profile |
| GET | `/` | List/filter providers by facility or role |

### Facility Management (`/api/v1/facility`) — Admin only
| Method | Path | Purpose |
|---|---|---|
| POST | `/` | Register a clinic |
| GET | `/` | List all facilities |
| GET | `/{id}/staff` | List providers under one facility |
| PUT | `/{id}/status` | Suspend/reactivate a facility |

### Center Profile (`/api/v1/center`)
| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/` | Admin, Provider | View this deployment's center profile |
| PUT | `/{id}` | Admin | Edit center name/region/contact info |

### Beneficiary Records (`/api/v1/beneficiary`)
| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/` | Admin only | Register a new beneficiary |
| GET | `/` | Admin (any/filtered), Provider (own facility only) | List/filter beneficiaries |
| GET | `/due-for-screening/{fiscal_year}` | Admin only | Beneficiaries not yet screened this cycle |
| GET | `/{id}` | Admin, Provider (facility-scoped) | View one beneficiary |
| PUT | `/{id}` | Admin only | Correct demographics |
| PUT | `/{id}/log-birth` | Admin only | Survival Mother → Survival Baby (same ID retained) |
| PUT | `/{id}/assign-facility` | Admin only | Assign/reassign screening facility |

### Clinical Screenings (`/api/v1/screening`)
| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/status` | Public | Health check |
| POST | `/submit` | Provider only | Submit the digital BL-006-04 form; runs BMI cross-check + referral engine |
| GET | `/beneficiary/{id}` | Admin, Provider (facility-scoped) | Full screening history for one beneficiary |
| GET | `/{record_id}` | Admin, Provider (facility-scoped) | View one submitted form |
| PUT | `/{record_id}` | Admin, Provider (facility-scoped) | Amend/correct a submitted form |

### Referral Case Management (`/api/v1/referrals`) — Admin only
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Dashboard: open cases (filterable by status/facility) |
| GET | `/{id}` | Full case detail + status history |
| PUT | `/{id}/status` | Move case through Identified → Referred → Scheduled → Completed / LostToFollowUp |

### Reporting (`/api/v1/report`) — Admin only
| Method | Path | Purpose |
|---|---|---|
| GET | `/{fiscal_year}` | Live JSON report matrix, sliced by 3 cohorts |
| GET | `/{fiscal_year}/export?format=xlsx` | Same data as a downloadable formatted document via Carbone |

### Audit Trail (`/api/v1/audit-logs`) — Admin only
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Browse/filter the full audit trail (by user, beneficiary, action keyword, date range) |
| GET | `/beneficiary/{id}` | Full access history for one beneficiary — "who has viewed/changed this record" |

`core/audit.py`'s `log_audit_event()` is already called from the auth, beneficiary, screening,
and referral routers on every significant read/write. This is the read side that exposes
that trail to the admin — previously the table existed but nothing could see into it.

## Key design decisions carried over from our discussion

- **Advertising/shortlisting is external.** No `Opportunity`/`Application`
  models — the platform starts at "Admin registers a vetted provider."
- **Beneficiary IDs are permanent.** A "Survival Mother" beneficiary_id
  represents the unborn baby; `log-birth` updates the same record in place.
- **Cohort aging (Baby → general participant at age 3) is computed, not
  stored-and-trusted** — see `services/cohort.py`. No cron job needed for
  correctness at this scale; add one later only if query performance
  requires pre-computed cohort values.
- **Malnutrition status is examiner-entered, source of truth.** The
  system's BMI-based calculation is stored separately
  (`bmi_computed_malnutrition_status`) as a cross-check, never overwrites
  the clinician's judgment.
- **Facility scoping is real, not cosmetic.** `facility_id` is embedded in
  the JWT at login and checked on every beneficiary/screening/referral
  access via `enforce_facility_scope`.
- **Referrals are real cases, not a boolean.** Auto-opened by
  `services/referral_engine.py` when a screening trips a trigger, tracked
  through a full status lifecycle with a permanent history log.
- **No external identity provider.** Auth is self-built (bcrypt + JWT +
  email OTP) — this was a deliberate choice, so `core/security.py` carries
  the full weight of getting this right.

## Bugs found and fixed by actually running this project

Caught by executing the code (imports, `TestClient` requests, and running
`seed_admin.py` end-to-end), not just reading it — listed here so you know
exactly what changed and why:

1. **Ambiguous foreign key between `User` and `Facility`.** These two
   tables reference each other two different ways (`User.facility_id` —
   which clinic a nurse belongs to — and `Facility.registered_by_admin_id`
   — which admin registered the clinic). SQLAlchemy couldn't infer which
   FK the `User.facility` / `Facility.staff` relationship should use.
   Fixed by adding explicit `foreign_keys=` to both relationship
   declarations in `models/user.py` and `models/facility.py`.
2. **`passlib` 1.7.4 is incompatible with `bcrypt` >= 4.1.** `passlib`
   hasn't been updated since 2020 and breaks on newer `bcrypt` internals.
   Fixed by pinning `bcrypt==4.0.1` in `requirements.txt`.
3. **`python-dotenv` was missing.** `pydantic-settings`'s `env_file=".env"`
   config silently does nothing without it — added to `requirements.txt`.

## Known open items (deliberately left for you to decide)

- **WHO Growth Standards**: `bmi_cross_check_malnutrition_status` in
  `clinical_math.py` uses placeholder BMI thresholds, explicitly flagged
  in the code. Replace with your organization's actual age/sex-specific
  reference tables before relying on it clinically.
- **Safeguarding visibility**: abuse/neglect-flagged referrals
  (`is_safeguarding_case="Yes"`) currently appear in the same admin
  dashboard as everything else. If your organization wants restricted
  visibility for these, that needs a sub-role and a filter — confirm with
  your safeguarding lead before building it.
- **Carbone template**: `CARBONE_REPORT_TEMPLATE_ID` must be created by
  uploading your actual FY25 xlsx to Carbone Studio and inserting
  `{d.field_name}` markers into the cells — that's a one-time manual setup
  step, not something this code can do for you.
- **Alembic migrations**: `create_all` is fine for now; switch before
  production data exists, so schema changes don't require a wipe.
