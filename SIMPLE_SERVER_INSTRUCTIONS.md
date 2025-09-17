# 🚀 Simple Server Instructions
## AI Content Moderation System

**For: [Manager's Name]**  
**From: [Your Name]**  
**Project: AI Content Moderation System**

---

## 🎯 **What This Is:**
- **AI-powered content moderation system**
- **Runs in web browser** (like Google, Facebook)
- **Screens messages** for inappropriate language
- **Professional business tool**

---

## 📋 **What You Need:**
- **Server/Computer** with internet connection
- **Python 3.8+** (programming language)
- **30-60 minutes** to set up
- **Basic technical knowledge** (or IT person)

---

## 🛠️ **Step-by-Step Setup:**

### **Step 1: Connect to Your Server**
```bash
# If it's a remote server, connect via SSH
ssh username@your-server-ip

# If it's a local server, just open terminal
```

### **Step 2: Install Python (if not already installed)**
```bash
# For Ubuntu/Linux:
sudo apt update
sudo apt install python3 python3-pip python3-venv git -y

# For Windows Server:
# Download Python from python.org and install
```

### **Step 3: Download the App**
```bash
# Go to a folder where you want the app
cd /var/www  # or any folder you prefer

# Download the app from GitHub
git clone https://github.com/pavanichella12/Alura.git

# Go into the app folder
cd Alura
```

### **Step 4: Install Dependencies**
```bash
# Create virtual environment (like a container for the app)
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### **Step 5: Configure (Optional)**
```bash
# Create environment file for notifications
nano .env

# Add these lines (replace with your actual values):
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE=your_twilio_phone
REVIEWER_PHONE=your_reviewer_phone
```

### **Step 6: Run the App**
```bash
# Start the application
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

### **Step 7: Access the App**
- **Open web browser**
- **Go to:** `http://your-server-ip:8501`
- **App is now live!**

---

## 🔧 **Make it Run Forever (Optional):**

### **Option 1: Simple (Recommended)**
```bash
# Just run the command above
# App will run until you close the terminal
```

### **Option 2: Professional**
```bash
# Install PM2 (process manager)
sudo npm install -g pm2

# Create PM2 config
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'content-moderation',
    script: 'streamlit',
    args: 'run app.py --server.port=8501 --server.address=0.0.0.0',
    cwd: '/var/www/Alura',
    interpreter: '/var/www/Alura/venv/bin/python'
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 🌐 **Web Access Setup (Optional):**

### **If you want a custom domain:**
```bash
# Install Nginx
sudo apt install nginx -y

# Create config file
sudo nano /etc/nginx/sites-available/content-moderation
```

**Add this content:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/content-moderation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ✅ **What Should Happen:**

### **Success Indicators:**
- ✅ **App starts** without errors
- ✅ **Web page loads** at your server IP
- ✅ **Message testing** works
- ✅ **AI analysis** functions
- ✅ **Database** stores data

### **Expected Behavior:**
- **Clean messages:** Get approved and sent
- **Bad messages:** Get flagged and blocked
- **Challenge system:** Users can appeal decisions
- **Admin panel:** Review challenges

---

## 🚨 **Common Issues & Solutions:**

### **"Port 8501 not accessible"**
```bash
# Check if port is open
sudo ufw allow 8501
# OR
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
```

### **"Python not found"**
```bash
# Install Python
sudo apt install python3 python3-pip -y
```

### **"Permission denied"**
```bash
# Fix permissions
sudo chown -R $USER:$USER /var/www/Alura
chmod -R 755 /var/www/Alura
```

### **"App won't start"**
```bash
# Check if port is already in use
sudo netstat -tlnp | grep 8501
# Kill process if needed
sudo kill -9 <PID>
```

---

## 📞 **Support:**

### **If You Need Help:**
1. **Check the logs** for error messages
2. **Verify Python version** (should be 3.8+)
3. **Check internet connection** (for package downloads)
4. **Contact [Your Name]** for technical support

### **Repository:** https://github.com/pavanichella12/Alura

---

## 🎯 **Summary:**

**This is a professional AI system that:**
- ✅ **Runs on your server** 24/7
- ✅ **Accessible from anywhere** via web browser
- ✅ **Moderates content** automatically
- ✅ **Provides audit trail** for compliance
- ✅ **Scales with your business** needs

**Setup time:** 30-60 minutes  
**Maintenance:** Minimal  
**Cost:** Just server resources (no licensing fees)

---

**Your AI Content Moderation System will be live and professional! 🚀**