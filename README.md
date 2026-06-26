# ✅ Habit + Mood Tracker

Ek chhota lekin fully working full-stack project — **100% Python** (frontend + backend), **PostgreSQL** database ke saath, **Docker** se containerized, aur **GitHub Actions** se CI/CD automated.

Idea simple hai: roz apne habits (jaise gym, padhai, paani peena) check-in karo aur saath me apna mood (1-5) record karo. App tumhe chart me dikhata hai ki konsa habit follow karne se mood kaisa rehta hai.

---

## 🧱 Tech Stack (sab Python hai)

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Frontend     | Streamlit (Python based UI, responsive) |
| Backend/API  | Flask + Flask-SQLAlchemy             |
| Database     | PostgreSQL                          |
| Containers   | Docker + docker-compose             |
| CI/CD        | GitHub Actions                      |

---

## 📁 Folder Structure

```
habit-tracker/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── models.py           # SQLAlchemy models (Habit, CheckIn)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py              # Streamlit UI
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml       # Backend + Frontend + Postgres ek saath chalane ke liye
└── .github/workflows/
    └── ci-cd.yml            # CI/CD pipeline
```

---

## 🚀 Project ko local mein chalana (bina Docker ke)

Agar Docker use nahi karna, sirf samajhna hai ki normal Python project kaise chalta hai:

```bash
# 1. Backend chalao
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://habit_user:habit_pass@localhost:5432/habit_db
python app.py        # http://localhost:5000 par chalega

# 2. Naye terminal mein Frontend chalao
cd frontend
pip install -r requirements.txt
export API_URL=http://localhost:5000
streamlit run app.py  # http://localhost:8501 par khulega
```

Iske liye tumhare paas pehle se local Postgres install hona chahiye. Isi wajah se **Docker** use karna easy hai — neeche dekho.

---

## 🐳 Docker samjho (step-by-step)

### Docker hai kya?
Docker ek tool hai jo tumhare app ko ek **container** (apna khud ka chhota isolated environment) mein pack kar deta hai — jisme Python, libraries, aur code sab kuch already setup hota hai. Isse "mere system pe chal raha tha but tumhare system pe nahi chal raha" wali problem khatam ho jaati hai.

### Dockerfile kya kar raha hai?
Har service (`backend` aur `frontend`) ke andar ek `Dockerfile` hai. Ye basically ek **recipe** hai:

```dockerfile
FROM python:3.12-slim     # Step 1: Python wala base image lo
WORKDIR /app              # Step 2: container ke andar /app folder banao
COPY requirements.txt .   # Step 3: requirements file copy karo
RUN pip install -r requirements.txt   # Step 4: dependencies install karo
COPY . .                  # Step 5: baki saara code copy karo
EXPOSE 5000                # Step 6: yeh port use hoga
CMD ["gunicorn", ...]     # Step 7: container start hote hi yeh command chalegi
```

Yani: "Python install karo → libraries install karo → code daalo → app start karo." Yehi 7 lines ek complete server bana deti hain.

### docker-compose.yml kya kar raha hai?
Hamare project mein 3 alag-alag services hain: `db` (Postgres), `backend` (Flask), `frontend` (Streamlit). Inhe ek-ek karke manually chalana mushkil hai, isliye `docker-compose.yml` sabko **ek command se** chalata hai aur ek dusre se connect bhi kar deta hai (jaise backend ko pata hota hai db kahaan hai — naam se, IP yaad rakhne ki zaroorat nahi).

### Chalane ka command

```bash
# Project ke root folder (jahan docker-compose.yml hai) mein:
docker compose up --build
```

Isse kya hota hai:
1. `db` service start hoti hai (Postgres database) — data `db_data` volume mein save hota hai, container restart hone par bhi data nahi udega.
2. Jab tak db "healthy" nahi hoti, `backend` wait karta hai (`depends_on: condition: service_healthy`).
3. `backend` apna Flask server start karta hai port `5000` par.
4. `frontend` (Streamlit) start hota hai port `8501` par, aur backend se `http://backend:5000` ke through baat karta hai.

Browser mein khol kar dekho:
- Frontend (App UI): **http://localhost:8501**
- Backend API: **http://localhost:5000/api/health**

