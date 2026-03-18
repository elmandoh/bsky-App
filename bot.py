import os
import random
from groq import Groq
from atproto import Client, client_utils
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
    # الـ Prompt الجديد مخصص للجمهور الأمريكي
    prompt = f"""Write a viral, high-energy English marketing post for the US audience for this app: '{app['name']}'.
    Context: {keywords_str}.
    Guidelines:
    - Language: Casual American English.
    - Style: Solves a problem or highlights a cool benefit.
    - Max 160 characters.
    - Include 2 trending US hashtags.
    - DO NOT include the link in the AI text, I will add it manually.
    """
    
    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    
    return completion.choices[0].message.content.strip()

def main():
    selected_app = random.choice(APPS)
    
    for acc in ACCOUNTS:
        try:
            client = Client()
            client.login(acc["handle"], acc["password"])
            
            # 1. توليد النص الإنجليزي
            ai_text = generate_marketing_post(selected_app)
            
            # 2. بناء المنشور برابط "أزرق" نشط احترافي
            tb = client_utils.TextBuilder()
            tb.text(f"{ai_text}\n\nCheck it out here: ")
            tb.link(selected_app['name'], selected_app['url']) # هيظهر اسم التطبيق كـ رابط أزرق
            
            # 3. إرسال المنشور
            client.send_post(tb)
            print(f"✅ Professional English post sent for {selected_app['name']} to {acc['handle']}")
        except Exception as e:
            print(f"❌ Error on {acc['handle']}: {e}")

if __name__ == "__main__":
    main()
