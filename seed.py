from datetime import date

from sqlmodel import select

from app.database import ensure_db_and_tables, get_cli_session
from app.models.event import Event, EventHost
from app.models.user import User
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.schemas.event import EventCreate
from app.schemas.user import AdminCreate, RegularUserCreate
from app.utilities.security import encrypt_password


users = [
    ("bob", "bob@example.com", "bobpass", "regular_user", "Bob", "Johnson", None, "Computer Science", "Alumni interested in networking events"),
    ("admin", "admin@example.com", "adminpass", "admin", "Admin", "User", None, "Administration", "System administrator"),
    ("prof_smith", "prof.smith@uwi.edu", "profsmitpass", "professor", "Jane", "Smith", None, "Computer Science", "Professor of Software Engineering"),
    ("prof_williams", "prof.williams@uwi.edu", "profwillpass", "professor", "Michael", "Williams", None, "Mathematics", "Professor of Data Science"),
    ("prof_brown", "prof.brown@uwi.edu", "profbrownpass", "professor", "Alicia", "Brown", None, "Information Systems", "Lecturer in digital transformation"),
    ("prof_clarke", "prof.clarke@uwi.edu", "profclarkepass", "professor", "Daniel", "Clarke", None, "Electrical Engineering", "Lecturer in robotics and embedded systems"),
    ("prof_morgan", "prof.morgan@uwi.edu", "profmorganpass", "professor", "Priya", "Morgan", None, "Business", "Lecturer in entrepreneurship and innovation"),
    ("alumni_jones", "jones.alumni@example.com", "jonespass", "alumni", "Sarah", "Jones", 2022, "Computer Science", "Software Developer at TechCorp"),
    ("alumni_lee", "lee.alumni@example.com", "leepass", "alumni", "David", "Lee", 2021, "Information Systems", "Data Analyst"),
    ("alumni_patel", "patel.alumni@example.com", "patelpass", "alumni", "Nadia", "Patel", 2023, "Business", "Product coordinator"),
    ("alumni_thomas", "thomas.alumni@example.com", "thomaspass", "alumni", "Andre", "Thomas", 2020, "Electrical Engineering", "Network engineer"),
    ("alumni_wilson", "wilson.alumni@example.com", "wilsonpass", "alumni", "Maya", "Wilson", 2019, "Mathematics", "Quantitative analyst"),
    ("alumni_garcia", "garcia.alumni@example.com", "garciapass", "alumni", "Elena", "Garcia", 2024, "Computer Science", "Junior backend developer"),
    ("alumni_bennett", "bennett.alumni@example.com", "bennettpass", "alumni", "Joshua", "Bennett", 2018, "Business", "Operations manager"),
    ("alumni_roberts", "roberts.alumni@example.com", "robertspass", "alumni", "Tiana", "Roberts", 2022, "Information Systems", "UX researcher"),
    ("alumni_khan", "khan.alumni@example.com", "khanpass", "alumni", "Omar", "Khan", 2021, "Electrical Engineering", "IoT consultant"),
    ("alumni_campbell", "campbell.alumni@example.com", "campbellpass", "alumni", "Leah", "Campbell", 2023, "Mathematics", "Actuarial analyst"),
]

connections = [
    ("alumni_jones", "alumni_lee"),
    ("alumni_jones", "alumni_garcia"),
    ("alumni_lee", "alumni_patel"),
    ("alumni_patel", "alumni_bennett"),
    ("alumni_thomas", "alumni_khan"),
    ("alumni_thomas", "prof_clarke"),
    ("alumni_wilson", "prof_williams"),
    ("alumni_garcia", "prof_smith"),
    ("alumni_roberts", "prof_brown"),
    ("alumni_campbell", "prof_morgan"),
    ("prof_smith", "prof_williams"),
]

