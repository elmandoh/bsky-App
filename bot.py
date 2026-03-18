import os
import random
from groq import Groq
from atproto import Client, client_utils # أضفنا client_utils للروابط

# إعداد Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ACCOUNTS = [
    {"handle": "globalpulse24.bsky.social", "password": os.environ.get("GLOBALPULSE24")},
    {"handle": "k3live.bsky.social", "password": os.environ.get("K3LIVE")},
    {"handle": "eurotrends24.bsky.social", "password": os.environ.get("EUROTRENDS24")}
]

# استيراد قائمة التطبيقات (تأكد أن ملف apps_data.py موجود)
from apps_data import APPS

def generate_marketing_post(app):
    keywords_str = ", ".join(app['keywords'])
    # طلبنا هاشتاجات ذكية من الذكاء الاصطناعي
    prompt = f"""Write a very short, viral Arabic post for the app '{app['name']}'. 
    Context: {keywords_str}. 
    Requirements:
    1. Max 150 characters.
    2. Include 2-3 relevant hashtags (e.g. #تطبيقات #اندرويد).
    3. Make it sound like a top recommendation.
    4. Link to include: {app['url']}"""
    
    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    
    post_text = completion.choices[0].message.content
    if len(post_text) > 290:
        post_text = post_text[:280] + "..."
    return post_text

def main():
    selected_app = random.choice(APPS)
    
    for acc in ACCOUNTS:
        try:
            client = Client()
            client.login(acc["handle"], acc["password"])
            
            post_text = generate_marketing_post(selected_app)
            
            # استخدام TextBuilder لجعل الرابط والهاشتاجات قابلة للضغط وزيادة الانتشار
            tb = client_utils.TextBuilder()
            tb.text(post_text)
            
            # إرسال المنشور مع الـ Facets (الروابط النشطة)
            client.send_post(tb)
            print(f"✅ Viral post published for {selected_app['name']} on {acc['handle']}")
        except Exception as e:
            print(f"❌ Error on {acc['handle']}: {e}")

if __name__ == "__main__":
    main()
