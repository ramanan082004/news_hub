from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from gtts import gTTS
from .models import TTSCache
import os, json
from django.conf import settings

@csrf_exempt
@require_POST
def generate_tts(request):
    try:
        data = json.loads(request.body)
        article_id = data.get('article_id')
        text = data.get('text', '').strip()
        lang = data.get('lang', 'ta')

        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        cached = TTSCache.objects.filter(article_id=article_id, language=lang).first()
        if cached and os.path.exists(cached.audio_file.path):
            return JsonResponse({
                'success': True,
                'audio_url': request.build_absolute_uri(cached.audio_file.url),
                'cached': True
            })

        tts = gTTS(text=text, lang=lang, slow=False)
        filename = f"tts_{article_id}_{lang}.mp3"
        filepath = os.path.join(settings.MEDIA_ROOT, 'tts_audio', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        tts.save(filepath)

        TTSCache.objects.update_or_create(
            article_id=article_id,
            language=lang,
            defaults={'audio_file': f'tts_audio/{filename}'}
        )

        audio_url = request.build_absolute_uri(settings.MEDIA_URL + f'tts_audio/{filename}')
        return JsonResponse({'success': True, 'audio_url': audio_url, 'cached': False})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)