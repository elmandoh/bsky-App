import os
from groq import Groq
from atproto import Client

# 1. إعداد الاتصال بـ Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. إعداد الاتصال بـ Bluesky
bsky_client = Client()
bsky_client.login(os.environ.get("BSKY_HANDLE"), os.environ.get("BSKY_PASSWORD"))

def generate_marketing_post():
    # هنا بنطلب من Groq يكتب بوست تسويقي "مش مكرر"
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a creative social media marketer. Write a short, engaging post in Arabic for a mobile app on Google Play. Use emojis and make it sound natural, not like an ad. Mention the benefits, not just features."
            },
            {
                "role": "user",
                "content": "Write a post for my productivity app. Link: [رابط تطبيقك هنا]"
            }
        ],
        model="llama3-8b-8192", # موديل سريع وذكي جداً
    )
    return chat_completion.choices[0].message.content

def main():
    try:
        # توليد المحتوى
        post_text = generate_marketing_post()
        
        # النشر على Bluesky
        bsky_client.send_post(text=post_text)
        print("Done! Post published successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
