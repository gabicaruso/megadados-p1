from typing import Optional, List, Dict
from enum import Enum
from fastapi import FastAPI, Query
from pydantic import BaseModel

import uuid

app = FastAPI()

fake_db = {}


class TaskIn(BaseModel):
    name: str
    description: str


class TaskOut(BaseModel):
    task_id: uuid.UUID
    name: str
    description: str
    status: bool


class TaskStatusModel(str, Enum):
    done = "done"
    not_done = "not_done"


@app.get("/")
def get_root():
    return {"Hello": "World"}


@app.post("/tasks", response_model=TaskOut)
async def create_task(task: TaskIn):
    global fake_db
    id = uuid.uuid4()
    task_out_db = TaskOut(**task.dict(), status=False, task_id=id)
    fake_db.update({id: task_out_db})
    return task_out_db


@app.get("/tasks_list", response_model=Dict[uuid.UUID, TaskOut])
async def read_task(q: Optional[TaskStatusModel] = Query(None)):
    global fake_db
    q_dict = {}
    if q != None:
        for task in fake_db.values():
            if task.status and q == TaskStatusModel.done:
                q_dict.update({task.task_id: task})
            elif not task.status and q == TaskStatusModel.not_done:
                q_dict.update({task.task_id: task})
        return q_dict
    else:
        return fake_db


@app.put("/tasks/{task_id}")
def update_item(task_id: uuid.UUID, task: TaskOut):
    global fake_db

    # task_db = fake_db.get(task_id)
    # fake_db.update({task_db.id: task})

    for tasks in list(fake_db.values()):
        if tasks.task_id == task_id:
            fake_db["name"] = task.name
            fake_db["description"] = task.description
            fake_db["status"] = task.status
    #               fake_db.update({"taskid": tasks.taskid,
    #               "name": tasks.name,
    #               "description": tasks.description,
    #               "status": tasks.status})

        print(fake_db.values())

    return task