# storage.py
from django.contrib.messages.storage.fallback import FallbackStorage


class LimitedMessageStorage(FallbackStorage):
    """
    Storage для сообщений с ограничением до 3
    """
    MAX_MESSAGES = 3

    def add(self, level, message, extra_tags=''):
        super().add(level, message, extra_tags)
        
        # Ограничиваем количество сообщений в очереди
        if len(self._queued_messages) > self.MAX_MESSAGES:
            self._queued_messages = self._queued_messages[-self.MAX_MESSAGES:]

    def _get(self, *args, **kwargs):
        messages, all_retrieved = super()._get(*args, **kwargs)
        
        # Ограничиваем при получении
        if len(messages) > self.MAX_MESSAGES:
            messages = messages[-self.MAX_MESSAGES:]
        
        return messages, all_retrieved