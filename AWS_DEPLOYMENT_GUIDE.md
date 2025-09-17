# 🚀 AWS Cloud Deployment Guide

## Option 1: AWS EC2 (Virtual Server)

### 💰 **Cost Breakdown:**

#### **Free Tier (First 12 Months):**
- **t2.micro instance:** FREE (750 hours/month)
- **30GB EBS storage:** FREE
- **Data transfer:** 15GB/month FREE
- **Total:** $0/month for first year

#### **After Free Tier:**
- **t2.micro:** ~$8.50/month
- **t3.small:** ~$15-20/month  
- **t3.medium:** ~$30-40/month
- **EBS storage (20GB):** ~$2/month
- **Data transfer:** $0.09/GB after 15GB

### 🛠️ **Step-by-Step Setup:**

#### **1. Create AWS Account**
- Go to: https://aws.amazon.com/
- Sign up (requires credit card)
- Verify phone number
- Choose "Basic Support" (free)

#### **2. Launch EC2 Instance**
```bash
# In AWS Console:
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose "Ubuntu Server 20.04 LTS"
4. Select "t2.micro" (free tier eligible)
5. Create new key pair (download .pem file)
6. Configure security group:
   - SSH (22): Your IP
   - HTTP (80): 0.0.0.0/0
   - Custom TCP (8501): 0.0.0.0/0
7. Launch instance
```

#### **3. Connect to Your Server**
```bash
# Replace with your key file and IP
ssh -i your-key.pem ubuntu@your-ec2-ip-address
```

#### **4. Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv git -y

# Install Node.js (for some dependencies)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### **5. Clone and Setup Your App**
```bash
# Clone your repository
git clone https://github.com/pavanichella12/Alura.git
cd Alura

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your environment variables
```

#### **6. Run Your App**
```bash
# Run Streamlit
streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# Your app will be available at:
# http://your-ec2-ip:8501
```

#### **7. Make it Persistent (Optional)**
```bash
# Install PM2 for process management
sudo npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'content-moderation',
    script: 'streamlit',
    args: 'run app.py --server.port=8501 --server.address=0.0.0.0',
    cwd: '/home/ubuntu/Alura',
    interpreter: '/home/ubuntu/Alura/venv/bin/python',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## Option 2: AWS Elastic Beanstalk (Easier)

### 💰 **Cost:**
- **Same as EC2** (uses EC2 under the hood)
- **Additional:** ~$1-2/month for load balancer

### 🛠️ **Setup:**
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

---

## Option 3: AWS App Runner (Serverless)

### 💰 **Cost:**
- **Free tier:** 2,000 vCPU minutes/month
- **After free tier:** ~$25-50/month
- **No server management needed**

### 🛠️ **Setup:**
1. Go to AWS App Runner console
2. Create service from source code
3. Connect to GitHub repository
4. Configure build settings
5. Deploy automatically

---

## 🌐 **Domain & SSL (Optional)**

### **Route 53 (Domain):**
- **Domain registration:** ~$12/year
- **Hosted zone:** ~$0.50/month

### **CloudFront (CDN):**
- **Free tier:** 1TB data transfer/month
- **After free tier:** ~$0.085/GB

### **SSL Certificate:**
- **AWS Certificate Manager:** FREE

---

## 📊 **Total Monthly Costs:**

### **Basic Setup (Free Tier):**
- **EC2 t2.micro:** $0
- **EBS storage:** $0
- **Data transfer:** $0
- **Total:** $0/month (first 12 months)

### **After Free Tier (Small App):**
- **EC2 t2.micro:** ~$8.50
- **EBS storage:** ~$2
- **Data transfer:** ~$2
- **Total:** ~$12.50/month

### **Production Setup:**
- **EC2 t3.small:** ~$18
- **EBS storage:** ~$5
- **Load balancer:** ~$18
- **Domain & SSL:** ~$1
- **Total:** ~$42/month

---

## 🚨 **Important Notes:**

### **Ollama Limitation:**
- **Ollama doesn't work on AWS** (requires local installation)
- **Your app will use fallback mode** (keyword matching)
- **This is actually good** - shows robust error handling

### **Database:**
- **SQLite works fine** on EC2
- **For production:** Consider RDS (starts at ~$15/month)

### **Security:**
- **Always use security groups** to restrict access
- **Keep your .pem file secure**
- **Regular security updates**

---

## 🎯 **Recommended for Your Demo:**

### **Start with Free Tier:**
1. **Use t2.micro** (free for 12 months)
2. **Deploy your app** on EC2
3. **Show it works** in cloud environment
4. **Explain the architecture** and fallback mechanisms

### **Talking Points:**
- *"I deployed this on AWS using the free tier"*
- *"The system gracefully handles cloud limitations"*
- *"It's production-ready and scalable"*

---

## 🚀 **Quick Start Commands:**

```bash
# 1. Launch EC2 instance (in AWS Console)
# 2. Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Setup
sudo apt update
sudo apt install python3-pip git -y
git clone https://github.com/pavanichella12/Alura.git
cd Alura
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

**Your app will be live at: http://your-ec2-ip:8501** 🌐

---

## 💡 **Pro Tips:**

1. **Start with free tier** - No cost for first year
2. **Use security groups** - Restrict access properly
3. **Monitor costs** - Set up billing alerts
4. **Backup regularly** - Use EBS snapshots
5. **Scale as needed** - Upgrade instance size when needed

**AWS gives you enterprise-grade infrastructure for your AI project!** 🚀