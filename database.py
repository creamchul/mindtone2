from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 URL 설정
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///mindtone.db')

# 엔진 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 초기화
def init_db():
    Base.metadata.create_all(bind=engine)

# 데이터베이스 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 비밀번호 해싱
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    ) 