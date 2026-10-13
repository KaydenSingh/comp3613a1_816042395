from app.database import ensure_db_and_tables, get_cli_session
from app.repositories.user import UserRepository
from app.repositories.event import EventRepository
from app.schemas.user import AdminCreate, RegularUserCreate
from app.schemas.event import EventCreate
from app.utilities.security import encrypt_password
from datetime import date

ensure_db_and_tables()

demo_users = [
    ("bob", "bob@example.com", "bobpass", "regular_user", "Bob", "Johnson", None, "Computer Science", "Alumni interested in networking events"),
    ("admin", "admin@example.com", "adminpass", "admin", "Admin", "User", None, "Administration", "System administrator"),
    ("prof_smith", "prof.smith@uwi.edu", "profsmitpass", "professor", "Jane", "Smith", None, "Computer Science", "Professor of Software Engineering"),
    ("prof_williams", "prof.williams@uwi.edu", "profwillpass", "professor", "Michael", "Williams", None, "Mathematics", "Professor of Data Science"),
    ("alumni_jones", "jones.alumni@example.com", "jonespass", "alumni", "Sarah", "Jones", 2022, "Computer Science", "Software Developer at TechCorp"),
    ("alumni_lee", "lee.alumni@example.com", "leepass", "alumni", "David", "Lee", 2021, "Information Systems", "Data Analyst"),
]

created = 0
skipped = 0
with get_cli_session() as session:
    repo = UserRepository(session)
    for user_info in demo_users:
        if len(user_info) == 9:
            username, email, password, role, firstname, lastname, yeargrad, dept, desc = user_info
        else:
            username, email, password, role = user_info[:4]
            firstname, lastname, yeargrad, dept, desc = "", "", None, "", ""
        if repo.get_by_username(username):
            print(f"skip {username}")
            skipped += 1
            continue
        payload_cls = AdminCreate if role == "admin" else RegularUserCreate
        try:
            user = payload_cls(
                username=username,
                email=email,
                password=encrypt_password(password),
                role=role,
                firstname=firstname,
                lastname=lastname,
                yeargraduated=yeargrad,
                department=dept,
                profile_description=desc,
            )
            repo.create(user)
            print(f"create {username}")
            created += 1
        except Exception as e:
            print(f"err {username}: {e}")

# seed events
with get_cli_session() as s:
    urepo = UserRepository(s)
    erepo = EventRepository(s)
    profs = []
    for name in ['prof_smith', 'prof_williams']:
        p = urepo.get_by_username(name)
        if p:
            profs.append(p)
    events = [
        ('Tech Career Fair', 'Meet top tech companies and explore opportunities', date(2026,11,15), '10:00', 'Main Auditorium', 'career, tech, networking', profs[0].id if profs else 2),
        ('Data Science Workshop', 'Hands-on workshop on ML fundamentals', date(2026,11,28), '14:00', 'Computer Lab', 'data, ml, workshop', profs[1].id if len(profs)>1 else (profs[0].id if profs else 2)),
        ('Alumni Mixer', 'Casual networking event for all alumni', date(2026,12,10), '18:00', 'Student Lounge', 'networking, social, alumni', profs[0].id if profs else 2),
    ]
    for e in events:
        try:
            erepo.create_for_user(EventCreate(event_title=e[0], description=e[1], event_date=e[2], time=e[3], location=e[4], keywords=e[5]), e[6])
            print(f"event ok: {e[0]}")
        except Exception as ex:
            print(ex)

print(f"done: created={created} skipped={skipped}")
