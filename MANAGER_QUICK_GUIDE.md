# 📋 Quick Guide for Manager
## AI Content Moderation System

---

## 🎯 **What You're Getting:**
- **Professional AI system** that moderates content
- **Runs on your web server** (like a website)
- **Accessible from anywhere** via internet browser
- **Business-ready** with audit trails and reporting

---

## ⏱️ **Time Required:**
- **Setup:** 30-60 minutes
- **Technical knowledge:** Basic (or ask IT person)
- **Maintenance:** Minimal

---

## 🛠️ **What Your IT Person Needs to Do:**

### **1. Connect to Server**
- SSH into your web server
- Or access server directly

### **2. Install Python**
```bash
sudo apt install python3 python3-pip python3-venv git -y
```

### **3. Download App**
```bash
git clone https://github.com/pavanichella12/Alura.git
cd Alura
```

### **4. Install Dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **5. Run App**
```bash
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

### **6. Access App**
- Open browser
- Go to: `http://your-server-ip:8501`
- **Done!**

---

## ✅ **What You'll See:**
- **Web interface** for content moderation
- **Message testing** functionality
- **AI analysis** of content
- **Challenge system** for appeals
- **Admin panel** for reviews

---

## 🚨 **If Something Goes Wrong:**
1. **Check error messages** in terminal
2. **Verify Python 3.8+** is installed
3. **Check port 8501** is accessible
4. **Contact [Your Name]** for support

---

## 📞 **Support:**
- **Repository:** https://github.com/pavanichella12/Alura
- **Technical Support:** [Your Name]
- **Documentation:** Included in repository

---

**This system will give your company professional AI-powered content moderation! 🚀**