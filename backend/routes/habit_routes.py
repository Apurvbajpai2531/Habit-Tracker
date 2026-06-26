from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError

from extensions import db
from models import Habit, CheckIn
from utils import success, error, handle_validation_errors

habit_bp = Blueprint("habits", __name__, url_prefix="/api/habits")


class HabitSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    category = fields.Str(required=False, load_default="general")


class CheckInSchema(Schema):
    mood = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    note = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))


habit_schema = HabitSchema()
checkin_schema = CheckInSchema()


def _owned_habit_or_404(habit_id, user_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return None
    return habit


@habit_bp.get("")
@jwt_required()
def list_habits():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    query = Habit.query.filter_by(user_id=user_id, is_active=True).order_by(Habit.id.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return success({
        "items": [h.to_dict(with_stats=True) for h in paginated.items],
        "page": page,
        "total_pages": paginated.pages,
        "total_items": paginated.total,
    })


@habit_bp.post("")
@jwt_required()
@handle_validation_errors
def create_habit():
    user_id = int(get_jwt_identity())
    payload = habit_schema.load(request.get_json(force=True))

    habit = Habit(name=payload["name"], category=payload["category"], user_id=user_id)
    db.session.add(habit)
    db.session.commit()
    return success(habit.to_dict(), "Habit created", 201)


@habit_bp.delete("/<int:habit_id>")
@jwt_required()
def delete_habit(habit_id):
    user_id = int(get_jwt_identity())
    habit = _owned_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit nahi mila", 404)

    habit.is_active = False   # soft delete — history preserve rehti hai
    db.session.commit()
    return success(message="Habit removed")


@habit_bp.post("/<int:habit_id>/checkin")
@jwt_required()
@handle_validation_errors
def checkin(habit_id):
    from models import User
    user_id = int(get_jwt_identity())
    habit = _owned_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit nahi mila", 404)

    payload = checkin_schema.load(request.get_json(force=True))
    user = User.query.get(user_id)

    existing = CheckIn.query.filter_by(habit_id=habit_id, done_on=date.today()).first()
    if existing:
        existing.mood = payload["mood"]
        existing.note = payload.get("note")
        db.session.commit()
        return success(existing.to_dict(), "Aaj ka check-in update hua")

    entry = CheckIn(habit_id=habit_id, mood=payload["mood"], note=payload.get("note"))
    db.session.add(entry)

    # ---- XP logic: base 10 XP + streak bonus + mood bonus ----
    from utils import calculate_streaks
    all_dates = [c.done_on for c in habit.checkins.all()] + [date.today()]
    current_streak, _ = calculate_streaks(all_dates)

    base_xp = 10
    streak_bonus = min(current_streak * 2, 50)   # max 50 bonus XP
    mood_bonus = payload["mood"] * 2
    earned_xp = base_xp + streak_bonus + mood_bonus

    old_level = user.level
    user.xp += earned_xp
    new_level = user.level
    leveled_up = new_level > old_level

    db.session.commit()

    response_data = entry.to_dict()
    response_data["earned_xp"] = earned_xp
    response_data["total_xp"] = user.xp
    response_data["level"] = new_level
    response_data["leveled_up"] = leveled_up

    return success(response_data, "Check-in saved", 201)


@habit_bp.get("/<int:habit_id>/checkins")
@jwt_required()
def get_checkins(habit_id):
    user_id = int(get_jwt_identity())
    habit = _owned_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit nahi mila", 404)

    entries = habit.checkins.order_by(CheckIn.done_on).all()
    return success([e.to_dict() for e in entries])

@habit_bp.get("/leaderboard")
@jwt_required()
def leaderboard():
    from models import User
    top_users = User.query.order_by(User.xp.desc()).limit(10).all()
    return success([
        {"email": u.email[:3] + "***", "xp": u.xp, "level": u.level}  # privacy: email partially hidden
        for u in top_users
    ])

@habit_bp.get("/<int:habit_id>/insights")
@jwt_required()
def get_insights(habit_id):
    import statistics
    from collections import defaultdict

    user_id = int(get_jwt_identity())
    habit = _owned_habit_or_404(habit_id, user_id)
    if not habit:
        return error("Habit nahi mila", 404)

    entries = habit.checkins.order_by(CheckIn.done_on).all()
    insights = []

    if len(entries) < 3:
        return success({"insights": ["Insights dekhne ke liye kam se kam 3 check-ins chahiye."]})

    # 1) Best day of week (consistency pattern)
    day_counts = defaultdict(int)
    day_moods = defaultdict(list)
    for e in entries:
        day_name = e.done_on.strftime("%A")
        day_counts[day_name] += 1
        day_moods[day_name].append(e.mood)

    best_day = max(day_counts, key=day_counts.get)
    insights.append(f"📅 Tum is habit ko sabse zyada **{best_day}** ke din follow karte ho ({day_counts[best_day]} baar).")

    # 2) Best mood day
    avg_mood_by_day = {d: round(statistics.mean(m), 1) for d, m in day_moods.items() if len(m) >= 1}
    if avg_mood_by_day:
        happiest_day = max(avg_mood_by_day, key=avg_mood_by_day.get)
        insights.append(f"😊 **{happiest_day}** ko tumhara mood sabse better rehta hai (avg {avg_mood_by_day[happiest_day]}/5).")

    # 3) Mood trend (improving / declining / stable)
    moods = [e.mood for e in entries]
    if len(moods) >= 6:
        first_half_avg = statistics.mean(moods[: len(moods) // 2])
        second_half_avg = statistics.mean(moods[len(moods) // 2 :])
        diff = second_half_avg - first_half_avg
        if diff > 0.3:
            insights.append(f"📈 Tumhara mood is habit me **improve** ho raha hai ({first_half_avg:.1f} → {second_half_avg:.1f}).")
        elif diff < -0.3:
            insights.append(f"📉 Tumhara mood thoda **decline** kar raha hai ({first_half_avg:.1f} → {second_half_avg:.1f}). Kya kuch badal gaya hai?")
        else:
            insights.append("➡️ Mood consistent hai, koi major change nahi.")

    # 4) Consistency score
    from utils import calculate_streaks
    dates = [e.done_on for e in entries]
    current_streak, longest_streak = calculate_streaks(dates)
    total_days_span = (dates[-1] - dates[0]).days + 1
    consistency_pct = round((len(set(dates)) / total_days_span) * 100, 1) if total_days_span > 0 else 100

    insights.append(f"🎯 Consistency score: **{consistency_pct}%** ({len(set(dates))} check-ins / {total_days_span} din).")

    if current_streak == 0 and longest_streak > 2:
        insights.append(f"⚠️ Tumhara streak toot gaya hai. Best streak tha **{longest_streak} din** — wapas try karo!")

    return success({"insights": insights, "consistency_pct": consistency_pct})