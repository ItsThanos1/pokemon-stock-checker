# 🎮 Pokemon Card Stock Checker - Best Buy

A web application to check Best Buy inventory for Pokemon cards across multiple stores near you!

## 🎨 Available SKUs

- **Black Edition** - SKU: 6612728
- **Grey Edition** - SKU: 6612730
- **Blue Edition** - SKU: 6612731
- **White Edition** - SKU: 6612732

## 🚀 Features

- ✅ Check multiple Pokemon card variants at once
- 📍 Search by zip code
- 🏪 Shows both pickup and ship-to-store availability
- 📦 Displays real-time stock levels
- 🎨 Beautiful, modern UI
- 📱 Mobile responsive

## 📋 Required Files for Render Deployment

Your repository needs these files (all included):

```
pokemon/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Tells Render how to run your app
├── render.yaml        # Render configuration (optional)
├── templates/
│   └── index.html     # Web interface
└── README.md          # This file
```

## 🔧 Deploying to Render

### Method 1: Via GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Pokemon stock checker"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up or log in (can use GitHub account)

3. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository
   - Select the repository with your Pokemon stock checker

4. **Configure the Service**
   - **Name**: `pokemon-stock-checker` (or any name you like)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave blank (or enter `.` if asked)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

5. **Deploy**
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment
   - Your app will be live at: `https://your-app-name.onrender.com`

### Method 2: Via Render Dashboard (Manual Upload)

If you don't want to use GitHub:

1. **Create a Render Account**
   - Go to https://render.com and sign up

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Choose "Deploy without a Git repository"

3. **Upload Files**
   - Upload your project folder via Render dashboard

4. **Configure Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

## ⚙️ Important Settings for Render

### Start Command (REQUIRED)
```
gunicorn app:app
```

### Build Command
```
pip install -r requirements.txt
```

### Environment Variables

**IMPORTANT: For reliable operation, configure these proxy settings in Render:**

Go to your Render service → **Environment** tab → Add these variables:

| Variable | Value | Required |
|----------|-------|----------|
| `PROXY_IP` | Your proxy IP (e.g., 65.195.104.96) | Yes |
| `PROXY_PORT` | Your proxy port (e.g., 50100) | No (defaults to 50100) |
| `PROXY_USER` | Your proxy username | Yes |
| `PROXY_PASS` | Your proxy password | Yes |

**Why use a proxy?** Best Buy may rate-limit or block Render's IP addresses. Using a residential proxy/ISP ensures reliable access to their API.

### Python Version
The app uses Python 3.11 by default (specified in `render.yaml`)

## 🧪 Testing Locally

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open http://localhost:5000 in your browser.

## 📦 What Each File Does

- **app.py**: Main Flask web server that handles requests and checks Best Buy API
- **templates/index.html**: Beautiful web interface users see
- **requirements.txt**: List of Python packages needed
- **Procfile**: Tells Render to use Gunicorn web server
- **render.yaml**: Optional config file for Render (makes deployment easier)

## 🎯 How to Use the App

1. Visit your deployed website
2. Enter your zip code
3. Select which Pokemon card colors to check (or "Check All")
4. Click "Check Stock Availability"
5. View results showing:
   - Stores with pickup available
   - Stores with ship-to-store options
   - Stock quantities
   - Store locations and distances

## 🔍 Troubleshooting

### App won't start on Render?
- Check Render logs for errors
- Verify Start Command is: `gunicorn app:app`
- Ensure all files are uploaded/committed

### No results showing?
- Verify zip code is valid
- Some areas may have no nearby stores
- Best Buy API might be rate limiting (wait a minute)

### "Module not found" error?
- Check requirements.txt is present
- Verify Build Command ran successfully in Render logs

## 💡 Tips

- Free tier on Render may sleep after inactivity (first load takes ~30 seconds)
- Upgrade to paid tier for 24/7 availability
- App automatically scales to handle traffic

## 🤝 Support

If you have issues:
1. Check Render logs (Dashboard → Your Service → Logs)
2. Verify all files are present
3. Make sure Python 3.11+ is being used

## 📝 License

Free to use and modify!

---

Made with ❤️ for Pokemon card hunters
