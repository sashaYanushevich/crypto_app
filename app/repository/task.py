from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models.user_tasks import UserTask
from app.models.tasks import Task
from sqlalchemy.orm import aliased
from app.models.user import User
from sqlalchemy.orm import joinedload
from app.repository.referral import crud_referral
from app.models.earnings import Earning
from typing import Optional


class CRUDTask:
    async def get_incomplete_tasks_for_user(self, db: AsyncSession, user_id: int):
        """Retrieve all tasks that the user has not completed."""
        ut = aliased(UserTask)

        result = await db.execute(
            select(Task)
            .outerjoin(ut, (ut.task_id == Task.id) & (ut.user_id == user_id))
            .where(ut.id == None)  # Only include tasks without a user task entry
        )
        return result.scalars().all()

    async def mark_task_completed(
        self, 
        db: AsyncSession, 
        user_id: int, 
        task_id: int
    ) -> Optional[UserTask]:
        # Проверяем существование задачи
        task_result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = task_result.scalar_one_or_none()
        if not task:
            return None

        # Проверяем существование или создаем запись UserTask
        user_task_result = await db.execute(
            select(UserTask).where(
                UserTask.user_id == user_id,
                UserTask.task_id == task_id
            )
        )
        user_task = user_task_result.scalar_one_or_none()

        if not user_task:
            user_task = UserTask(
                user_id=user_id,
                task_id=task_id,
                status='completed',
                last_completed_date=datetime.utcnow()
            )
            db.add(user_task)
        else:
            user_task.status = 'completed'
            user_task.last_completed_date = datetime.utcnow()

        # Награждаем пользователя
        await self.award_user_for_task(db, user_id, task_id)
        
        await db.commit()
        await db.refresh(user_task)
        
        return user_task

    async def award_user_for_task(self, db: AsyncSession, user_id: int, task_id: int):
        """Award the user with coins, tokens, and tickets for completing a task."""
        # Retrieve the task rewards
        task_result = await db.execute(select(Task).where(Task.id == task_id))
        task = task_result.scalar_one_or_none()

        # Retrieve the user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if task and user:
            # Update user's rewards
            user.coins += task.reward_coins
            user.tokens += task.reward_tokens
            user.tickets += task.reward_tickets

            # Create earnings record
            earning = Earning(
                user_id=user_id,
                amount=task.reward_coins,
                currency='coins',
                source_type='task_completion',
                source_id=task_id
            )
            db.add(earning)

            # Process referral rewards if user has a referrer
            if user.parent_id:
                await crud_referral.process_referral_rewards(
                    db, 
                    user.parent_id, 
                    user_id, 
                    task.reward_coins
                )

            await db.commit()
            await db.refresh(user)
            return user
        return None

crud_task = CRUDTask()
