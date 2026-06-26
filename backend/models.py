from datetime import date, datetime
import bcrypt
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    xp = db.Column(db.Integer, default=0)              # 👈 naya field

    habits = db.relationship("Habit", backref="owner", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password_hash.encode("utf-8"))

    @property
    def level(self):
        # Har level ke liye XP requirement badhta jaata hai (RPG-style curve)
        import math
        return int(math.sqrt(self.xp / 50)) + 1

    @property
    def xp_for_next_level(self):
        next_level = self.level + 1
        return 50 * (next_level - 1) ** 2

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "xp": self.xp,
            "level": self.level,
            "xp_for_next_level": self.xp_for_next_level,
        }

class Habit(db.Model):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), default="general")
    created_at = db.Column(db.Date, default=date.today)
    is_active = db.Column(db.Boolean, default=True)

    checkins = db.relationship(
        "CheckIn",
        backref="habit",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def to_dict(self, with_stats=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }

        if with_stats:
            total = self.checkins.count()
            avg_mood = db.session.query(
                db.func.avg(CheckIn.mood)
            ).filter(
                CheckIn.habit_id == self.id
            ).scalar()

            data["total_checkins"] = total
            data["avg_mood"] = round(float(avg_mood), 2) if avg_mood else None

        return data


class CheckIn(db.Model):
    __tablename__ = "checkins"

    __table_args__ = (
        db.UniqueConstraint(
            "habit_id",
            "done_on",
            name="uq_habit_day"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    habit_id = db.Column(
        db.Integer,
        db.ForeignKey("habits.id"),
        nullable=False,
        index=True
    )

    done_on = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    mood = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "done_on": self.done_on.isoformat(),
            "mood": self.mood,
            "note": self.note,
        }