# 🚀 Server Deployment Instructions
## AI Content Moderation System

**For: [Manager's Name]**  
**Project: AI Content Moderation System**  
**Repository: https://github.com/pavanichella12/Alura**

---

## 📋 **Prerequisites Checklist**

### **Server Requirements:**
- [ ] **Operating System:** Linux (Ubuntu 20.04+ recommended) or Windows Server
- [ ] **Python:** Version 3.8 or higher
- [ ] **RAM:** Minimum 2GB (4GB recommended)
- [ ] **Storage:** At least 5GB free space
- [ ] **Network:** Port 8501 accessible (or custom port)
- [ ] **Internet:** Required for package installation

### **Access Requirements:**
- [ ] **SSH access** to the server
- [ ] **Root/sudo privileges** for package installation
- [ ] **Git** installed on server
- [ ] **Firewall configured** to allow port 8501

---

## 🛠️ **Step-by-Step Deployment**

### **Step 1: Server Preparation**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install python3 python3-pip python3-venv git curl -y

# Verify Python version (should be 3.8+)
python3 --version
```

### **Step 2: Clone Repository**
```bash
# Navigate to desired directory (e.g., /var/www or /home/user)
cd /var/www  # or your preferred directory

# Clone the repository
git clone https://github.com/pavanichella12/Alura.git

# Navigate to project directory
cd Alura
```

### **Step 3: Setup Python Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### **Step 4: Environment Configuration**
```bash
# Create environment file
nano .env

# Add the following content (replace with actual values):
```

**Environment Variables Template:**
```bash
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE=your_twilio_phone_number_here
REVIEWER_PHONE=your_reviewer_phone_number_here
```

### **Step 5: Test Installation**
```bash
# Test if everything works
python -c "import streamlit; print('Streamlit installed successfully')"
python -c "import ollama; print('Ollama client installed successfully')"
```

### **Step 6: Run the Application**
```bash
# Start the application
streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# The app will be available at: http://your-server-ip:8501
```

---

## 🔧 **Production Setup (Recommended)**

### **Option 1: Using PM2 (Process Manager)**
```bash
# Install Node.js and PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pm2

# Create PM2 configuration
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'content-moderation-app',
    script: 'streamlit',
    args: 'run app.py --server.port=8501 --server.address=0.0.0.0',
    cwd: '/var/www/Alura',  # Update path as needed
    interpreter: '/var/www/Alura/venv/bin/python',  # Update path as needed
    env: {
      NODE_ENV: 'production'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### **Option 2: Using Systemd Service**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/content-moderation.service
```

**Service File Content:**
```ini
[Unit]
Description=AI Content Moderation System
After=network.target

[Service]
Type=simple
User=www-data  # or your preferred user
WorkingDirectory=/var/www/Alura
Environment=PATH=/var/www/Alura/venv/bin
ExecStart=/var/www/Alura/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable content-moderation
sudo systemctl start content-moderation
sudo systemctl status content-moderation
```

---

## 🌐 **Web Server Integration**

### **Nginx Reverse Proxy (Recommended)**
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/content-moderation
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/content-moderation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 **Security Configuration**

### **Firewall Setup**
```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501  # Only if not using reverse proxy
sudo ufw enable
```

### **SSL Certificate (Optional)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## 📊 **Monitoring & Maintenance**

### **Check Application Status**
```bash
# If using PM2
pm2 status
pm2 logs content-moderation-app

# If using systemd
sudo systemctl status content-moderation
sudo journalctl -u content-moderation -f
```

### **Update Application**
```bash
# Navigate to project directory
cd /var/www/Alura

# Pull latest changes
git pull origin main

# Restart application
pm2 restart content-moderation-app
# OR
sudo systemctl restart content-moderation
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **Port Already in Use:**
```bash
# Check what's using port 8501
sudo netstat -tlnp | grep 8501
# Kill process if needed
sudo kill -9 <PID>
```

#### **Permission Issues:**
```bash
# Fix file permissions
sudo chown -R www-data:www-data /var/www/Alura
sudo chmod -R 755 /var/www/Alura
```

#### **Python Dependencies:**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

#### **Database Issues:**
```bash
# Check database file permissions
ls -la data/database/
# Fix if needed
sudo chmod 664 data/database/content_moderation.db*
```

---

## 📱 **Access Information**

### **Application URLs:**
- **Direct Access:** `http://your-server-ip:8501`
- **With Domain:** `http://your-domain.com` (if Nginx configured)
- **HTTPS:** `https://your-domain.com` (if SSL configured)

### **Admin Access:**
- **Challenge Management:** Available in the web interface
- **Database:** SQLite file at `data/database/content_moderation.db`
- **Logs:** Check PM2/systemd logs for debugging

---

## 📞 **Support & Contact**

### **Technical Issues:**
- **Repository:** https://github.com/pavanichella12/Alura
- **Documentation:** Check `README.md` and `DEPLOYMENT_GUIDE.md`
- **Issues:** Create GitHub issue for bugs

### **Configuration Help:**
- **Environment Variables:** See `env_template.txt`
- **Database:** SQLite (no additional setup needed)
- **Notifications:** Requires valid Twilio credentials

---

## ✅ **Deployment Checklist**

- [ ] Server meets requirements
- [ ] Repository cloned successfully
- [ ] Python environment created
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Application starts without errors
- [ ] Web interface accessible
- [ ] Database file created
- [ ] Process manager configured (optional)
- [ ] Reverse proxy configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Firewall configured
- [ ] Monitoring setup

---

## 🎯 **Expected Behavior**

### **What Should Work:**
- ✅ **Web Interface:** Accessible at configured URL
- ✅ **Message Analysis:** AI-powered content moderation
- ✅ **Database Storage:** Messages and violations stored
- ✅ **Challenge System:** Users can challenge decisions
- ✅ **Notifications:** WhatsApp notifications (if Twilio configured)

### **Fallback Mode:**
- ⚠️ **Ollama Not Available:** System uses keyword matching
- ✅ **Still Functional:** All features work with fallback
- ✅ **Robust Design:** Graceful degradation

---

**Deployment should take approximately 30-60 minutes depending on server setup and experience level.**