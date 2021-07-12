_**AlexFireChat**_
------------

Status of Last Deployment:<br>
<img src="https://github.com/AlexFire-Dev/AlexFireChat/workflows/CI/badge.svg?branch=main"><br>


### **_conf.env_**
`location - deploy/conf.env`


~~~~
PYTHONBUFFEERED=1

POSTGRES_USER={{ Имя пользователя postgres }}
POSTGRES_DB={{ БД postgres }}
POSTGRES_PASSWORD={{ Пароль БД postgres }}

REDIS_HOST=redis
REDIS_PORT=6379

SECRET_KEY={{ Секретный ключ django  }}
DB_USER={{ Имя пользователя postgres }}
DB_PASSWORD={{ Пароль БД postgres }}
DB_HOST=db
DB_PORT=5432
DB_NAME={{ БД postgres }}
DEBUG=0

EMAIL_HOST={{ Хост smtp }}
EMAIL_PORT={{ Порт smtp }}
EMAIL_USER={{ Пользователь почты }}
EMAIL_PASSWORD={{ Пароль почты }}
~~~~

________
