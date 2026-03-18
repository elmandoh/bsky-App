import os
import random
from groq import Groq
from atproto import Client, client_utils, models
from apps_data import APPS

# إعداد Groq بموديل حديث
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# الحسابات (يتم جلبها من Secrets)
ACCOUNTS = [
    {"handle": "globalpulse24.bsky.social", "password": os.environ.get("GLOBALPULSE24")},
    {"handle": "k3live.bsky.social", "password": os.environ.get("K3LIVE")},
    {"handle": "eurotrends24.bsky.social", "password": os.environ.get("EUROTRENDS24")}
]

HISTORY_FILE = "posted_history.txt"

def get_next_app():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            posted_names = f.read().splitlines()
    else:
        posted_names = []

    remaining_apps = [app for app in APPS if app['name'] not in posted_names]

    if not remaining_apps:
        remaining_apps = APPS
        # مسح محتوى الملف للبدء من جديد
        open(HISTORY_FILE, 'w').close()
        posted_names = []

    selected_app = random.choice(remaining_apps)

    with open(HISTORY_FILE, "a") as f:
        f.write(f"{selected_app['name']}\n")
    
    return selected_app

def generate_teaser(app):
    styles = ["viral and catchy", "problem-solving", "tech recommendation", "enthusiastic"]
    style = random.choice(styles)
    
    prompt = f"Write one {style} English sentence for US users about an app called '{app['name']}'. Context: {', '.join(app['keywords'])}. No hashtags, no quotes. Keep it natural."
    
    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=1.0 # لضمان عدم تكرار الجملة
    )
    return completion.choices[0].message.content.strip()

def main():
    selected_app = get_next_app()
    
    for acc in ACCOUNTS:
        try:
            client = Client()
            client.login(acc["handle"], acc["password"])
            
            # توليد نص مختلف لكل حساب في كل مرة
            post_text = generate_teaser(selected_app)
            
            tb = client_utils.TextBuilder()
            tb.text(post_text)

            # إرسال المنشور مع الـ Embed (Link Card) لإظهار معاينة احترافية
            client.send_post(
                text=tb,
                embed=models.AppBskyEmbedExternal.Main(
                    external=models.AppBskyEmbedExternal.External(
                        title=selected_app['name'],
                        description="Check it out on Google Play Store",
                        uri=selected_app['url'],
                    )
                )
            )
            print(f"✅ Posted {selected_app['name']} to {acc['handle']}")
        except Exception as e:
            print(f"❌ Error on {acc['handle']}: {e}")

if __name__ == "__main__":
    main()
