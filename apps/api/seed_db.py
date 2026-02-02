#!/usr/bin/env python3
"""Seed the database with initial course data."""
import sys
print("Starting seed script...", flush=True)

try:
    from app.database import SessionLocal
    print("Database import OK", flush=True)
except Exception as e:
    print(f"Database import failed: {e}", flush=True)
    sys.exit(1)

try:
    from app.models.course import University, Course
    print("Models import OK", flush=True)
except Exception as e:
    print(f"Models import failed: {e}", flush=True)
    sys.exit(1)

try:
    from app.data.seed_courses import get_all_courses, get_all_universities
    print("Seed data import OK", flush=True)
except Exception as e:
    print(f"Seed data import failed: {e}", flush=True)
    sys.exit(1)

def seed_database():
    """Seed the database with universities and courses."""
    db = SessionLocal()
    try:
        # Get seed data
        universities = get_all_universities()
        courses = get_all_courses()

        print(f"Seeding {len(universities)} universities...", flush=True)

        # Seed universities
        for uni_data in universities:
            existing = db.query(University).filter(University.id == uni_data["id"]).first()
            if existing:
                print(f"  University {uni_data['id']} already exists, skipping", flush=True)
                continue

            uni = University(
                id=uni_data["id"],
                name=uni_data["name"],
                short_name=uni_data["short_name"],
                course_pattern=uni_data.get("course_pattern"),
                gpa_scale=uni_data.get("gpa_scale", 4.0),
                uses_plus_minus=uni_data.get("uses_plus_minus", True),
                tier=uni_data.get("tier", 1),
                cs_ranking=uni_data.get("cs_ranking"),
            )
            db.add(uni)
            print(f"  Added university: {uni_data['name']}", flush=True)

        db.commit()
        print("Universities seeded.", flush=True)

        print(f"Seeding {len(courses)} courses...", flush=True)

        # Seed courses
        for course_data in courses:
            existing = db.query(Course).filter(Course.id == course_data["id"]).first()
            if existing:
                print(f"  Course {course_data['id']} already exists, skipping", flush=True)
                continue

            course = Course(
                id=course_data["id"],
                university_id=course_data["university_id"],
                department=course_data["department"],
                number=course_data["number"],
                name=course_data["name"],
                aliases=course_data.get("aliases"),
                difficulty_tier=course_data["difficulty_tier"],
                difficulty_score=course_data["difficulty_score"],
                typical_gpa=course_data.get("typical_gpa"),
                is_curved=course_data.get("is_curved", False),
                curve_type=course_data.get("curve_type"),
                course_type=course_data.get("course_type", "core"),
                is_technical=course_data.get("is_technical", True),
                is_weeder=course_data.get("is_weeder", False),
                is_proof_based=course_data.get("is_proof_based", False),
                has_heavy_projects=course_data.get("has_heavy_projects", False),
                has_coding=course_data.get("has_coding", False),
                units=course_data.get("units", 3),
                prerequisites=course_data.get("prerequisites"),
                relevant_to=course_data.get("relevant_to"),
                equivalents=course_data.get("equivalents"),
                description=course_data.get("description"),
                confidence=course_data.get("confidence", 1.0),
                source=course_data.get("source", "research"),
            )
            db.add(course)
            print(f"  Added course: {course_data['id']}", flush=True)

        db.commit()
        print("Courses seeded.", flush=True)

        # Print summary
        uni_count = db.query(University).count()
        course_count = db.query(Course).count()
        print(f"\nDatabase now has {uni_count} universities and {course_count} courses.", flush=True)

    except Exception as e:
        print(f"Error seeding database: {e}", flush=True)
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
    print("Done!", flush=True)
