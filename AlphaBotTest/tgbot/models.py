from django.db import models


class AnswerFromChat(models.Model):
    chat_id = models.CharField('Chat ID пользователя', max_length=70)
    tg_login = models.CharField('Telegram логин пользователя', max_length=70)
    name = models.CharField('Имя пользователь (ответ на первый вопрос)', max_length=150)
    phone = models.CharField('Номер телефона', max_length=50)
    answers = models.CharField('Ответы через запятую', max_length=150)

    def __str__(self):
        return str(self.name) + str(self.phone) + str(self.answers)


class ChatInUse(models.Model):
    chat_id = models.IntegerField()
    stage = models.CharField(max_length=50)
    presaved_name = models.CharField('Имя пользователя (ответ на первый вопрос)', max_length=150, blank=True)
    presaved_phone = models.CharField('Номер телефона', max_length=50, blank=True)


class MessageFromBotInChat(models.Model):
    message_id = models.IntegerField()
    from_chat = models.ForeignKey(ChatInUse, on_delete=models.CASCADE)
