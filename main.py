from openai import OpenAI
import base64
from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from services.gemini_service import ask_groq
from services.voice_service import speech_to_text

import requests
import os

load_dotenv()

app = FastAPI()

# --------------------------------
# GROQ VISION CLIENT
# --------------------------------
vision_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


@app.get("/")
async def home():
    return {"message": "Server is running"}


@app.post("/webhook")
async def whatsapp_webhook(request: Request):

    form = await request.form()

    response = MessagingResponse()

    # --------------------------------
    # CHECK MEDIA COUNT
    # --------------------------------
    num_media = form.get("NumMedia")

    if num_media:
        num_media = int(num_media)
    else:
        num_media = 0

    print("NUM MEDIA:", num_media)

    # --------------------------------
    # MEDIA HANDLING
    # --------------------------------
    if num_media > 0:

        try:

            media_url = form.get("MediaUrl0")
            media_type = form.get("MediaContentType0")

            print("MEDIA URL:", media_url)
            print("MEDIA TYPE:", media_type)

            # =========================================
            # VOICE MESSAGE
            # =========================================
            if media_type and "audio" in media_type:

                print("VOICE MESSAGE DETECTED")

                audio_response = requests.get(
                    media_url,
                    auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                )

                print("DOWNLOAD STATUS:", audio_response.status_code)

                audio_path = "farmer_audio.ogg"

                with open(audio_path, "wb") as f:
                    f.write(audio_response.content)

                print("AUDIO SAVED")

                # SPEECH TO TEXT
                farmer_text = speech_to_text(audio_path)

                print("TRANSCRIBED:", farmer_text)

                # AI RESPONSE
                ai_reply = ask_groq(
                    f"Reply in under 60 words only: {farmer_text}"
                )

                print("AI REPLY:", ai_reply)

                # SEND WHATSAPP REPLY
                msg = response.message()
                msg.body(ai_reply)

                return Response(
                    content=str(response),
                    media_type="application/xml"
                )

            # =========================================
            # IMAGE MESSAGE
            # =========================================
            elif media_type and "image" in media_type:

                print("IMAGE DETECTED")

                image_response = requests.get(
                    media_url,
                    auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                )

                print("IMAGE DOWNLOAD STATUS:", image_response.status_code)

                image_path = "farmer_image.jpg"

                with open(image_path, "wb") as f:
                    f.write(image_response.content)

                print("IMAGE SAVED")

                # CONVERT IMAGE TO BASE64
                with open(image_path, "rb") as img_file:
                    base64_image = base64.b64encode(
                        img_file.read()
                    ).decode("utf-8")

                print("IMAGE ENCODED")

                # ASK VISION MODEL
                completion = vision_client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """
                                    
You are an AI farming assistant.
Analyze this farming image.
Identify crop disease, pests,
soil issue, or plant condition.
Give solution in simple language
under 80 words.
"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]
                )

                ai_reply = completion.choices[0].message.content

                print("VISION AI REPLY:", ai_reply)

                # SEND WHATSAPP REPLY
                msg = response.message()
                msg.body(ai_reply)

                return Response(
                    content=str(response),
                    media_type="application/xml"
                )

        except Exception as e:

            print("MEDIA ERROR:", e)

            msg = response.message()
            msg.body("Could not process media.")

            return Response(
                content=str(response),
                media_type="application/xml"
            )

    # --------------------------------
    # NORMAL TEXT MESSAGE
    # --------------------------------
    incoming_msg = form.get("Body")

    print("TEXT MESSAGE:", incoming_msg)

    try:

        ai_reply = ask_groq(incoming_msg)

        print("AI REPLY:", ai_reply)

        # SEND WHATSAPP REPLY
        msg = response.message()
        msg.body(ai_reply)

    except Exception as e:

        print("TEXT ERROR:", e)

        msg = response.message()
        msg.body("AI error occurred.")

    return Response(
        content=str(response),
        media_type="application/xml"
    )