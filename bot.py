import os
import random
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

HISTORY_FILE = "posted_history.txt"

def get_next_app():
    # قراءة التاريخ
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            posted_names = f.read().splitlines()
    else:
        posted_names = []

    # تصفية التطبيقات اللي لسه منشرتش
    remaining_apps = [app for app in APPS if app['name'] not in posted_names]

    # لو خلصناهم كلهم، صفر الملف وابدأ من جديد
    if not remaining_apps:
        remaining_apps = APPS
        posted_names = []

    selected_app = random.choice(remaining_apps)

    # تحديث التاريخ
    posted_names.append(selected_app['name'])
    with open(HISTORY_FILE, "w") as f:
        f.write("\n".join(posted_names))
    
    return selected_app

def generate_english_teaser(app):
    prompt = f"Write one viral, high-energy English sentence for the US audience about an app called '{app['name']}'. Context: {', '.join(app['keywords'])}. No hashtags, no links."
    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    return completion.choices[0].message.content.strip().replace('"', '')

def main():
    selected_app = get_next_app()
    post_text = generate_english_teaser(selected_app)
    
    for acc in ACCOUNTS:
        try:
            client = Client()
            client.login(acc["handle"], acc["password"])
            
            # بناء النص بالهاشتاجات بطريقة Bluesky الأصلية (بدون ما تظهر كنص ميت)
            tb = client_utils.TextBuilder()
            tb.text(f"{post_text}\n\n")
            tb.tag("#TechTips", "TechTips")
            tb.text(" ")
            tb.tag("#Android", "Android")

            # إرسال المنشور مع "بطاقة معاينة" (Embed External)
            # دي اللي بتعمل شكل الصندوق وبتشيل رسالة التحذير
            client.send_post(
                text=tb,
                embed=models.AppBskyEmbedExternal.Main(
                    external=models.AppBskyEmbedExternal.External(
                        title=selected_app['name'],
                        description="Check out this app on Google Play!",
                        uri=selected_app['url'],
                    )
                )
            )
            print(f"✅ Success: Posted {selected_app['name']} to {acc['handle']}")
        except Exception as e:
            print(f"❌ Error on {acc['handle']}: {e}")

if __name__ == "__main__":
    main()
