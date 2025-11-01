from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class Meal(Base):
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    meal_type = Column(String)
    description = Column(String)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    created_at = Column(String)

class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self._init_db()

    def _init_db(self):
        Base.metadata.create_all(self.engine)
        logger.info("Database initialized")

    def save_meal(self, meal_data: dict) -> int:
        session = self.Session()
        try:
            meal = Meal(
                date=datetime.now().strftime("%Y-%m-%d"),
                meal_type=meal_data['meal_type'],
                description=meal_data['description'],
                calories=meal_data['calories'],
                protein=meal_data['protein'],
                fat=meal_data['fat'],
                carbs=meal_data['carbs'],
                created_at=datetime.now().isoformat()
            )
            session.add(meal)
            session.commit()
            return meal.id
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
