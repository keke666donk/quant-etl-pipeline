from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
engine=create_engine("sqlite:///database_v2.db",echo=False)
SessionLocal=sessionmaker(bind=engine)
db_session=scoped_session(SessionLocal)