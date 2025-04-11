from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Пользователь сайта. Наследуется от стандартного пользователя Django.
    Добавлены:
    - аватар,
    - прогресс по урокам,
    - настройка уведомлений.
    """
    email = models.EmailField(_('Электронная почта'), unique=True)
    avatar = models.ImageField(_('Аватар'), upload_to='avatars/', null=True,
                               blank=True)
    notify_by_email = models.BooleanField(_('Получать уведомления на почту'),
                                          default=True)
    progress = models.JSONField(_('Прогресс по урокам'),
                                default=dict)  # Пример: {"1": 75, "2": 100}

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Lesson(models.Model):
    """
    Урок, содержащий видео, изображение и описание.
    К уроку могут быть привязаны задачи и тесты.
    """
    title = models.CharField(_('Название урока'), max_length=255)
    description = models.TextField(_('Описание'))
    video_url = models.URLField(_('Ссылка на видео'), blank=True, null=True)
    image = models.ImageField(_('Изображение'), upload_to='lessons/',
                              null=True, blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Achievement(models.Model):
    """
    Достижение, которое можно получить за выполнение задачи или прохождение теста.
    """
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'))
    icon = models.ImageField(_('Иконка достижения'), upload_to='achievements/')
    condition = models.CharField(_('Условие получения'),
                                 max_length=255)  # Пример: "finish_5_lessons"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"


class Task(models.Model):
    """
    Задача, которую нужно решить в рамках урока.
    Может быть связана с достижением.
    """
    lesson = models.ForeignKey(Lesson, related_name='tasks',
                               on_delete=models.CASCADE, verbose_name='Урок')
    question = models.TextField(_('Вопрос'))
    points = models.PositiveIntegerField(_('Баллы за выполнение'), default=10)
    achievement = models.ForeignKey(
        Achievement, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Достижение за выполнение'
    )

    def __str__(self):
        return f"{self.lesson.title} — {self.question[:30]}"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class UserAchievement(models.Model):
    """
    Связь между пользователем и полученным им достижением.
    """
    user = models.ForeignKey('kyberapp.CustomUser', on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE,
                                    verbose_name='Достижение')
    earned_at = models.DateTimeField(_('Дата получения'), auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')
        verbose_name = "Полученное достижение"
        verbose_name_plural = "Полученные достижения"

    def __str__(self):
        return f"{self.user.username} — {self.achievement.title}"


class Notification(models.Model):
    """
    Уведомление для пользователя. Может быть прочитано или непрочитано.
    """
    user = models.ForeignKey('kyberapp.CustomUser', on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    title = models.CharField(_('Заголовок'), max_length=255)
    message = models.TextField(_('Сообщение'))
    is_read = models.BooleanField(_('Прочитано'), default=False)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    def __str__(self):
        return f"Для: {self.user.username} — {self.title}"

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"


class News(models.Model):
    """
    Новость, отображаемая в разделе новостей. Может быть опубликована или скрыта.
    """
    title = models.CharField(_('Заголовок'), max_length=255)
    content = models.TextField(_('Содержание'))
    image = models.ImageField(_('Изображение'), upload_to='news/', null=True,
                              blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    is_published = models.BooleanField(_('Опубликована'), default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


class Test(models.Model):
    """
    Тест по уроку, содержащий вопросы.
    """
    lesson = models.ForeignKey(Lesson, related_name='tests',
                               on_delete=models.CASCADE, verbose_name='Урок')
    title = models.CharField(_('Название теста'), max_length=255)
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def total_points(self):
        """
        Сумма всех баллов за задачи урока, к которому привязан тест.
        """
        return sum(task.points for task in self.lesson.tasks.all())

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class Question(models.Model):
    """
    Вопрос, входящий в тест.
    """
    test = models.ForeignKey(Test, related_name='questions',
                             on_delete=models.CASCADE, verbose_name='Тест')
    question_text = models.TextField(_('Текст вопроса'))
    question_type = models.CharField(
        _('Тип вопроса'),
        max_length=50,
        choices=[
            ('one', 'Один правильный ответ'),
            ('multiple', 'Несколько правильных ответов')
        ]
    )

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(models.Model):
    """
    Вариант ответа на вопрос теста.
    """
    question = models.ForeignKey(Question, related_name='answers',
                                 on_delete=models.CASCADE,
                                 verbose_name='Вопрос')
    answer_text = models.CharField(_('Текст ответа'), max_length=255)
    is_correct = models.BooleanField(_('Правильный'), default=False)

    def __str__(self):
        return self.answer_text

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


class TestResult(models.Model):
    """
    Результат прохождения теста пользователем.
    """
    user = models.ForeignKey('kyberapp.CustomUser', on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    test = models.ForeignKey(Test, on_delete=models.CASCADE,
                             verbose_name='Тест')
    score = models.PositiveIntegerField(_('Баллы'))
    passed = models.BooleanField(_('Пройден'), default=False)
    achieved_achievement = models.ForeignKey(
        'kyberapp.Achievement',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Полученное достижение'
    )

    def __str__(self):
        return f"Результат {self.user.username} — {self.test.title}"

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"


class UserTest(models.Model):
    """
    Информация о том, когда пользователь прошёл тест и с каким результатом.
    """
    user = models.ForeignKey('kyberapp.CustomUser', on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    test = models.ForeignKey(Test, on_delete=models.CASCADE,
                             verbose_name='Тест')
    score = models.PositiveIntegerField(_('Набранные баллы'), default=0)
    completed_at = models.DateTimeField(_('Дата прохождения'),
                                        auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"

    class Meta:
        verbose_name = "Прохождение теста"
        verbose_name_plural = "Прохождения тестов"
