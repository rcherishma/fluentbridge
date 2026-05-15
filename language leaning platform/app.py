"""
FluentBridge - Professional Language Learning Platform
Backend: Python Flask with SQLite Database
"""
from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import json
import random
import subprocess
import tempfile
from io import BytesIO
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database path
DATABASE = 'database.db'

# ======================== DATABASE SETUP ========================

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  profile_photo TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Languages table
    c.execute('''CREATE TABLE IF NOT EXISTS languages
                 (id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL UNIQUE,
                  flag TEXT NOT NULL)''')
    
    # Lessons table
    c.execute('''CREATE TABLE IF NOT EXISTS lessons
                 (id INTEGER PRIMARY KEY,
                  language_id INTEGER NOT NULL,
                  level TEXT NOT NULL,
                  category TEXT NOT NULL,
                  word TEXT NOT NULL,
                  meaning TEXT NOT NULL,
                  example TEXT,
                  FOREIGN KEY(language_id) REFERENCES languages(id))''')
    
    # Quiz Questions table
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_questions
                 (id INTEGER PRIMARY KEY,
                  language_id INTEGER NOT NULL,
                  question TEXT NOT NULL,
                  options TEXT NOT NULL,
                  correct_answer TEXT NOT NULL,
                  difficulty TEXT NOT NULL,
                  FOREIGN KEY(language_id) REFERENCES languages(id))''')
    
    # User Progress table
    c.execute('''CREATE TABLE IF NOT EXISTS user_progress
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER NOT NULL,
                  language_id INTEGER NOT NULL,
                  level TEXT DEFAULT 'Beginner',
                  score INTEGER DEFAULT 0,
                  streak INTEGER DEFAULT 0,
                  lessons_completed INTEGER DEFAULT 0,
                  quizzes_completed INTEGER DEFAULT 0,
                  last_learned TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  FOREIGN KEY(language_id) REFERENCES languages(id))''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ======================== AUTHENTICATION HELPERS ========================
from gtts import gTTS

@app.route('/speak/<language>/<text>')
def speak(language, text):

    language_codes = {
        'English': 'en',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt',
        'Japanese': 'ja',
        'Chinese': 'zh-CN',
        'Korean': 'ko',
        'Arabic': 'ar',
        'Hindi': 'hi',
        'Telugu': 'te',
        'Russian': 'ru',
        'Turkish': 'tr'
    }

    lang_code = language_codes.get(language, 'en')

    tts = gTTS(text=text, lang=lang_code)

    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    return send_file(
        audio_buffer,
        mimetype='audio/mpeg',
        as_attachment=False,
        download_name='pronunciation.mp3'
    )
