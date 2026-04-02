from django.shortcuts import render, redirect
from .models import AIRecommendation, AIHistory
from catalog.models import Car
import google.generativeai as genai
from django.views import View
from django.contrib import messages
import concurrent.futures
import requests
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import os
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GENAI = os.getenv("GENAI")
genai.configure(api_key=GENAI)
groq_client = Groq(api_key=GROQ_API_KEY)




def ask_gemini(prompt):
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return ("gemini", response.text)
        except:
            continue
    return None


def ask_groq(prompt):
    try:
        completion = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq error: {e}")
        return None



def ask_openrouter(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                     "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            },
            timeout=30
        )
        if response.status_code == 200:
            return ("openrouter", response.json()['choices'][0]['message']['content'])
    except:
        pass
    return None


def ask_ai(text, mode):
    cars = Car.objects.filter(is_deleted=False)
    data = [
        f'title:{c.title}, brand:{c.brand.name}, price:{c.price}' for c in cars]

    prompts = {
        'recommendate': f'Коротко, 3-4 предложения. Порекомендуй машину из: {data}. Вопрос: {text}. Ссылка: <a href="/catalog/" class=" text-blue-600 dark:text-red-600 ">каталог</a> или же <a href="/catalog/[id]" class=" text-blue-600 dark:text-red-600 " >Смотреть товар</a> [id]- id ставишь сам',
        'search': f'Коротко, 3-4 предложения. Найди машину из: {data}. Запрос: {text}. Ссылка: <a href="/catalog/" class=" text-blue-600 dark:text-red-600 ">смотреть</a> или же <a href="/catalog/[id]" class=" text-blue-600 dark:text-red-600 " >Смотреть товар</a> [id] - id ставишь сам',
        'ask': f'Коротко, Очень коротко: {text}',
    }

    full_prompt = f'Ты ассистент LUXE AUTO. Не отвечай на темы не касающегося насчёт авто или если она не совпадает с требованием {prompts.get(mode, text)}'

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(ask_gemini, full_prompt),
            executor.submit(ask_groq, full_prompt),
            executor.submit(ask_openrouter, full_prompt)
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                source, answer = result
                print(f"Ответ получен от: {source}")
                return answer

    return "Сервис временно недоступен. Попробуйте позже."


class AddAiQuestion(View):
    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Авторизуйтесь')
            return redirect('login')

        user_text = request.POST.get('user_text')
        mode = request.POST.get('mode', 'ask')

        if user_text:
            ai_response = ask_ai(user_text, mode)

            history, _ = AIHistory.objects.get_or_create(user_id=user_id)
            AIRecommendation.objects.create(
                user_text=user_text,
                mode=mode,
                ai_response=ai_response,
                chat_id=history
            )
            # messages.success(request, 'Отправлено')

        return redirect(request.META.get('HTTP_REFERER', 'home'))


class DeleteChatView(View):
    def post(self, request, message_id):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        try:
            msg = AIRecommendation.objects.get(
                id=message_id, chat_id__user_id=user_id)
            msg.delete()
            messages.success(request, 'Удалено')
        except:
            messages.error(request, 'Ошибка')

        return redirect(request.META.get('HTTP_REFERER', 'home'))
