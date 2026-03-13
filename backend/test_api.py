from fastapi.testclient import TestClient
from backend.main import app
from backend import models
from backend.database import engine

# reset db
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

# basic smoke tests
r = client.post("/courses", json={"title":"Math 101","description":"Basic math"})
print('create course', r.status_code, r.json())

r2 = client.get("/courses")
print('list courses', r2.status_code, r2.json())

cid = r.json()['id']

en = client.post(f"/courses/{cid}/enroll", json={"name":"Alice","email":"alice@example.com"})
print('enroll', en.status_code, en.json())

asgn = client.post(f"/courses/{cid}/assignments", json={"title":"HW1","description":"desc","due_date":None})
print('assignment', asgn.status_code, asgn.json())

aid = asgn.json()['id']
sub = client.post(f"/assignments/{aid}/submissions", json={"student_id":en.json()['id'],"content":"answers"})
print('submission', sub.status_code, sub.json())

print('view submissions', client.get(f"/assignments/{aid}/submissions").json())

