from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.core.security import TokenData, get_current_user
from app.db.session import async_session
from app.models.payment import Payment
from app.models.user import User
from app.models.earnings import Earning
from aiogram import Bot
from aiogram.types import LabeledPrice
import asyncio

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

API_TOKEN = '7711734873:AAHOnxncCEo5e2mFOioc8P530lHg-Y8I0hs'

bot = Bot(token=API_TOKEN)

@router.post("/payments/create-invoice")
async def create_invoice(
    amount: float,
    description: str,
    db: AsyncSession = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user)
):
    """
    Create payment invoice through Telegram Stars
    """
    # Get full user object
    user_result = await db.execute(select(User).where(User.id == current_user_token.id))
    current_user = user_result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        prices = [LabeledPrice(label='XTR', amount=int(amount))]

        # Create invoice
        invoice_link = await bot.create_invoice_link(
            title='DROPPU Stars',
            description=description,
            provider_token='',
            currency='XTR', 
            prices=prices,
            payload='stars-payment-payload'
        )

        print(invoice_link)
        # Save payment to database
        new_payment = Payment(
            user_id=current_user.id,
            invoice_id=str(invoice_link).replace('https://t.me/', ''),
            amount=amount,
            currency='XTR',
            status='pending'
        )
        db.add(new_payment)
        await db.commit()

        return {
            "success": True,
            "payment_url": invoice_link
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating invoice: {str(e)}"
        )

@router.post("/payments/{invoice_id}/paid")
async def payment_paid(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user)
):
    """Handle successful payment"""
    # Get payment record
    payment = await db.execute(
        select(Payment).where(
            Payment.invoice_id == invoice_id,
            Payment.status == 'pending'
        )
    )
    payment = payment.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found or already processed")

    # Get user
    user = await db.get(User, payment.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Update payment status
        payment.status = 'paid'
        payment.completed_at = datetime.utcnow()


        await db.commit()

        return {
            "success": True,
            "status": "paid"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing payment: {str(e)}"
        )

@router.post("/payments/{invoice_id}/cancelled")
async def payment_cancelled(
    invoice_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle cancelled payment"""
    payment = await db.execute(
        select(Payment).where(
            Payment.invoice_id == invoice_id,
            Payment.status == 'pending'
        )
    )
    payment = payment.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found or already processed")

    try:
        payment.status = 'cancelled'
        payment.completed_at = datetime.utcnow()
        await db.commit()

        return {
            "success": True,
            "status": "cancelled"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelling payment: {str(e)}"
        )

@router.post("/payments/{invoice_id}/failed")
async def payment_failed(
    invoice_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle failed payment"""
    payment = await db.execute(
        select(Payment).where(
            Payment.invoice_id == invoice_id,
            Payment.status == 'pending'
        )
    )
    payment = payment.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found or already processed")

    try:
        payment.status = 'failed'
        payment.completed_at = datetime.utcnow()
        await db.commit()

        return {
            "success": True,
            "status": "failed"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing failed payment: {str(e)}"
        )

@router.get("/payments/{invoice_id}/status")
async def get_payment_status(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_token: TokenData = Depends(get_current_user)
):
    """Get payment status"""
    payment = await db.execute(
        select(Payment).where(Payment.invoice_id == invoice_id)
    )
    payment = payment.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.user_id != current_user_token.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "invoice_id": payment.invoice_id,
        "status": payment.status,
        "amount": payment.amount,
        "created_at": payment.created_at,
        "completed_at": payment.completed_at
    }