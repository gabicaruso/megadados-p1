from typing import Optional, List, Dict
from enum import Enum
from fastapi import FastAPI, Path, Body, Query
from pydantic import BaseModel, Field
import uuid

app = FastAPI()

fake_db = {}


class TaskIn(BaseModel):
    name: str = Field(
        description="Name of the task (user imput)",
    )
    description: str = Field(
        description="Description of the task (user imput)",
    )


class TaskOut(BaseModel):
    task_id: uuid.UUID = Field(
        description="Id of the task (UUID)",
    )
    name: str = Field(
        description="Name of the task",
    )
    description: str = Field(
        description="Description of the task",
    )
    status: bool = Field(
        description="Status of the task (done or not done yet)",
        example="True, False"
    )


class TaskInUpdate(BaseModel):
    description: str = Field(
        description="Description of the task",
    )
    status: bool = Field(
        description="Status of the task (done or not done yet)",
        example="True, False"
    )


class TaskStatusModel(str, Enum):
    done = "done"
    not_done = "not_done"


@app.get("/",
    summary="Root",
    description="Used to check if the network is running",)

def get_root():
    return {"Check": "Running"}


@app.post("/tasks",
    summary="Create Tasks",
    description="Used to create new tasks",
    response_description="New task",
    response_model=TaskOut)

async def create_task(task: TaskIn = Body(...)):

    global fake_db
    id = uuid.uuid4()

    task_out_db = TaskOut(**task.dict(), status=False, task_id=id)
    fake_db.update({id: task_out_db})

    return task_out_db


@app.get("/tasks_list/", 
    summary="Read Tasks",
    description="Used to consult the sistem in order to retrieve tasks on the dictionary",
    response_description="Dictionary containing all tasks based on the query parameter or returning all the tasks created if no query is sent",
    response_model=Dict[uuid.UUID, TaskOut])

async def read_task(q: Optional[TaskStatusModel] = Query(
        None,
        alias="status",
        title="Query filter based on status",
        description="Used to return only the tasks with the status in question or all of then if no status is sent",
        example="Example: done, not_done")):

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


@app.patch("/task_update/{task_id}",
    summary="Update Tasks",
    description="Used to update the description and the status of a task on the dictionary",
    response_description="Dictionary containing the altered task",
    response_model=TaskOut)
def update_item(*, task_id: uuid.UUID = Path(
    ..., 
    description="The ID of the task to be altered", 
    example= "Example: 3fa85f64-5717-4562-b3fc-2c963f66afa6"), 
    task: TaskInUpdate):
    
    global fake_db

    task_db = fake_db.get(task_id)
    update_data = task_db.dict()
    update_data.update(**task.dict())
    task_out = TaskOut(**update_data)
    fake_db.update({task_id: task_out})

    return task_out


@app.delete("/task_delete/{task_id}",
    summary="Delete Tasks",
    description="Used to delete a task on the dictionary",
    response_description="Dictionary containing all the remaining tasks",
    response_model=Dict[uuid.UUID, TaskOut])

def delete_task(*,task_id: uuid.UUID = Path(
    ..., 
    description="The ID of the task to be deleted", 
    example= "Example: 3fa85f64-5717-4562-b3fc-2c963f66afa6")):

    global fake_db
    task_db = fake_db.get(task_id)
    del fake_db[task_id]

    return fake_db