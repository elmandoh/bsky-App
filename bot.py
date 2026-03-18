import os
import random
import re
from groq import Groq
from atproto import Client, client_utils, models
from apps_data import APPS

# إعداد Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ACCOUNTS = [
    {"handle": "globalpulse24.bsky.social", "password": os.environ.get("GLOBALPULSE24")},
    {"handle": "k3live.bsky.social", "password": os.environ.get("K3LIVE")},
    {"handle": "eurotrends24.bsky.social", "password": os.environ.get("EUROTRENDS24")}
]

def generate_english_post(app):
    prompt = f"""Write a catchy 1-sentence English teaser for an app called '{app['name']}'. 
    Topic: {', '.join(app['keywords'])}. 
    Make it sound like a useful discovery for US users. No links, no hashtags."""
    
    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    return completion.choices[0].message.content.strip().replace('"', '')

def main():
    selected_app = random.choice(APPS)
    post_content = generate_english_post(selected_app)
    
    # إضافة هاشتاجات تريند أمريكية بشكل طبيعي في سطر منفصل
    hashtags = " #Tech #AppStore #Android" 

    for acc in ACCOUNTS:
        try:
            client = Client()
            client.login(acc["handle"], acc["password"])
            
            # بناء المنشور مع الروابط والهاشتاجات كـ Facets لتكون "نشطة"
            text_builder = client_utils.TextBuilder()
            text_builder.text(f"{post_content}\n\n")
            text_builder.tag("#TechTips", "TechTips")
            text_builder.text(" ")
            text_builder.tag("#MustHave", "MustHave")

            # أهم جزء: إنشاء بطاقة المعاينة (Link Card)
            # ملحوظة: Bluesky يحتاج أحياناً لرفع صورة المعاينة يدوياً أو استخدام Open Graph
            # سنستخدم هنا الطريقة المباشرة لجعل الرابط "ظاهرياً" كبطاقة
            
            client.send_post(
                text=text_builder,
                embed=models.AppBskyEmbedExternal.Main(
                    external=models.AppBskyEmbedExternal.External(
                        title=selected_app['name'],
                        description=f"Get {selected_app['name']} on Google Play Store",
                        uri=selected_app['url'],
                    )
                )
            )
            print(f"✅ Success: Link Card post for {selected_app['name']} on {acc['handle']}")
        except Exception as e:
            print(f"❌ Error on {acc['handle']}: {e}")

if __name__ == "__main__":
    main()
