# 🚀 Web Server Deployment Guide

## Option 1: Streamlit Cloud (Recommended for Demo)

### Prerequisites:
- GitHub repository (✅ You have this!)
- Streamlit Cloud account (free)

### Steps:

#### 1. **Sign up for Streamlit Cloud**
- Go to: https://share.streamlit.io/
- Sign in with your GitHub account
- Authorize Streamlit to access your repositories

#### 2. **Deploy Your App**
- Click "New app"
- Select your repository: `pavanichella12/Alura`
- Main file path: `streamlit_app.py`
- App URL: Choose a custom name (e.g., `alura-content-moderation`)

#### 3. **Set Environment Variables**
In Streamlit Cloud dashboard, add these secrets:
```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE=your_twilio_phone
REVIEWER_PHONE=your_reviewer_phone
```

#### 4. **Deploy**
- Click "Deploy!"
- Wait 5-10 minutes for deployment
- Your app will be live at: `https://alura-content-moderation.streamlit.app`

---

## Option 2: Heroku Deployment

### Prerequisites:
- Heroku account (free tier available)
- Heroku CLI installed

### Steps:

#### 1. **Create Heroku App**
```bash
heroku create your-app-name
```

#### 2. **Create Procfile**
```bash
echo "web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
```

#### 3. **Set Environment Variables**
```bash
heroku config:set TWILIO_ACCOUNT_SID=your_twilio_account_sid
heroku config:set TWILIO_AUTH_TOKEN=your_twilio_auth_token
heroku config:set TWILIO_PHONE=your_twilio_phone
heroku config:set REVIEWER_PHONE=your_reviewer_phone
```

#### 4. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

---

## Option 3: AWS EC2 (Professional)

### Prerequisites:
- AWS account
- EC2 instance (t2.micro for free tier)

### Steps:

#### 1. **Launch EC2 Instance**
- Choose Ubuntu 20.04 LTS
- t2.micro instance type
- Configure security group (open port 8501)

#### 2. **Connect and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo apt update
sudo apt install python3-pip git
```

#### 3. **Clone and Run**
```bash
git clone https://github.com/pavanichella12/Alura.git
cd Alura
pip3 install -r requirements.txt
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

---

## 🌐 **Important Notes for Web Deployment:**

### **Ollama Limitation:**
- **Ollama doesn't work on cloud platforms** (requires local installation)
- **Your app will use fallback mode** (keyword matching)
- **This is actually good for demos** - shows robust error handling

### **Database:**
- **SQLite works fine** on cloud platforms
- **Data persists** between sessions
- **No additional setup needed**

### **Twilio:**
- **Works perfectly** on cloud platforms
- **Set environment variables** in deployment platform
- **WhatsApp notifications** will work

---

## 🎯 **Recommended Approach:**

### **For Your Interview/Demo:**
1. **Use Streamlit Cloud** - Easiest and most impressive
2. **Show both modes** - Local (with Ollama) and Cloud (fallback)
3. **Explain the architecture** - How it adapts to different environments

### **Talking Points:**
- *"I designed the system to work in multiple environments"*
- *"It gracefully falls back when Ollama isn't available"*
- *"The cloud version demonstrates production readiness"*

---

## 🚀 **Quick Start (Streamlit Cloud):**

1. **Push your changes:**
```bash
git add .
git commit -m "Add cloud deployment support"
git push origin main
```

2. **Go to Streamlit Cloud:**
   - https://share.streamlit.io/
   - Deploy from your GitHub repo

3. **Share the live URL:**
   - Your app will be accessible worldwide!
   - Perfect for interviews and demos

---

## 📱 **Access Your Live App:**
Once deployed, your app will be accessible at:
- **Streamlit Cloud:** `https://your-app-name.streamlit.app`
- **Heroku:** `https://your-app-name.herokuapp.com`
- **AWS:** `http://your-ec2-ip:8501`

**Your AI Content Moderation System will be live on the web! 🌐**