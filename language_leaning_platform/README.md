# FluentBridge - Professional Language Learning Platform

A comprehensive, scalable full-stack Language Learning Platform built with Python Flask, SQLite, and modern UI/UX design.

## 🌟 Features

### **Authentication & User Management**
- ✅ User sign-up and login system
- ✅ Secure password hashing (werkzeug.security)
- ✅ Session management
- ✅ Protected routes (login required)

### **Languages & Content**
- ✅ 20+ pre-populated languages with flags (emojis)
- ✅ Structured lessons in 3 levels: Beginner, Intermediate, Advanced
- ✅ 6 lesson categories: Greetings, Numbers, Food, Travel, Daily Conversation, Grammar
- ✅ Dynamic lesson loading from database
- ✅ Example sentences for context learning

### **Quiz System**
- ✅ Multiple choice questions
- ✅ Instant feedback on answers
- ✅ Score calculation and display
- ✅ Progress tracking
- ✅ Difficulty-based questions

### **User Progress Tracking**
- ✅ Per-language progress tracking
- ✅ Lesson completion counts
- ✅ Quiz completion tracking
- ✅ Daily streaks
- ✅ Score percentages

### **Modern UI/UX**
- ✅ Responsive design (mobile + desktop)
- ✅ Gradient color scheme (purple/blue theme)
- ✅ Smooth animations and transitions
- ✅ Professional card-based layout
- ✅ Dark mode ready (CSS variables)

### **Advanced Features**
- ✅ Text-to-speech pronunciation
- ✅ RESTful API endpoints
- ✅ Dynamic content loading
- ✅ Scalable database structure

## 📁 Project Structure

```
language-learning-platform/
├── app.py                          # Main Flask application
├── database.db                     # SQLite database (auto-created)
├── static/
│   ├── style.css                  # Modern responsive styles
│   └── script.js                  # JavaScript utilities
├── templates/
│   ├── index.html                 # Homepage with language selection
│   ├── login_page.html            # Login page
│   ├── signup_page.html           # Sign-up page
│   ├── dashboard_page.html        # User dashboard
│   ├── lessons_page.html          # Lessons view
│   └── quiz_page.html             # Quiz interface
└── README.md                       # This file
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- pip (Python package manager)

### **Installation**

1. **Clone or download the project**
   ```bash
   cd language-learning-platform
   ```

2. **Install dependencies**
   ```bash
   pip install flask
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   - Go to: `http://127.0.0.1:5000`
   - Or: `http://localhost:5000`

## 📝 How to Use

### **For New Users**
1. Visit the homepage and see all available languages
2. Click "Get Started" to sign up
3. Create an account with name, email, and password
4. Go to the dashboard and select a language
5. Start learning with structured lessons
6. Take quizzes to test knowledge
7. Track your progress

### **User Flow**
```
Homepage (Language Selection)
  ↓
Sign Up / Login
  ↓
Dashboard (Select Language)
  ↓
Lessons (Learn Content)
  ↓
Quiz (Test Knowledge)
  ↓
Progress Tracking
```

## 🗄️ Database Schema

### **Users Table**
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- email (TEXT UNIQUE)
- password (TEXT - hashed)
- created_at (TIMESTAMP)
```

### **Languages Table**
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT UNIQUE)
- flag (TEXT - emoji)
```

### **Lessons Table**
```sql
- id (INTEGER PRIMARY KEY)
- language_id (FOREIGN KEY)
- level (TEXT: Beginner/Intermediate/Advanced)
- category (TEXT: Greetings/Numbers/Food/Travel/etc)
- word (TEXT)
- meaning (TEXT)
- example (TEXT)
```

### **Quiz Questions Table**
```sql
- id (INTEGER PRIMARY KEY)
- language_id (FOREIGN KEY)
- question (TEXT)
- options (TEXT - JSON array)
- correct_answer (TEXT)
- difficulty (TEXT: Beginner/Intermediate/Advanced)
```

### **User Progress Table**
```sql
- id (INTEGER PRIMARY KEY)
- user_id (FOREIGN KEY)
- language_id (FOREIGN KEY)
- level (TEXT)
- score (INTEGER - percentage)
- streak (INTEGER - days)
- lessons_completed (INTEGER)
- quizzes_completed (INTEGER)
- last_learned (TIMESTAMP)
```

