import time
from celery_main import celery_app


@celery_app.task(name="send_order_email")
def send_order_email(order_id: int, client_email: str):
   """Имитация отправки email. В реальности — SMTP или внешний сервис."""
   print(f"[CELERY] Отправка email для заказа #{order_id} на {client_email}")
   time.sleep(2)   # имитация долгой операции
   print(f"[CELERY] Email для заказа #{order_id} отправлен")
   return {"order_id": order_id, "status": "sent"}