def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            next_url = request.path
            return redirect(url_for('login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function


def get_voice_lang_code(language_name):
    codes = {
        'English': 'en-US',
        'Spanish': 'es-ES',
        'French': 'fr-FR',
        'German': 'de-DE',
        'Italian': 'it-IT',
        'Portuguese': 'pt-PT',
        'Japanese': 'ja-JP',
        'Chinese': 'zh-CN',
        'Korean': 'ko-KR',
        'Arabic': 'ar-SA',
        'Hindi': 'hi-IN',
        'Telugu': 'te-IN',
        'Dutch': 'nl-NL',
        'Swedish': 'sv-SE',
        'Norwegian': 'nb-NO',
        'Danish': 'da-DK',
        'Polish': 'pl-PL',
        'Greek': 'el-GR',
        'Vietnamese': 'vi-VN',
        'Thai': 'th-TH',
        'Indonesian': 'id-ID',
        'Czech': 'cs-CZ',
        'Russian': 'ru-RU',
        'Turkish': 'tr-TR'
    }
    return codes.get(language_name, 'en-US')

# ======================== POPULATE DATABASE ========================

def populate_sample_data():
    """Populate database with sample languages and lessons"""
    conn = get_db()
    c = conn.cursor()
    
    # Languages with flags
    languages = [
        ('English', 'us'),
        ('Spanish', '🇪🇸'),
        ('French', '🇫🇷'),
        ('German', '🇩🇪'),
        ('Italian', '🇮🇹'),
        ('Portuguese', '🇵🇹'),
        ('Japanese', '🇯🇵'),
        ('Korean', '🇰🇷'),
        ('Chinese', '🇨🇳'),
        ('Arabic', '🇸🇦'),
        ('Russian', '🇷🇺'),
        ('Turkish', '🇹🇷'),
        ('Dutch', '🇳🇱'),
        ('Hindi', '🇮🇳'),
        ('Telugu', '🇮🇳'),
        ('Swedish', '🇸🇪'),
        ('Norwegian', '🇳🇴'),
        ('Danish', '🇩🇰'),
        ('Polish', '🇵🇱'),
        ('Greek', '🇬🇷'),
        ('Vietnamese', '🇻🇳'),
        ('Thai', '🇹🇭'),
        ('Indonesian', '🇮🇩'),
        ('Czech', '🇨🇿'),

    ]
    
    # Check if languages exist
    c.execute('SELECT COUNT(*) FROM languages')
    if c.fetchone()[0] == 0:
        for lang, flag in languages:
            c.execute('INSERT INTO languages (name, flag) VALUES (?, ?)', (lang, flag))
        conn.commit()
    
    # Sample lessons for Spanish
    c.execute('SELECT id FROM languages WHERE name = ?', ('Spanish',))
    spanish_id = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM lessons WHERE language_id = ?', (spanish_id,))
    if c.fetchone()[0] == 0:
        lessons = [
            # Beginner - Greetings
            (spanish_id, 'Beginner', 'Greetings', 'Hola', 'Hello', 'Hola, ¿cómo estás?'),
            (spanish_id, 'Beginner', 'Greetings', 'Adiós', 'Goodbye', 'Adiós, hasta luego'),
            (spanish_id, 'Beginner', 'Greetings', 'Buenos días', 'Good morning', 'Buenos días, ¿cómo estás?'),
            (spanish_id, 'Beginner', 'Greetings', 'Buenas noches', 'Good night', 'Buenas noches'),
            (spanish_id, 'Beginner', 'Greetings', 'Gracias', 'Thank you', 'Muchas gracias'),
            (spanish_id, 'Beginner', 'Greetings', 'De nada', 'You are welcome', 'De nada, es un placer'),
            
            # Beginner - Numbers
            (spanish_id, 'Beginner', 'Numbers', 'Uno', 'One', 'Tengo uno manzana'),
            (spanish_id, 'Beginner', 'Numbers', 'Dos', 'Two', 'Hay dos gatos'),
            (spanish_id, 'Beginner', 'Numbers', 'Tres', 'Three', 'Veo tres pájaros'),
            (spanish_id, 'Beginner', 'Numbers', 'Diez', 'Ten', 'Tengo diez dedos'),
            
            # Beginner - Food
            (spanish_id, 'Beginner', 'Food', 'Pan', 'Bread', 'Quiero pan, por favor'),
            (spanish_id, 'Beginner', 'Food', 'Agua', 'Water', 'Un vaso de agua, por favor'),
            (spanish_id, 'Beginner', 'Food', 'Manzana', 'Apple', 'Me gusta la manzana'),
            (spanish_id, 'Beginner', 'Food', 'Arroz', 'Rice', 'Prefiero el arroz'),
            
            # Intermediate - Travel
            (spanish_id, 'Intermediate', 'Travel', 'Aeropuerto', 'Airport', 'Necesito ir al aeropuerto'),
            (spanish_id, 'Intermediate', 'Travel', 'Hotel', 'Hotel', 'Busco un hotel'),
            (spanish_id, 'Intermediate', 'Travel', 'Billete', 'Ticket', 'Quiero un billete'),
            (spanish_id, 'Intermediate', 'Travel', 'Mapa', 'Map', 'Necesito un mapa'),
            
            # Intermediate - Daily Conversation
            (spanish_id, 'Intermediate', 'Daily Conversation', '¿Cómo estás?', 'How are you?', '¿Cómo estás hoy?'),
            (spanish_id, 'Intermediate', 'Daily Conversation', 'Estoy bien', 'I am fine', 'Estoy muy bien, gracias'),
            (spanish_id, 'Intermediate', 'Daily Conversation', '¿Y tú?', 'And you?', '¿Y tú, qué tal?'),
            (spanish_id, 'Intermediate', 'Daily Conversation', 'Me llamo...', 'My name is...', 'Me llamo Carlos'),
        ]
        
        for lang_id, level, category, word, meaning, example in lessons:
            c.execute('''INSERT INTO lessons 
                        (language_id, level, category, word, meaning, example) 
                        VALUES (?, ?, ?, ?, ?, ?)''', 
                     (lang_id, level, category, word, meaning, example))
        
        conn.commit()
    
    # Sample quiz questions with multilingual options
    translations = {
        'Japanese': {'Hello': 'こんにちは', 'Goodbye': 'さようなら', 'Thank you': 'ありがとう', 'Water': 'みず'},
        'Chinese': {'Hello': '你好', 'Goodbye': '再见', 'Thank you': '谢谢', 'Water': '水'},
        'Korean': {'Hello': '안녕하세요', 'Goodbye': '안녕히 가세요', 'Thank you': '감사합니다', 'Water': '물'},
        'French': {'Hello': 'Bonjour', 'Goodbye': 'Au revoir', 'Thank you': 'Merci', 'Water': 'Eau'},
        'Spanish': {'Hello': 'Hola', 'Goodbye': 'Adiós', 'Thank you': 'Gracias', 'Water': 'Agua'},
        'German': {'Hello': 'Hallo', 'Goodbye': 'Auf Wiedersehen', 'Thank you': 'Danke', 'Water': 'Wasser'},
        'Italian': {'Hello': 'Ciao', 'Goodbye': 'Arrivederci', 'Thank you': 'Grazie', 'Water': 'Acqua'},
        'Portuguese': {'Hello': 'Olá', 'Goodbye': 'Adeus', 'Thank you': 'Obrigado', 'Water': 'Água'},
        'Arabic': {'Hello': 'مرحبا', 'Goodbye': 'وداعا', 'Thank you': 'شكرا', 'Water': 'ماء'},
        'Russian': {'Hello': 'Привет', 'Goodbye': 'До свидания', 'Thank you': 'Спасибо', 'Water': 'Вода'},
        'Turkish': {'Hello': 'Merhaba', 'Goodbye': 'Güle güle', 'Thank you': 'Teşekkürler', 'Water': 'Su'},
        'Dutch': {'Hello': 'Hallo', 'Goodbye': 'Tot ziens', 'Thank you': 'Dank je', 'Water': 'Water'},
        'Hindi': {'Hello': 'नमस्ते', 'Goodbye': 'अलविदा', 'Thank you': 'धन्यवाद', 'Water': 'पानी'},
        'Telugu': {'Hello': 'నమస్కారం', 'Goodbye': 'వీడ్కోలు', 'Thank you': 'ధన్యవాదాలు', 'Water': 'నీరు'},
        'Swedish': {'Hello': 'Hej', 'Goodbye': 'Hejdå', 'Thank you': 'Tack', 'Water': 'Vatten'},
        'Norwegian': {'Hello': 'Hei', 'Goodbye': 'Ha det', 'Thank you': 'Takk', 'Water': 'Vann'},
        'Danish': {'Hello': 'Hej', 'Goodbye': 'Farvel', 'Thank you': 'Tak', 'Water': 'Vand'},
        'Polish': {'Hello': 'Cześć', 'Goodbye': 'Do widzenia', 'Thank you': 'Dziękuję', 'Water': 'Woda'},
        'Greek': {'Hello': 'Γεια σας', 'Goodbye': 'Αντίο', 'Thank you': 'Ευχαριστώ', 'Water': 'Νερό'},
        'Vietnamese': {'Hello': 'Xin chào', 'Goodbye': 'Tạm biệt', 'Thank you': 'Cảm ơn', 'Water': 'Nước'},
        'Thai': {'Hello': 'สวัสดี', 'Goodbye': 'ลาก่อน', 'Thank you': 'ขอบคุณ', 'Water': 'น้ำ'},
        'Indonesian': {'Hello': 'Halo', 'Goodbye': 'Selamat tinggal', 'Thank you': 'Terima kasih', 'Water': 'Air'},
        'Czech': {'Hello': 'Ahoj', 'Goodbye': 'Na shledanou', 'Thank you': 'Děkuji', 'Water': 'Voda'},
        'English': {'Hello': 'Hello', 'Goodbye': 'Goodbye', 'Thank you': 'Thank you', 'Water': 'Water'},
    }
    
    # Create quiz questions for each language
    for lang_name, trans in translations.items():
        c.execute('SELECT id FROM languages WHERE name = ?', (lang_name,))
        lang_row = c.fetchone()
        if lang_row:
            lang_id = lang_row[0]
            words = ['Hello', 'Goodbye', 'Thank you', 'Water']
            for word in words:
                question = f'What is the {lang_name} word for {word}?'
                correct = trans[word]
                other_words = [w for w in words if w != word]
                options = [correct] + [trans[ow] for ow in other_words]
                random.shuffle(options)
                c.execute('''INSERT INTO quiz_questions 
                            (language_id, question, options, correct_answer, difficulty) 
                            VALUES (?, ?, ?, ?, ?)''', 
                         (lang_id, question, json.dumps(options), correct, 'Beginner'))
    
    conn.commit()

    # Generate native lessons for all languages if missing
    c.execute('SELECT id, name FROM languages')
    all_languages = c.fetchall()
    language_lessons = {
        'English': [
            ('Beginner', 'Greetings', 'Hello', 'Hello', 'Learn how to say hello in English.'),
            ('Beginner', 'Greetings', 'Goodbye', 'Goodbye', 'Say goodbye when you finish the lesson.'),
            ('Beginner', 'Numbers', 'One', 'One', 'Count to one in English.'),
            ('Beginner', 'Numbers', 'Two', 'Two', 'Count to two in English.'),
            ('Beginner', 'Food', 'Water', 'Water', 'Ask for water during a meal.'),
            ('Intermediate', 'Travel', 'Airport', 'Airport', 'Ask for directions to the airport.'),
            ('Intermediate', 'Daily Conversation', 'How are you?', 'How are you?', 'Use this phrase to start daily conversations.'),
            ('Advanced', 'Grammar Basics', 'Because', 'Because', 'Learn how to express reasons in English.'),
        ],
        'Spanish': [
            ('Beginner', 'Greetings', 'Hola', 'Hello', 'Hola, ¿cómo estás?'),
            ('Beginner', 'Greetings', 'Adiós', 'Goodbye', 'Adiós, hasta luego'),
            ('Beginner', 'Numbers', 'Uno', 'One', 'Tengo una manzana'),
            ('Beginner', 'Numbers', 'Dos', 'Two', 'Tengo dos gatos'),
            ('Beginner', 'Food', 'Agua', 'Water', 'Quiero un vaso de agua'),
            ('Intermediate', 'Travel', 'Aeropuerto', 'Airport', 'Necesito ir al aeropuerto'),
            ('Intermediate', 'Daily Conversation', '¿Cómo estás?', 'How are you?', '¿Cómo estás hoy?'),
            ('Advanced', 'Grammar Basics', 'Porque', 'Because', 'No vine porque estaba cansado'),
        ],
        'French': [
            ('Beginner', 'Greetings', 'Bonjour', 'Hello', 'Bonjour, comment ça va ?'),
            ('Beginner', 'Greetings', 'Au revoir', 'Goodbye', 'Au revoir, à bientôt'),
            ('Beginner', 'Numbers', 'Un', 'One', 'J’ai un livre'),
            ('Beginner', 'Numbers', 'Deux', 'Two', 'Il y a deux chaises'),
            ('Beginner', 'Food', 'Eau', 'Water', 'Je veux de l’eau, s’il vous plaît'),
            ('Intermediate', 'Travel', 'Aéroport', 'Airport', 'Je dois aller à l’aéroport'),
            ('Intermediate', 'Daily Conversation', 'Comment ça va ?', 'How are you?', 'Comment ça va aujourd’hui ?'),
            ('Advanced', 'Grammar Basics', 'Parce que', 'Because', 'Je suis venu parce que j’aime apprendre'),
        ],
        'German': [
            ('Beginner', 'Greetings', 'Hallo', 'Hello', 'Hallo, wie geht es dir?'),
            ('Beginner', 'Greetings', 'Auf Wiedersehen', 'Goodbye', 'Auf Wiedersehen, bis bald'),
            ('Beginner', 'Numbers', 'Eins', 'One', 'Ich habe eins Buch'),
            ('Beginner', 'Numbers', 'Zwei', 'Two', 'Ich sehe zwei Vögel'),
            ('Beginner', 'Food', 'Wasser', 'Water', 'Ich möchte Wasser, bitte'),
            ('Intermediate', 'Travel', 'Flughafen', 'Airport', 'Ich muss zum Flughafen gehen'),
            ('Intermediate', 'Daily Conversation', 'Wie geht es dir?', 'How are you?', 'Wie geht es dir heute?'),
            ('Advanced', 'Grammar Basics', 'Weil', 'Because', 'Ich lerne, weil ich besser werden möchte'),
        ],
        'Italian': [
            ('Beginner', 'Greetings', 'Ciao', 'Hello', 'Ciao, come stai?'),
            ('Beginner', 'Greetings', 'Arrivederci', 'Goodbye', 'Arrivederci, a presto'),
            ('Beginner', 'Numbers', 'Uno', 'One', 'Ho uno zaino'),
            ('Beginner', 'Numbers', 'Due', 'Two', 'Ho due amici'),
            ('Beginner', 'Food', 'Acqua', 'Water', 'Vorrei un bicchiere d’acqua'),
            ('Intermediate', 'Travel', 'Aeroporto', 'Airport', 'Dove si trova l’aeroporto?'),
            ('Intermediate', 'Daily Conversation', 'Come stai?', 'How are you?', 'Come stai oggi?'),
            ('Advanced', 'Grammar Basics', 'Perché', 'Because', 'Non sono venuto perché ero occupato'),
        ],
        'Portuguese': [
            ('Beginner', 'Greetings', 'Olá', 'Hello', 'Olá, tudo bem?'),
            ('Beginner', 'Greetings', 'Adeus', 'Goodbye', 'Adeus, até logo'),
            ('Beginner', 'Numbers', 'Um', 'One', 'Tenho um amigo'),
            ('Beginner', 'Numbers', 'Dois', 'Two', 'Vejo dois carros'),
            ('Beginner', 'Food', 'Água', 'Water', 'Preciso de água, por favor'),
            ('Intermediate', 'Travel', 'Aeroporto', 'Airport', 'Vou para o aeroporto amanhã'),
            ('Intermediate', 'Daily Conversation', 'Como vai?', 'How are you?', 'Como vai você hoje?'),
            ('Advanced', 'Grammar Basics', 'Porque', 'Because', 'Eu estudo porque quero melhorar'),
        ],
        'Japanese': [
            ('Beginner', 'Greetings', 'こんにちは', 'Hello', 'こんにちは、お元気ですか？'),
            ('Beginner', 'Greetings', 'さようなら', 'Goodbye', 'さようなら、またね'),
            ('Beginner', 'Numbers', '一', 'One', '私は一つのりんごを持っています'),
            ('Beginner', 'Numbers', '二', 'Two', 'りんごが二つあります'),
            ('Beginner', 'Food', '水', 'Water', '水をください'),
            ('Intermediate', 'Travel', '空港', 'Airport', '空港へ行きたいです'),
            ('Intermediate', 'Daily Conversation', 'お元気ですか？', 'How are you?', '今日はお元気ですか？'),
            ('Advanced', 'Grammar Basics', 'なぜ', 'Because', '私はなぜ日本語を勉強しますか？'),
        ],
        'Chinese': [
            ('Beginner', 'Greetings', '你好', 'Hello', '你好，你怎么样？'),
            ('Beginner', 'Greetings', '再见', 'Goodbye', '再见，明天见'),
            ('Beginner', 'Numbers', '一', 'One', '我有一个苹果'),
            ('Beginner', 'Numbers', '二', 'Two', '桌子上有两个杯子'),
            ('Beginner', 'Food', '水', 'Water', '请给我一杯水'),
            ('Intermediate', 'Travel', '机场', 'Airport', '我需要去机场'),
            ('Intermediate', 'Daily Conversation', '你好吗？', 'How are you?', '你今天好吗？'),
            ('Advanced', 'Grammar Basics', '因为', 'Because', '我来这里因为我想学习'),
        ],
        'Korean': [
            ('Beginner', 'Greetings', '안녕하세요', 'Hello', '안녕하세요, 어떻게 지내세요?'),
            ('Beginner', 'Greetings', '안녕히 가세요', 'Goodbye', '안녕히 가세요, 다음에 봐요'),
            ('Beginner', 'Numbers', '하나', 'One', '나는 하나의 책을 가지고 있어요'),
            ('Beginner', 'Numbers', '둘', 'Two', '집에는 두 개의 방이 있어요'),
            ('Beginner', 'Food', '물', 'Water', '물 한 잔 주세요'),
            ('Intermediate', 'Travel', '공항', 'Airport', '공항으로 가야 해요'),
            ('Intermediate', 'Daily Conversation', '어떻게 지내세요?', 'How are you?', '오늘 어떻게 지내세요?'),
            ('Advanced', 'Grammar Basics', '왜', 'Because', '나는 왜 한국어를 공부해요?'),
        ],
        'Arabic': [
            ('Beginner', 'Greetings', 'مرحبا', 'Hello', 'مرحبا، كيف حالك؟'),
            ('Beginner', 'Greetings', 'وداعا', 'Goodbye', 'وداعا، إلى اللقاء'),
            ('Beginner', 'Numbers', 'واحد', 'One', 'لدي واحد كتاب'),
            ('Beginner', 'Numbers', 'اثنان', 'Two', 'هناك اثنان من الأقلام'),
            ('Beginner', 'Food', 'ماء', 'Water', 'أريد كوباً من الماء'),
            ('Intermediate', 'Travel', 'مطار', 'Airport', 'أحتاج الذهاب إلى المطار'),
            ('Intermediate', 'Daily Conversation', 'كيف حالك؟', 'How are you?', 'كيف حالك اليوم؟'),
            ('Advanced', 'Grammar Basics', 'لأن', 'Because', 'أدرس لأنني أريد التعلم'),
        ],
        'Hindi': [
            ('Beginner', 'Greetings', 'नमस्ते', 'Hello', 'नमस्ते, आप कैसे हैं?'),
            ('Beginner', 'Greetings', 'अलविदा', 'Goodbye', 'अलविदा, फिर मिलेंगे'),
            ('Beginner', 'Numbers', 'एक', 'One', 'मेरे पास एक किताब है'),
            ('Beginner', 'Numbers', 'दो', 'Two', 'मेरे पास दो सेब हैं'),
            ('Beginner', 'Food', 'पानी', 'Water', 'मुझे पानी चाहिए'),
            ('Intermediate', 'Travel', 'हवाई अड्डा', 'Airport', 'मुझे हवाई अड्डे जाना है'),
            ('Intermediate', 'Daily Conversation', 'आप कैसे हैं?', 'How are you?', 'आज आप कैसे हैं?'),
            ('Advanced', 'Grammar Basics', 'क्योंकि', 'Because', 'मैं हिंदी इसलिए सीख रहा हूँ क्योंकि मुझे भाषा पसंद है'),
        ],
        'Telugu': [
            ('Beginner', 'Greetings', 'నమస్కారం', 'Hello', 'నమస్కారం, మీరు ఎలా ఉన్నారు?'),
            ('Beginner', 'Greetings', 'వీడ్కోలు', 'Goodbye', 'వీడ్కోలు, మళ్ళీ కలుద్దాం'),
            ('Beginner', 'Numbers', 'ఒకటి', 'One', 'నా వద్ద ఒక పుస్తకం ఉంది'),
            ('Beginner', 'Numbers', 'రెండు', 'Two', 'నాకు రెండు ఆపిల్స్ ఉన్నాయి'),
            ('Beginner', 'Food', 'నీరు', 'Water', 'దయచేసి నీరు ఇవ్వండి'),
            ('Intermediate', 'Travel', 'విమానాశ్రయం', 'Airport', 'నాకు విమానాశ్రయానికి వెళ్ళాలి'),
            ('Intermediate', 'Daily Conversation', 'మీరు ఎలా ఉన్నారు?', 'How are you?', 'మీరు ఈరోజు ఎలా ఉన్నారు?'),
            ('Advanced', 'Grammar Basics', 'ఎందుకంటే', 'Because', 'నేను నేర్చుకుంటున్నాను ఎందుకంటే నేను మెరుగ్గా కావాలనుకుంటున్నాను'),
        ],
        'Dutch': [
            ('Beginner', 'Greetings', 'Hallo', 'Hello', 'Hallo, hoe gaat het?'),
            ('Beginner', 'Greetings', 'Tot ziens', 'Goodbye', 'Tot ziens, tot ziens later'),
            ('Beginner', 'Numbers', 'Eén', 'One', 'Ik heb één boek'),
            ('Beginner', 'Numbers', 'Twee', 'Two', 'Ik zie twee stoelen'),
            ('Beginner', 'Food', 'Water', 'Water', 'Ik wil water, alstublieft'),
            ('Intermediate', 'Travel', 'Luchthaven', 'Airport', 'Ik moet naar de luchthaven'),
            ('Intermediate', 'Daily Conversation', 'Hoe gaat het?', 'How are you?', 'Hoe gaat het vandaag?'),
            ('Advanced', 'Grammar Basics', 'Omdat', 'Because', 'Ik studeer omdat ik beter wil worden'),
        ],
        'Swedish': [
            ('Beginner', 'Greetings', 'Hej', 'Hello', 'Hej, hur mår du?'),
            ('Beginner', 'Greetings', 'Hejdå', 'Goodbye', 'Hejdå, ses snart'),
            ('Beginner', 'Numbers', 'Ett', 'One', 'Jag har ett äpple'),
            ('Beginner', 'Numbers', 'Två', 'Two', 'Jag ser två bilar'),
            ('Beginner', 'Food', 'Vatten', 'Water', 'Jag vill ha vatten, tack'),
            ('Intermediate', 'Travel', 'Flygplats', 'Airport', 'Jag måste gå till flygplatsen'),
            ('Intermediate', 'Daily Conversation', 'Hur mår du?', 'How are you?', 'Hur mår du idag?'),
            ('Advanced', 'Grammar Basics', 'För att', 'Because', 'Jag lär mig för att bli bättre'),
        ],
        'Norwegian': [
            ('Beginner', 'Greetings', 'Hei', 'Hello', 'Hei, hvordan har du det?'),
            ('Beginner', 'Greetings', 'Ha det', 'Goodbye', 'Ha det, vi sees senere'),
            ('Beginner', 'Numbers', 'En', 'One', 'Jeg har en bok'),
            ('Beginner', 'Numbers', 'To', 'Two', 'Jeg ser to fugler'),
            ('Beginner', 'Food', 'Vann', 'Water', 'Jeg vil ha vann, takk'),
            ('Intermediate', 'Travel', 'Flyplass', 'Airport', 'Jeg må til flyplassen'),
            ('Intermediate', 'Daily Conversation', 'Hvordan har du det?', 'How are you?', 'Hvordan har du det i dag?'),
            ('Advanced', 'Grammar Basics', 'Fordi', 'Because', 'Jeg lærer fordi jeg vil bli bedre'),
        ],
        'Danish': [
            ('Beginner', 'Greetings', 'Hej', 'Hello', 'Hej, hvordan går det?'),
            ('Beginner', 'Greetings', 'Farvel', 'Goodbye', 'Farvel, vi ses'),
            ('Beginner', 'Numbers', 'En', 'One', 'Jeg har en pen'),
            ('Beginner', 'Numbers', 'To', 'Two', 'Der er to stole'),
            ('Beginner', 'Food', 'Vand', 'Water', 'Jeg vil gerne have vand'),
            ('Intermediate', 'Travel', 'Lufthavn', 'Airport', 'Jeg skal til lufthavnen'),
            ('Intermediate', 'Daily Conversation', 'Hvordan har du det?', 'How are you?', 'Hvordan har du det i dag?'),
            ('Advanced', 'Grammar Basics', 'Fordi', 'Because', 'Jeg øver, fordi jeg vil blive bedre'),
        ],
        'Polish': [
            ('Beginner', 'Greetings', 'Cześć', 'Hello', 'Cześć, jak się masz?'),
            ('Beginner', 'Greetings', 'Do widzenia', 'Goodbye', 'Do widzenia, do zobaczenia'),
            ('Beginner', 'Numbers', 'Jeden', 'One', 'Mam jeden zeszyt'),
            ('Beginner', 'Numbers', 'Dwa', 'Two', 'Widzę dwa koty'),
            ('Beginner', 'Food', 'Woda', 'Water', 'Proszę o wodę'),
            ('Intermediate', 'Travel', 'Lotnisko', 'Airport', 'Muszę iść na lotnisko'),
            ('Intermediate', 'Daily Conversation', 'Jak się masz?', 'How are you?', 'Jak się masz dzisiaj?'),
            ('Advanced', 'Grammar Basics', 'Ponieważ', 'Because', 'Uczę się, ponieważ chcę podróżować'),
        ],
        'Greek': [
            ('Beginner', 'Greetings', 'Γεια σου', 'Hello', 'Γεια σου, πώς είσαι;'),
            ('Beginner', 'Greetings', 'Αντίο', 'Goodbye', 'Αντίο, τα λέμε'),
            ('Beginner', 'Numbers', 'Ένα', 'One', 'Έχω ένα βιβλίο'),
            ('Beginner', 'Numbers', 'Δύο', 'Two', 'Βλέπω δύο πουλιά'),
            ('Beginner', 'Food', 'Νερό', 'Water', 'Θέλω νερό, παρακαλώ'),
            ('Intermediate', 'Travel', 'Αεροδρόμιο', 'Airport', 'Πρέπει να πάω στο αεροδρόμιο'),
            ('Intermediate', 'Daily Conversation', 'Πώς είσαι;', 'How are you?', 'Πώς είσαι σήμερα;'),
            ('Advanced', 'Grammar Basics', 'Επειδή', 'Because', 'Μαθαίνω επειδή μου αρέσει'),
        ],
        'Vietnamese': [
            ('Beginner', 'Greetings', 'Xin chào', 'Hello', 'Xin chào, bạn khỏe không?'),
            ('Beginner', 'Greetings', 'Tạm biệt', 'Goodbye', 'Tạm biệt, hẹn gặp lại'),
            ('Beginner', 'Numbers', 'Một', 'One', 'Tôi có một cuốn sách'),
            ('Beginner', 'Numbers', 'Hai', 'Two', 'Tôi thấy hai con mèo'),
            ('Beginner', 'Food', 'Nước', 'Water', 'Cho tôi một ly nước'),
            ('Intermediate', 'Travel', 'Sân bay', 'Airport', 'Tôi cần đến sân bay'),
            ('Intermediate', 'Daily Conversation', 'Bạn khỏe không?', 'How are you?', 'Bạn khỏe không hôm nay?'),
            ('Advanced', 'Grammar Basics', 'Bởi vì', 'Because', 'Tôi học vì tôi muốn giỏi hơn'),
        ],
        'Thai': [
            ('Beginner', 'Greetings', 'สวัสดี', 'Hello', 'สวัสดี, คุณสบายดีหรือเปล่า?'),
            ('Beginner', 'Greetings', 'ลาก่อน', 'Goodbye', 'ลาก่อน, ไว้เจอกันใหม่'),
            ('Beginner', 'Numbers', 'หนึ่ง', 'One', 'ฉันมีหนังสือหนึ่งเล่ม'),
            ('Beginner', 'Numbers', 'สอง', 'Two', 'มีสองแก้วบนโต๊ะ'),
            ('Beginner', 'Food', 'น้ำ', 'Water', 'ขอน้ำหนึ่งแก้ว'),
            ('Intermediate', 'Travel', 'สนามบิน', 'Airport', 'ฉันต้องไปสนามบิน'),
            ('Intermediate', 'Daily Conversation', 'คุณสบายดีไหม?', 'How are you?', 'คุณสบายดีไหมวันนี้?'),
            ('Advanced', 'Grammar Basics', 'เพราะ', 'Because', 'ฉันเรียนเพราะฉันอยากพัฒนา'),
        ],
        'Indonesian': [
            ('Beginner', 'Greetings', 'Halo', 'Hello', 'Halo, apa kabar?'),
            ('Beginner', 'Greetings', 'Selamat tinggal', 'Goodbye', 'Selamat tinggal, sampai nanti'),
            ('Beginner', 'Numbers', 'Satu', 'One', 'Saya punya satu buku'),
            ('Beginner', 'Numbers', 'Dua', 'Two', 'Ada dua kursi'),
            ('Beginner', 'Food', 'Air', 'Water', 'Tolong berikan air'),
            ('Intermediate', 'Travel', 'Bandara', 'Airport', 'Saya harus ke bandara'),
            ('Intermediate', 'Daily Conversation', 'Apa kabar?', 'How are you?', 'Apa kabar hari ini?'),
            ('Advanced', 'Grammar Basics', 'Karena', 'Because', 'Saya belajar karena ingin menjadi lebih baik'),
        ],
        'Czech': [
            ('Beginner', 'Greetings', 'Ahoj', 'Hello', 'Ahoj, jak se máš?'),
            ('Beginner', 'Greetings', 'Na shledanou', 'Goodbye', 'Na shledanou, uvidíme se později'),
            ('Beginner', 'Numbers', 'Jedna', 'One', 'Mám jedno jablko'),
            ('Beginner', 'Numbers', 'Dva', 'Two', 'Vidím dva ptáky'),
            ('Beginner', 'Food', 'Voda', 'Water', 'Prosím o vodu'),
            ('Intermediate', 'Travel', 'Letiště', 'Airport', 'Musím jet na letiště'),
            ('Intermediate', 'Daily Conversation', 'Jak se máš?', 'How are you?', 'Jak se máš dnes?'),
            ('Advanced', 'Grammar Basics', 'Protože', 'Because', 'Učím se, protože chci být lepší'),
        ],
        'Russian': [
            ('Beginner', 'Greetings', 'Привет', 'Hello', 'Привет, как дела?'),
            ('Beginner', 'Greetings', 'До свидания', 'Goodbye', 'До свидания, до скорого'),
            ('Beginner', 'Numbers', 'Один', 'One', 'У меня один учебник'),
            ('Beginner', 'Numbers', 'Два', 'Two', 'Я вижу два стула'),
            ('Beginner', 'Food', 'Вода', 'Water', 'Мне нужна вода, пожалуйста'),
            ('Intermediate', 'Travel', 'Аэропорт', 'Airport', 'Мне нужно в аэропорт'),
            ('Intermediate', 'Daily Conversation', 'Как дела?', 'How are you?', 'Как дела сегодня?'),
            ('Advanced', 'Grammar Basics', 'Потому что', 'Because', 'Я учу, потому что хочу лучше'),
        ],
        'Turkish': [
            ('Beginner', 'Greetings', 'Merhaba', 'Hello', 'Merhaba, nasılsın?'),
            ('Beginner', 'Greetings', 'Güle güle', 'Goodbye', 'Güle güle, görüşürüz'),
            ('Beginner', 'Numbers', 'Bir', 'One', 'Bir kitabım var'),
            ('Beginner', 'Numbers', 'İki', 'Two', 'İki elma görüyorum'),
            ('Beginner', 'Food', 'Su', 'Water', 'Bir bardak su lütfen'),
            ('Intermediate', 'Travel', 'Havaalanı', 'Airport', 'Havaalanına gitmem gerekiyor'),
            ('Intermediate', 'Daily Conversation', 'Nasılsın?', 'How are you?', 'Bugün nasılsın?'),
            ('Advanced', 'Grammar Basics', 'Çünkü', 'Because', 'Çalışıyorum çünkü daha iyi olmak istiyorum'),
        ],
    }

    generic_keywords = ('Hello', 'Goodbye', 'One', 'Two', 'Water', 'Airport', 'How are you?', 'Because')

    for lang in all_languages:
        lang_id = lang['id']
        lang_name = lang['name']

        # Count existing lessons
        c.execute('SELECT COUNT(*) FROM lessons WHERE language_id = ?', (lang_id,))
        lesson_count = c.fetchone()[0]

        if lesson_count == 0:
            should_replace = True
        else:
            # Detect old generic English lessons for non-English languages
            c.execute('''SELECT COUNT(*) FROM lessons 
                         WHERE language_id = ? AND word IN ({})'''.format(
                         ','.join('?' for _ in generic_keywords)),
                      (lang_id, *generic_keywords))
            generic_match_count = c.fetchone()[0]
            should_replace = lang_name != 'English' and generic_match_count == lesson_count

        if should_replace:
            if lesson_count > 0:
                c.execute('DELETE FROM lessons WHERE language_id = ?', (lang_id,))

            lessons_for_lang = language_lessons.get(lang_name, language_lessons['English'])
            for level, category, word, meaning, example in lessons_for_lang:
                c.execute('''INSERT INTO lessons 
                            (language_id, level, category, word, meaning, example) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (lang_id, level, category, word, meaning, example))
            conn.commit()

    conn.close()

# ======================== ROUTES ========================

@app.route('/')
def index():
    """Homepage - Show all languages"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM languages')
    languages = c.fetchall()
    conn.close()

    landing_page = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FluentBridge - Master Languages Anywhere</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
        <style>
            .choose-language-section {
                padding: 4rem 0;
                background: #f8fbff;
            }
            .choose-language-section .section-title {
                margin-bottom: 0.5rem;
            }
            .choose-language-section .section-subtitle {
                text-align: center;
                color: var(--gray);
                max-width: 660px;
                margin: 0 auto 2.5rem;
                font-size: 1.05rem;
                line-height: 1.8;
            }
            .language-slider-wrapper {
                position: relative;
                max-width: 1200px;
                margin: 0 auto;
            }
            .language-slider {
                display: flex;
                gap: 1rem;
                overflow-x: auto;
                padding: 0 1.5rem;
                scroll-snap-type: x mandatory;
                scroll-behavior: smooth;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                -ms-overflow-style: none;
                cursor: grab;
            }
            .language-slider::-webkit-scrollbar {
                display: none;
            }
            .language-slider-card {
                flex: 0 0 auto;
                width: 160px;
                height: 210px;
                border-radius: 24px;
                background: white;
                padding: 1rem;
                text-decoration: none;
                box-shadow: 0 18px 40px rgba(102, 126, 234, 0.12);
                color: var(--dark);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                transition: transform 0.25s ease, box-shadow 0.25s ease;
                scroll-snap-align: start;
                border: 1px solid rgba(102, 126, 234, 0.08);
            }
            .language-slider-card:hover {
                transform: translateY(-6px);
                box-shadow: 0 24px 50px rgba(102, 126, 234, 0.18);
            }
            .slider-flag {
                width: 92px;
                height: 92px;
                border-radius: 50%;
                display: grid;
                place-items: center;
                background: white;
                font-size: 2.8rem;
                margin-bottom: 1rem;
                box-shadow: 0 18px 32px rgba(102, 126, 234, 0.12);
            }
            .language-slider-card h3 {
                margin: 0;
                font-size: 1rem;
                font-weight: 700;
                letter-spacing: 0.01em;
            }
            .slider-arrow {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 48px;
                height: 48px;
                border-radius: 50%;
                background: white;
                border: 1px solid rgba(102, 126, 234, 0.24);
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 14px 30px rgba(0, 0, 0, 0.08);
                transition: transform 0.25s ease, background 0.25s ease, color 0.25s ease;
                z-index: 2;
                color: var(--primary);
            }
            .slider-arrow:hover {
                transform: translateY(-50%) scale(1.05);
                background: var(--primary);
                color: white;
            }
            .slider-arrow-left {
                left: 0.75rem;
            }
            .slider-arrow-right {
                right: 0.75rem;
            }
            @media (max-width: 768px) {
                .slider-arrow {
                    display: none;
                }
                .language-slider {
                    padding: 0 1rem;
                }
                .choose-language-section {
                    padding: 3rem 0;
                }
            }
            .language-slider.active,
            .language-slider:active {
                cursor: grabbing;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">
                <h1 class="logo">FluentBridge</h1>
            </div>
            <div class="navbar-right">
                <a href="/login" class="btn btn-outline">Sign In</a>
                <a href="/signup" class="btn btn-primary">Get Started</a>
                <button class="btn btn-outline btn-small dark-toggle" type="button" onclick="toggleDarkMode()">🌙</button>
            </div>
        </nav>

        <section class="hero">
            <h2>Master 20+ Languages</h2>
            <p>Learn at your own pace with interactive lessons, quizzes, and daily challenges</p>
            <a href="/login" class="btn btn-primary btn-large">Start Learning Today</a>
        </section>

      

        <section class="features">
            <div class="container">
                <h2 class="section-title">Why Choose FluentBridge?</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📚</div>
                        <h3>Structured Lessons</h3>
                        <p>Learn from beginner to advanced with organized lessons and categories</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎯</div>
                        <h3>Interactive Quizzes</h3>
                        <p>Test your knowledge with varied quiz types and instant feedback</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔥</div>
                        <h3>Daily Streaks</h3>
                        <p>Build consistent learning habits and track your progress</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🏆</div>
                        <h3>Achievements</h3>
                        <p>Earn badges and compete on the leaderboard</p>
                    </div>
                </div>
            </div>
        </section>

        <footer class="footer">
            <p>&copy; 2026 FluentBridge. All rights reserved.</p>
        </footer>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const slider = document.querySelector('.language-slider');
                const prev = document.querySelector('.slider-arrow-left');
                const next = document.querySelector('.slider-arrow-right');
                if (!slider || !prev || !next) return;
                prev.addEventListener('click', function() {
                    slider.scrollBy({ left: -220, behavior: 'smooth' });
                });
                next.addEventListener('click', function() {
                    slider.scrollBy({ left: 220, behavior: 'smooth' });
                });

                let isDown = false;
                let startX = 0;
                let scrollLeft = 0;

                slider.addEventListener('mousedown', function(e) {
                    isDown = true;
                    slider.classList.add('active');
                    startX = e.pageX - slider.offsetLeft;
                    scrollLeft = slider.scrollLeft;
                });
                slider.addEventListener('mouseleave', function() {
                    isDown = false;
                    slider.classList.remove('active');
                });
                slider.addEventListener('mouseup', function() {
                    isDown = false;
                    slider.classList.remove('active');
                });
                slider.addEventListener('mousemove', function(e) {
                    if (!isDown) return;
                    e.preventDefault();
                    const x = e.pageX - slider.offsetLeft;
                    const walk = (x - startX) * 1.5;
                    slider.scrollLeft = scrollLeft - walk;
                });
                slider.addEventListener('touchstart', function(e) {
                    startX = e.touches[0].pageX - slider.offsetLeft;
                    scrollLeft = slider.scrollLeft;
                });
                slider.addEventListener('touchmove', function(e) {
                    const x = e.touches[0].pageX - slider.offsetLeft;
                    const walk = (x - startX) * 1.5;
                    slider.scrollLeft = scrollLeft - walk;
                });
            });
        </script>
    </body>
    </html>
    '''

    return render_template_string(landing_page, languages=languages)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup"""
    next_page = request.form.get('next') or request.args.get('next')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            return render_template('signup_page.html', error='All fields required', next=next_page)
        
        conn = get_db()
        c = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, hashed_password))
            conn.commit()
            
            # Get the new user ID
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user_id = c.fetchone()[0]
            
            # Initialize user progress for all languages
            c.execute('SELECT id FROM languages')
            languages = c.fetchall()
            for lang in languages:
                c.execute('''INSERT INTO user_progress (user_id, language_id) 
                           VALUES (?, ?)''', (user_id, lang[0]))
            conn.commit()
            conn.close()
            
            session['user_id'] = user_id
            session['name'] = name
            return redirect(next_page or url_for('dashboard'))
        
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup_page.html', error='Email already exists', next=next_page)
    
    return render_template('signup_page.html', next=next_page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    next_page = request.form.get('next') or request.args.get('next')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login_page.html', error='Email and password required', next=next_page)
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['user_id'] = user['id']
            session['name'] = user['name']
            return redirect(next_page or url_for('dashboard'))
        
        return render_template('login_page.html', error='Invalid email or password', next=next_page)
    
    return render_template('login_page.html', next=next_page)

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    conn = get_db()
    c = conn.cursor()
    message = None
    error = None

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            c.execute('DELETE FROM user_progress WHERE user_id = ?',
                      (session['user_id'],))
            c.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
            conn.commit()
            conn.close()
            session.clear()
            return redirect(url_for('index'))

        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                c.execute('UPDATE users SET profile_photo = ? WHERE id = ?',
                          (filename, session['user_id']))
                conn.commit()
                message = 'Profile photo updated successfully.'

        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if not name:
            error = 'Name cannot be empty.'
        elif not email:
            error = 'Email cannot be empty.'
        elif password and password != confirm:
            error = 'Passwords do not match.'
        else:
            c.execute('SELECT id FROM users WHERE email = ? AND id != ?',
                      (email, session['user_id']))
            existing = c.fetchone()
            if existing:
                error = 'That email is already in use.'
            else:
                if password:
                    hashed_password = generate_password_hash(password)
                    c.execute('UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?',
                              (name, email, hashed_password, session['user_id']))
                else:
                    c.execute('UPDATE users SET name = ?, email = ? WHERE id = ?',
                              (name, email, session['user_id']))
                conn.commit()
                session['name'] = name
                if not message:
                    message = 'Profile updated successfully.'

    c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()

    c.execute('SELECT * FROM user_progress WHERE user_id = ?', (session['user_id'],))
    progress_rows = c.fetchall()

    c.execute('SELECT COUNT(*) FROM user_progress WHERE user_id = ? AND score >= 80',
             (session['user_id'],))
    completed_languages = c.fetchone()[0]

    average_score = 0
    if progress_rows:
        average_score = int(
            sum([row['score'] for row in progress_rows]) / len(progress_rows)
        )

    total_quizzes = sum([row['quizzes_completed'] for row in progress_rows]) if progress_rows else 0
    max_streak = max([row['streak'] for row in progress_rows]) if progress_rows else 0
    languages_started = sum(
        1 for row in progress_rows
        if row['score'] > 0 or row['lessons_completed'] > 0 or row['quizzes_completed'] > 0
    )
    achievements = []
    if max_streak >= 7:
        achievements.append({'icon': '🔥', 'title': 'Streak Keeper', 'subtitle': f'{max_streak}-day streak'})
    if total_quizzes >= 5:
        achievements.append({'icon': '🧠', 'title': 'Quiz Champion', 'subtitle': f'{total_quizzes} quizzes completed'})
    if languages_started >= 3:
        achievements.append({'icon': '🌍', 'title': 'Polyglot Path', 'subtitle': f'{languages_started} languages started'})
    if not achievements:
        achievements.append({'icon': '✨', 'title': 'Keep Going', 'subtitle': 'Complete lessons and quizzes to unlock more achievements'})

    selected_language = None
    if session.get('language_id'):
        c.execute('SELECT * FROM languages WHERE id = ?',
                 (session['language_id'],))
        selected_language = c.fetchone()

    # Store languages in dictionary
    languages = {}

    c.execute('SELECT id, name, flag FROM languages')

    for row in c.fetchall():
        languages[row['id']] = dict(row)

    detailed_progress = []

    for row in progress_rows:
        language = languages.get(row['language_id'])

        if language:
            language_name = language['name']
            language_flag = language['flag']
        else:
            language_name = 'Unknown'
            language_flag = '🌍'

        detailed_progress.append({
            'language_name': language_name,
            'language_flag': language_flag,
            'level': row['level'],
            'score': row['score'],
            'streak': row['streak'],
            'lessons_completed': row['lessons_completed'],
            'quizzes_completed': row['quizzes_completed'],
        })

    conn.close()

    return render_template(
        'profile.html',
        user=user,
        selected_language=selected_language,
        progress_rows=detailed_progress,
        completed_languages=completed_languages,
        average_score=average_score,
        achievements=achievements,
        message=message,
        error=error
    )

@app.route('/select-language/<int:lang_id>')
@login_required
def select_language(lang_id):
    """Select a language and go to dashboard"""
    session['language_id'] = lang_id
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    conn = get_db()
    c = conn.cursor()
    
    # Get user info
    c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()
    
    # Get all languages
    c.execute('SELECT * FROM languages')
    languages = c.fetchall()
    
    # Get user progress for each language
    c.execute('''SELECT * FROM user_progress WHERE user_id = ?''', (session['user_id'],))
    progress_rows = c.fetchall()
    progress = {row['language_id']: row for row in progress_rows}
    
    selected_language = None
    selected_progress = None
    recommended_lesson = None
    if session.get('language_id'):
        c.execute('SELECT * FROM languages WHERE id = ?', (session['language_id'],))
        selected_language = c.fetchone()
        selected_progress = progress.get(session['language_id'])

        if selected_language:
            current_level = selected_progress['level'] if selected_progress and selected_progress['level'] else 'Beginner'
            c.execute('''SELECT word, meaning, category FROM lessons
                         WHERE language_id = ? AND level = ?
                         ORDER BY id ASC LIMIT 1''',
                      (selected_language['id'], current_level))
            row = c.fetchone()
            if not row:
                c.execute('''SELECT word, meaning, category FROM lessons
                             WHERE language_id = ? ORDER BY id ASC LIMIT 1''',
                          (selected_language['id'],))
                row = c.fetchone()
            if row:
                recommended_lesson = {
                    'word': row['word'],
                    'meaning': row['meaning'],
                    'category': row['category'],
                    'level': current_level
                }

    overall_score = 0
    if progress_rows:
        overall_score = int(sum([row['score'] for row in progress_rows]) / len(progress_rows))

    total_quizzes = sum([row['quizzes_completed'] for row in progress_rows]) if progress_rows else 0
    max_streak = max([row['streak'] for row in progress_rows]) if progress_rows else 0
    languages_started = sum(
        1 for row in progress_rows
        if row['score'] > 0 or row['lessons_completed'] > 0 or row['quizzes_completed'] > 0
    )
    achievements = []
    if max_streak >= 7:
        achievements.append({'icon': '🔥', 'title': 'Streak Keeper', 'subtitle': f'{max_streak}-day streak'})
    if total_quizzes >= 5:
        achievements.append({'icon': '🧠', 'title': 'Quiz Champion', 'subtitle': f'{total_quizzes} quizzes completed'})
    if languages_started >= 3:
        achievements.append({'icon': '🌍', 'title': 'Polyglot Path', 'subtitle': f'{languages_started} languages started'})
    if not achievements:
        achievements.append({'icon': '✨', 'title': 'Keep Going', 'subtitle': 'Complete lessons and quizzes to unlock more achievements'})

    if overall_score >= 80:
        badge = 'Language Master'
    elif overall_score >= 60:
        badge = 'Rising Star'
    elif overall_score >= 40:
        badge = 'Learner'
    else:
        badge = 'New Explorer'

    conn.close()
    
    return render_template('dashboard_page.html', 
                          user=user, 
                          languages=languages,
                          progress=progress,
                          selected_language=selected_language,
                          selected_progress=selected_progress,
                          recommended_lesson=recommended_lesson,
                          overall_score=overall_score,
                          badge=badge,
                          achievements=achievements)

@app.route('/lessons/<int:lang_id>')
@login_required
def lessons(lang_id):
    """View lessons for a language"""
    conn = get_db()
    c = conn.cursor()

    # Get language
    c.execute('SELECT * FROM languages WHERE id = ?', (lang_id,))
    language = c.fetchone()

    # Get lessons by level
    c.execute('''SELECT DISTINCT level FROM lessons WHERE language_id = ? 
                ORDER BY CASE level 
                         WHEN 'Beginner' THEN 1 
                         WHEN 'Intermediate' THEN 2 
                         WHEN 'Advanced' THEN 3 
                         END''', (lang_id,))
    levels = [row[0] for row in c.fetchall()]

    # Get lessons by category for each level
    lessons_data = {}
    for level in levels:
        c.execute('''SELECT DISTINCT category FROM lessons 
                    WHERE language_id = ? AND level = ?''', (lang_id, level))
        categories = [row[0] for row in c.fetchall()]
        lessons_data[level] = {}

        for category in categories:
            c.execute('''SELECT * FROM lessons 
                        WHERE language_id = ? AND level = ? AND category = ?''',
                     (lang_id, level, category))
            lessons_data[level][category] = c.fetchall()

    # Get user progress
    c.execute('SELECT * FROM user_progress WHERE user_id = ? AND language_id = ?',
             (session['user_id'], lang_id))
    user_progress = c.fetchone()
    
    conn.close()
    
    return render_template('lessons_page.html',
                          language=language,
                          levels=levels,
                          lessons_data=lessons_data,
                          user_progress=user_progress)

@app.route('/pronounce')
@login_required
def pronounce():
    word = request.args.get('word', '').strip()
    language = request.args.get('lang', 'English').strip()
    if not word:
        return redirect(request.referrer or url_for('dashboard'))

    voice_code = get_voice_lang_code(language)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_path = temp_wav.name
    temp_wav.close()

    temp_txt = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8')
    temp_txt.write(word)
    temp_txt_path = temp_txt.name
    temp_txt.close()

    safe_path = temp_path.replace("'", "''")
    safe_txt_path = temp_txt_path.replace("'", "''")
    voice_prefix = voice_code.split('-')[0]
    ps_script = (
        "Add-Type -AssemblyName System.Speech; "
        "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voice = $synth.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like '*" + voice_prefix + "*' -or $_.VoiceInfo.Culture.TwoLetterISOLanguageName -eq '" + voice_prefix + "' } | Select-Object -First 1; "
        "if (-not $voice) { $voice = $synth.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like '*en*' -or $_.VoiceInfo.Culture.TwoLetterISOLanguageName -eq 'en' } | Select-Object -First 1 }; "
        "if ($voice) { $synth.SelectVoice($voice.VoiceInfo.Name) }; "
        "$text = Get-Content -Raw -Path '" + safe_txt_path + "'; "
        "$synth.SetOutputToWaveFile('" + safe_path + "'); "
        "$synth.Speak($text); "
        "$synth.Dispose();"
    )

    try:
        subprocess.run(
            [
                'powershell.exe',
                '-NoProfile',
                '-ExecutionPolicy',
                'Bypass',
                '-Command',
                ps_script
            ],
            capture_output=True,
            text=True,
            check=True
        )

        with open(temp_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        return send_file(BytesIO(audio_data), mimetype='audio/wav', as_attachment=False)
    except subprocess.CalledProcessError as exc:
        return jsonify({'error': 'TTS generation failed', 'details': exc.stderr}), 500
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(temp_txt_path):
            os.unlink(temp_txt_path)

@app.route('/quiz/<int:lang_id>')
@login_required
def quiz(lang_id):
    """Take a quiz for a language"""
    conn = get_db()
    c = conn.cursor()
    
    # Get language
    c.execute('SELECT * FROM languages WHERE id = ?', (lang_id,))
    language = c.fetchone()
    
    # Get all quiz questions
    c.execute('SELECT * FROM quiz_questions WHERE language_id = ?', (lang_id,))
    questions = c.fetchall()

    # Convert sqlite rows to normal dictionaries
    questions = [dict(q) for q in questions]

    # Shuffle questions
    random.shuffle(questions)

    # Take first 8 questions
    questions = questions[:8]

    # Convert options JSON string to Python list
    for question in questions:
        question['options'] = json.loads(question['options'])
    
    conn.close()
    
    return render_template('quiz_page.html', language=language, questions=questions)

@app.route('/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    """Submit quiz answers and calculate score"""
    data = request.get_json()
    lang_id = data['language_id']
    answers = data['answers']
    
    conn = get_db()
    c = conn.cursor()
    
    score = 0
    total = len(answers)
    
    for q_id, answer in answers.items():
        c.execute('SELECT correct_answer FROM quiz_questions WHERE id = ?', (q_id,))
        row = c.fetchone()
        if row and row['correct_answer'] == answer:
            score += 1
    
    # Get current user progress
    c.execute('SELECT * FROM user_progress WHERE user_id = ? AND language_id = ?',
             (session['user_id'], lang_id))
    progress = c.fetchone()
    
    # Calculate streak
    today = datetime.now().date()
    last_learned = None
    new_streak = 1
    
    if progress and progress['last_learned']:
        last_learned_str = progress['last_learned'].split(' ')[0]  # Extract date part
        last_learned = datetime.strptime(last_learned_str, '%Y-%m-%d').date()
        
        # Check if user already learned today
        if last_learned == today:
            new_streak = progress['streak']  # Don't increment if already done today
        # Check if learned yesterday
        elif (today - last_learned).days == 1:
            new_streak = progress['streak'] + 1  # Increment streak
        # Otherwise reset streak
        else:
            new_streak = 1
    
    # Update user progress
    percentage = (score / total * 100) if total > 0 else 0
    
    # Calculate new average score
    current_score = progress['score'] if progress else 0
    new_average = (current_score + percentage) / 2
    
    # Determine level based on average score
    if new_average >= 70:
        new_level = 'Advanced'
    elif new_average >= 40:
        new_level = 'Intermediate'
    else:
        new_level = 'Beginner'
    
    c.execute('''UPDATE user_progress SET 
                lessons_completed = lessons_completed + 1,
                quizzes_completed = quizzes_completed + 1,
                score = ?,
                level = ?,
                streak = ?,
                last_learned = CURRENT_TIMESTAMP
                WHERE user_id = ? AND language_id = ?''',
             (int(percentage), new_level, new_streak, session['user_id'], lang_id))
    conn.commit()
    conn.close()
    
    return jsonify({'score': score, 'total': total, 'percentage': percentage})

@app.route('/api/languages')
def api_languages():
    """API endpoint for languages"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM languages')
    languages = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(languages)

# ======================== ERROR HANDLERS ========================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# ======================== APP INITIALIZATION ========================

if __name__ == '__main__':
    # Initialize database first
    init_db()
    
    # Create uploads folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Populate sample data
    populate_sample_data()
    
    # Open browser automatically
    import webbrowser
    webbrowser.open('http://localhost:5000')
    
    # Run app
    app.run(debug=True)
