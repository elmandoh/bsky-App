import os
import random
from groq import Groq
from atproto import Client
from apps_data import APPS

# إعداد Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ACCOUNTS = [
    {"handle": "globalpulse24.bsky.social", "password": os.environ.get("GLOBALPULSE24")},
    {"handle": "k3live.bsky.social", "password": os.environ.get("K3LIVE")},
    {"handle": "eurotrends24.bsky.social", "password": os.environ.get("EUROTRENDS24")}
]

def generate_marketing_post(app):
    keywords_str = ", ".join(app['keywords'])
    prompt = f"Write a professional and catchy social media post in Arabic for an Android app named '{app['name']}'. Context: {keywords_str}. The post should be persuasive, include emojis, and end with the link: {app['url']}."
    
    # تأكد من المسافات هنا (4 مسافات تحت الدالة)
    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant", # الموديل الأحدث والشغال
    )
    return completion.choices[0].message.content

def main():
    selected_app = random.choice(APPS)
    
    for acc in ACCOUNTS:
        try:
            client = Client()
            client.login(acc["handle"], acc["password"])
            
            post_text = generate_marketing_post(selected_app)
            
            client.send_post(text=post_text)
            print(f"✅ Posted about {selected_app['name']} on {acc['handle']}")
        except Exception as e:
            print(f"❌ Error on {acc['handle']}: {e}")

if __name__ == "__main__":
    main()
