# 🚀 FluentBridge - Quick Setup Guide

## **Step-by-Step Instructions**

### **1. Prerequisites**
- ✅ Python 3.8 or higher installed
- ✅ pip (Python package manager)
- ✅ A modern web browser

### **2. Installation**

#### **Windows Users:**
```powershell
# Navigate to project folder
cd "c:\Users\mindl\OneDrive\Desktop\language leaning platform"

# Install Flask
pip install flask

# Run the application
python app.py
```

#### **Mac/Linux Users:**
```bash
# Navigate to project folder
cd language-learning-platform

# Install Flask
pip3 install flask

# Run the application
python3 app.py
```

### **3. Access the Application**

Open your web browser and go to:
```
http://localhost:5000
```

or

```
http://127.0.0.1:5000
```

### **4. First Time Setup**

1. **Homepage**: You'll see 20+ languages with flag emojis
2. **Sign Up**: Click "Get Started" to create an account
3. **Login**: Use your credentials to sign in
4. **Dashboard**: Select a language to start learning
5. **Learn**: Go through organized lessons by level and category
6. **Quiz**: Test your knowledge with interactive quizzes
7. **Progress**: Track your learning journey

## **📝 Sample Test Credentials** (After signup)

You can create test accounts with any email/password combination.

## **🎯 User Flow**

```
┌─────────────────────────────────────────┐
│     🌐 HOMEPAGE (20+ Languages)         │
│     ✓ Browse all available languages   │
│     ✓ Click any language to proceed    │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│      📝 LOGIN / SIGNUP                   │
│      ✓ Create new account               │
│      ✓ Or sign in existing              │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│      📊 DASHBOARD                        │
│      ✓ Select language to learn         │
│      ✓ View progress for each language  │
│      ✓ See daily streaks & scores      │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│      📚 LESSONS                          │
│      ✓ Beginner Level                   │
│      ✓ Intermediate Level               │
│      ✓ Advanced Level                   │
│                                         │
│      Categories:                        │
│      • Greetings                        │
│      • Numbers                          │
│      • Food                             │
│      • Travel                           │
│      • Daily Conversation               │
│      • Grammar                          │
│                                         │
│      Features:                          │
│      🔊 Pronunciation button            │
│      📝 Example sentences               │
│      ✓ Learn at your pace               │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│      🎯 QUIZ                             │
│      ✓ Multiple choice questions        │
│      ✓ Instant feedback                 │
│      ✓ Score calculation                │
│      ✓ Progress tracking                │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│      📈 PROGRESS TRACKING                │
│      ✓ Lessons completed                │
│      ✓ Quiz scores                      │
│      ✓ Daily streaks                    │
│      ✓ Performance graphs               │
└─────────────────────────────────────────┘
```

## **🔑 Key Features Explained**

### **Authentication System**
- Secure sign-up with email verification logic
- Password hashing for security
- Session-based login/logout
- Protected routes (must login to access lessons/quizzes)

### **Database Structure**
- **Users**: Store account information
- **Languages**: 20+ pre-populated languages
- **Lessons**: Organized by level and category
- **Quizzes**: Multiple-choice questions
- **Progress**: Track user advancement

### **Learning Path**
- **Beginner Level**: Start with basics
- **Intermediate Level**: Build on fundamentals
- **Advanced Level**: Master the language

### **Content Categories**
1. **Greetings**: Say hello, goodbye, thank you
2. **Numbers**: Count and understand numerals
3. **Food**: Learn food and drink vocabulary
4. **Travel**: Essential phrases for traveling
5. **Daily Conversation**: Real-life dialogues
6. **Grammar**: Grammar basics and rules

## **🎨 Features You'll Love**

✨ **Modern UI**
- Gradient purple theme
- Smooth animations
- Responsive design
- Mobile-friendly

🔊 **Interactive Learning**
- Text-to-speech for pronunciation
- Example sentences for context
- Multiple quiz types

📊 **Progress Tracking**
- Score tracking
- Lesson completion
- Daily streaks
- Level progression

🌍 **Multilingual**
- 20+ languages available
- Organized by difficulty
- Real examples from native speakers

## **⚙️ Troubleshooting**

### **Problem: "Port 5000 already in use"**
**Solution:**
```bash
# Find the process using port 5000
# Windows:
netstat -ano | findstr :5000

# Then kill it:
taskkill /PID <PID_NUMBER> /F

# Or use a different port in app.py:
# Change: app.run(debug=True)
# To: app.run(debug=True, port=5001)
```

### **Problem: "ModuleNotFoundError: No module named 'flask'"**
**Solution:**
```bash
pip install flask
```

### **Problem: "Database error"**
**Solution:**
```bash
# Delete the corrupted database
rm database.db
# or (Windows):
del database.db

# Restart the app
python app.py
```

### **Problem: Can't access http://localhost:5000**
**Solution:**
- Make sure the Flask server is running
- Check that you're using the correct URL
- Try: `http://127.0.0.1:5000`
- Check your firewall settings

## **📱 Browser Compatibility**

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+
✅ Mobile browsers (iOS Safari, Chrome Mobile)

## **🎓 Learning Tips**

1. **Start with Beginner**: Build foundation first
2. **Use Pronunciation**: Listen to correct pronunciation
3. **Read Examples**: Understand in context
4. **Take Quizzes**: Test your knowledge regularly
5. **Build Streaks**: Learn a little every day
6. **Review Mistakes**: Focus on weak areas

## **📊 Database Details**

The application uses SQLite (built into Python), so no external database setup is needed. The database file `database.db` is automatically created when you first run the app.

### **Auto-populated Data:**
- 20 languages with flag emojis
- Spanish lessons (Beginner & Intermediate)
- 8+ Spanish quiz questions
- User progress tracking

## **🔐 Security Notes**

- Passwords are hashed using werkzeug.security
- Sessions expire after browser close
- Protected routes require login
- Input validation on all forms

For production:
- Change `app.secret_key` to a strong random value
- Enable HTTPS
- Use environment variables for sensitive data
- Implement CSRF protection

## **🚀 Next Steps**

1. ✅ Run `python app.py`
2. ✅ Open `http://localhost:5000`
3. ✅ Click "Get Started" to sign up
4. ✅ Select a language from the dashboard
5. ✅ Start learning!

## **💡 Tips & Tricks**

- **Keyboard Shortcuts**: Most modern browsers support Ctrl+F for searching
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Text-to-Speech**: Click the 🔊 icon to hear pronunciation
- **Progress Tracking**: Check your score and completion percentage
- **Multiple Attempts**: Retake quizzes to improve your score

## **📞 Need Help?**

Check the README.md file for more detailed documentation.

---

**Happy Learning! 🌍📚**

**FluentBridge © 2026**
