from django.db import models
class TTSCache(models.Model):
    article_id = models.IntegerField(unique=True)
    language = models.CharField(max_length=10, default='ta')
    audio_file = models.FileField(upload_to='tts_audio/')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"TTS - Article {self.article_id} ({self.language})"
