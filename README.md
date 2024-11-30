Migrations:

alembic revision --autogenerate -m "New tables"
alembic upgrade head


uvicorn app.main:app --host droppu.ru --port 7777 --ssl-keyfile /home/admin/conf/web/droppu.ru/ssl/droppu.ru.key --ssl-certfile /home/admin/conf/web/droppu.ru/ssl/droppu.ru.crt --ssl-ca-certs /home/admin/conf/web/droppu.ru/ssl/droppu.ru.pem --reload