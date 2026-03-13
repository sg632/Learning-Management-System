from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models
from .database import engine, get_db
from pydantic import BaseModel

# create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Learning Management System API")


# --- Pydantic schemas -------------------------------------------------------

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None


class CourseOut(CourseCreate):
    id: int

    class Config:
        orm_mode = True


class StudentCreate(BaseModel):
    name: str
    email: str


class StudentOut(StudentCreate):
    id: int

    class Config:
        orm_mode = True


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class AssignmentOut(AssignmentCreate):
    id: int
    course_id: int

    class Config:
        orm_mode = True


class SubmissionCreate(BaseModel):
    student_id: int
    content: str


class SubmissionOut(BaseModel):
    id: int
    student: StudentOut
    content: str
    submitted_at: datetime

    class Config:
        orm_mode = True


# --- course endpoints ------------------------------------------------------

@app.post("/courses", response_model=CourseOut)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@app.get("/courses", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()


# --- enrollment -------------------------------------------------------------

@app.post("/courses/{course_id}/enroll", response_model=StudentOut)
def enroll_student(course_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = db.query(models.Student).filter(models.Student.email == student.email).first()
    if existing is None:
        existing = models.Student(**student.dict())
        db.add(existing)
        db.commit()
        db.refresh(existing)

    # avoid duplicate enrollments
    already = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.course_id == course_id, models.Enrollment.student_id == existing.id)
        .first()
    )
    if already:
        return existing

    enrollment = models.Enrollment(course_id=course_id, student_id=existing.id)
    db.add(enrollment)
    db.commit()
    return existing


# --- assignments -----------------------------------------------------------

@app.post("/courses/{course_id}/assignments", response_model=AssignmentOut)
def create_assignment(course_id: int, assignment: AssignmentCreate, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db_assignment = models.Assignment(course_id=course_id, **assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


@app.get("/courses/{course_id}/assignments", response_model=List[AssignmentOut])
def list_assignments(course_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Assignment)
        .filter(models.Assignment.course_id == course_id)
        .all()
    )


# --- submissions -----------------------------------------------------------

@app.post("/assignments/{assignment_id}/submissions", response_model=SubmissionOut)
def submit_assignment(assignment_id: int, submission: SubmissionCreate, db: Session = Depends(get_db)):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    student = db.query(models.Student).get(submission.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db_sub = models.Submission(
        assignment_id=assignment_id,
        student_id=submission.student_id,
        content=submission.content,
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


@app.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionOut])
def view_submissions(assignment_id: int, db: Session = Depends(get_db)):
    subs = (
        db.query(models.Submission)
        .filter(models.Submission.assignment_id == assignment_id)
        .all()
    )
    return subs