Band karne ke liye:
```bash
docker compose down          # containers band, data save rehta hai
docker compose down -v       # containers + data dono delete (fresh start)
```

Background mein chalana ho (terminal free rakhne ke liye):
```bash
docker compose up --build -d
docker compose logs -f       # logs dekhne ke liye
```

---

## 🔄 CI/CD samjho (step-by-step)

CI/CD ka matlab: jab bhi tum code GitHub par push karo, **automatically** kuch steps chal jaate hain — bina manually kuch kiye.

- **CI (Continuous Integration)** = code check karna: kya sahi se install hota hai, kya import errors hain, kya Docker image build hoti hai.
- **CD (Continuous Deployment)** = agar sab sahi hai, to automatically Docker image ko Docker Hub par bhej dena, taaki server pe deploy karna easy ho.

File: `.github/workflows/ci-cd.yml`. Ye file GitHub ko batati hai "kab" aur "kya" karna hai.

### Trigger (kab chalega)
```yaml
on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]
```
Matlab: jab bhi `main` branch par push hoga, ya koi pull request `main` ki taraf aayega — pipeline automatically chalega.

### Job 1: `build-and-test` (CI part)
Yeh job ek temporary Ubuntu machine spin karta hai aur:
1. Code checkout karta hai (`actions/checkout`)
2. Python 3.12 setup karta hai
3. Ek temporary Postgres service start karta hai (testing ke liye, exactly docker-compose jaisa hi concept)
4. Backend aur frontend ke dependencies install karta hai
5. Check karta hai ki code import ho raha hai bina error ke
6. Docker images build karta hai (sirf build, push nahi — yeh sirf verify karne ke liye ki Dockerfile sahi hai)

Agar yahan koi step fail ho jaaye (e.g. requirements.txt mein typo, ya code mein syntax error) — pipeline **red ❌** ho jaayega aur tumhe GitHub par Actions tab mein notification milega exactly kaunsa step fail hua.

### Job 2: `build-and-push` (CD part)
Yeh job tabhi chalta hai jab:
```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```
Matlab sirf jab seedha `main` par push hua ho (PR par nahi — kyunki PR ka code abhi merge nahi hua).

Yeh job:
1. Docker Hub mein login karta hai (credentials secrets se aate hain, neeche dekho)
2. Backend image build karke `yourusername/habit-backend:latest` naam se push karta hai
3. Frontend image build karke `yourusername/habit-frontend:latest` naam se push karta hai

Iske baad koi bhi server in images ko pull karke directly chala sakta hai, dobara build karne ki zaroorat nahi:
```bash
docker pull yourusername/habit-backend:latest
docker pull yourusername/habit-frontend:latest
```

### GitHub Secrets setup karna (zaroori step)
CD job kaam karega tabhi jab tum GitHub repo mein secrets add karoge:

1. GitHub repo open karo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** click karo aur ye 2 add karo:
   - `DOCKERHUB_USERNAME` → tumhara Docker Hub username
   - `DOCKERHUB_TOKEN` → Docker Hub se generate kiya hua access token (password nahi, token use karo — Docker Hub → Account Settings → Security → New Access Token)

Bina inke CD job fail ho jaayega login step par — yeh normal hai, secrets add karne ke baad theek ho jaayega.

### Pipeline ka result kahan dekhna hai
GitHub repo ke **"Actions"** tab mein jaake dekho — har push ka apna run hota hai, har step ke saamne ✅ ya ❌ dikhega, aur click karke poora log padh sakte ho.

---

## 🧠 Quick mental model (yaad rakhne ke liye)

```
Code likha → git push kiya
        ↓
GitHub Actions automatically trigger hota hai
        ↓
CI: dependencies install + sanity check + docker build (verify)
        ↓ (sirf agar main branch hai)
CD: Docker Hub par image push ho jaati hai
        ↓
Server par "docker pull" + "docker compose up" se latest version live ho jaata hai
```

---

## 🔧 Future ideas (agar extend karna ho)
- Login/auth add karna (Flask-Login)
- Weekly email summary (cron job)
- Mobile app wrapper (Streamlit already responsive hai mobile browser pe)
- Habit streaks aur badges

Enjoy your habits tracking! 🎯