## 🎨 Design Features

### **Color Palette**
- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Dark Purple)
- Accent: `#ff6b6b` (Red)
- Light Background: `#f8f9fa` (Light Gray)

### **UI Components**
- Gradient buttons with hover effects
- Responsive grid layouts
- Card-based content display
- Smooth fade-in animations
- Progress bars for tracking

## 🔐 Security Features

- Password hashing with werkzeug.security
- Session-based authentication
- Protected routes with @login_required decorator
- CSRF protection ready (implement in production)
- Input validation on all forms

## 📱 Responsive Breakpoints

- Desktop: 1200px+ (3 columns for languages)
- Tablet: 768px+ (2 columns)
- Mobile: 480px+ (1 column)

## 🌐 Pre-populated Languages (20+)

1. English 🇺🇸
2. Spanish 🇪🇸
3. French 🇫🇷
4. German 🇩🇪
5. Italian 🇮🇹
6. Portuguese 🇵🇹
7. Japanese 🇯🇵
8. Korean 🇰🇷
9. Chinese 🇨🇳
10. Arabic 🇸🇦
11. Russian 🇷🇺
12. Turkish 🇹🇷
13. Dutch 🇳🇱
14. Hindi 🇮🇳
15. Telugu 🇮🇳
16. Swedish 🇸🇪
17. Norwegian 🇳🇴
18. Danish 🇩🇰
19. Polish 🇵🇱
20. Greek 🇬🇷

## 📊 Sample Data

The application comes with:
- ✅ 20 languages pre-configured
- ✅ Spanish lessons for all levels
- ✅ 8+ sample quiz questions
- ✅ Organized by categories and levels

## 🔧 Customization

### **Add New Language**
1. Insert into `languages` table
2. Add lessons to `lessons` table
3. Add questions to `quiz_questions` table

### **Add New Lessons**
```python
c.execute('''INSERT INTO lessons 
            (language_id, level, category, word, meaning, example) 
            VALUES (?, ?, ?, ?, ?, ?)''',
         (lang_id, 'Beginner', 'Greetings', 'Hola', 'Hello', 'Hola, ¿cómo estás?'))
```

### **Add New Quiz Questions**
```python
c.execute('''INSERT INTO quiz_questions 
            (language_id, question, options, correct_answer, difficulty) 
            VALUES (?, ?, ?, ?, ?)''',
         (lang_id, 'Question?', '["Option1","Option2","Option3"]', 'Option1', 'Beginner'))
```

## 🚀 Future Enhancements

- [ ] Admin panel for managing content
- [ ] Leaderboard system
- [ ] Daily challenges
- [ ] Achievements/Badges
- [ ] Speech recognition
- [ ] Offline mode
- [ ] Mobile app
- [ ] Dark mode toggle
- [ ] Email verification
- [ ] Password reset functionality

## 🐛 Troubleshooting

### **Port 5000 already in use**
```bash
# Find and kill the process
lsof -i :5000
kill -9 <PID>
```

### **Database error**
```bash
# Delete the database and restart
rm database.db
python app.py
```

### **Module not found**
```bash
# Install Flask
pip install flask
```

## 📖 API Endpoints

### **Public Endpoints**
- `GET /` - Homepage
- `GET/POST /login` - Login page
- `GET/POST /signup` - Sign-up page

### **Protected Endpoints** (Login required)
- `GET /dashboard` - User dashboard
- `GET /lessons/<lang_id>` - View lessons
- `GET /quiz/<lang_id>` - Take quiz
- `POST /submit-quiz` - Submit quiz answers
- `GET /select-language/<lang_id>` - Select language
- `GET /logout` - Logout

### **API Endpoints**
- `GET /api/languages` - Get all languages (JSON)

## 📝 License

This project is open source and available for educational purposes.

## 💬 Support

For issues or suggestions, please refer to the code comments for understanding the implementation.

---

**Made with ❤️ for language learners worldwide**

**FluentBridge © 2026**
