# PAN Info API

Lookup PAN details using Spinny API.

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /api/pan?pan=BBGPP5787F` - Get PAN details

## Deploy on Render

1. Push to GitHub
2. Create new Web Service on Render
3. Connect GitHub repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. Deploy!

## Local Testing

```bash
pip install -r requirements.txt
python app.py---

## Render pe deploy kaise karein:

1. **GitHub pe push karo** in 3 files ko ek repo mein

2. **[Render.com](https://render.com)** pe jao → Sign up → "New +" → "Web Service"

3. **Connect GitHub repo** jo abhi banaya

4. **Settings:**
   - **Name:** pan-api (kuch bhi)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

5. **Create Web Service** → Automatic deploy ho jayega

**Live URL milega:** `https://pan-api-xxx.onrender.com/api/pan?pan=BBGPP5787F`

Ho gaya! Koi problem aaye toh batao.
