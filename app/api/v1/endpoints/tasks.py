from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.core.security import get_current_user
from app.schemas.user import User
from app.schemas.task import TaskInDB, UserTaskInDB, UserTaskUpdate, UserTaskComplete
from app.repository.task import crud_task

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.get("/tasks/incomplete", response_model=list[TaskInDB])
async def get_incomplete_tasks(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Retrieve all tasks that the current user has not completed."""
    incomplete_tasks = await crud_task.get_incomplete_tasks_for_user(db, current_user.id)
    return incomplete_tasks

@router.post("/tasks/{task_id}/complete", response_model=UserTaskComplete)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Mark a task as completed for the current user and award rewards."""
    # Mark task as completed and award user
    user_task = await crud_task.mark_task_completed(db, current_user.id, task_id)
    
    if not user_task:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    
    return UserTaskComplete(
        id=user_task.id,
        status=user_task.status,
        user_id=user_task.user_id,
        task_id=user_task.task_id,
        last_completed_date=user_task.last_completed_date
    )
