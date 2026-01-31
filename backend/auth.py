import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta

# Секретный ключ и алгоритм для токена
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Функция для создания токена
def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(hours=1)  # Время истечения токена
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для верификации токена
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Зависимость для извлечения токена из заголовка
def get_jwt_token(authorization: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    if authorization is None:
        raise HTTPException(status_code=403, detail="Not authorized")
    return authorization