events = [
    ("Tech Career Fair", "Meet technology employers and explore opportunities.", date(2026, 11, 20), "10:00", "Main Auditorium", "career, technology, networking", "prof_smith", ["prof_brown"]),
    ("Data Science Workshop", "Practical machine learning workshop.", date(2026, 11, 28), "14:00", "Computer Lab 2", "data, machine learning, workshop", "prof_williams", ["prof_smith"]),
    ("Alumni Mixer", "An evening for graduates and students to reconnect.", date(2026, 12, 10), "18:00", "Student Lounge", "networking, social, alumni", "prof_morgan", ["prof_smith"]),
    ("Innovation and Startup Panel", "Alumni founders discuss building businesses.", date(2027, 1, 15), "16:00", "Business School Theatre", "entrepreneurship, startups", "prof_morgan", ["prof_brown"]),
    ("Robotics Demonstration Day", "Student robotics projects and career discussion.", date(2027, 1, 29), "11:00", "Engineering Atrium", "robotics, engineering", "prof_clarke", ["prof_williams"]),
    ("Women in Technology Breakfast", "Networking breakfast for women in technology.", date(2027, 2, 12), "08:30", "Conference Centre", "women, technology, networking", "prof_brown", ["prof_smith"]),
    ("Analytics for Business Seminar", "Using dashboards and evidence for decisions.", date(2027, 2, 26), "13:00", "Business Lab", "analytics, business", "prof_williams", ["prof_morgan"]),
    ("Mentorship Meet and Greet", "Connect graduates with alumni and faculty mentors.", date(2027, 3, 12), "17:30", "Alumni House", "mentorship, alumni", "prof_smith", ["prof_brown", "prof_morgan"]),
    ("Cybersecurity Careers Q&A", "Questions and answers with security practitioners.", date(2027, 3, 26), "15:00", "Science Lecture Hall", "cybersecurity, careers", "prof_clarke", ["prof_smith"]),
    ("Research Showcase", "Faculty and alumni research presentations.", date(2027, 4, 9), "12:00", "Research Commons", "research, collaboration", "prof_morgan", ["prof_williams", "prof_clarke"]),
]

ensure_db_and_tables()
user_map = {}

with get_cli_session() as session:
    repo = UserRepository(session)

    for row in users:
        username, email, password, role, first, last, year, department, description = row
        existing = repo.get_by_username(username)

        if existing:
            user_map[username] = existing
            print(f"skip user: {username}")
            continue

        payload = AdminCreate if role == "admin" else RegularUserCreate
        user_map[username] = repo.create(
            payload(
                username=username,
                email=email,
                password=encrypt_password(password),
                role=role,
                firstname=first,
                lastname=last,
                yeargraduated=year,
                department=department,
                profile_description=description,
            )
        )
        print(f"created user: {username}")

with get_cli_session() as session:
    repo = UserRepository(session)

    for left_name, right_name in connections:
        left = user_map[left_name]
        right = user_map[right_name]

        if left.id and right.id:
            repo.connect_users(left.id, right.id)
            repo.connect_users(right.id, left.id)

with get_cli_session() as session:
    event_repo = EventRepository(session)

    for title, description, event_date, event_time, location, keywords, primary_name, extra_names in events:
        primary = user_map[primary_name]
        existing = session.exec(
            select(Event).where(Event.event_title == title)
        ).first()

        if existing:
            event = existing
            print(f"skip event: {title}")
        else:
            event = event_repo.create_for_user(
                EventCreate(
                    event_title=title,
                    description=description,
                    event_date=event_date,
                    time=event_time,
                    location=location,
                    keywords=keywords,
                ),
                primary.id,
            )
            print(f"created event: {title}")

        host_names = [primary_name, *extra_names]
        existing_host_ids = {
            host.userid
            for host in session.exec(
                select(EventHost).where(EventHost.eventid == event.eventid)
            ).all()
        }

        for host_name in host_names:
            host = user_map[host_name]
            if host.id not in existing_host_ids:
                session.add(EventHost(eventid=event.eventid, userid=host.id))

        session.commit()

print("Seeding complete.")