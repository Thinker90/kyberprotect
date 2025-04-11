from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator

from .forms import CustomUserCreationForm

from .models import (Lesson, Achievement, UserAchievement, Task,
                     News, Test, Question, Answer, TestResult)


def home(request):
    news_list = News.objects.all()  # Получаем все новости
    paginator = Paginator(news_list, 5)  # Пагинируем, 5 новостей на странице
    page_number = request.GET.get('page')  # Получаем номер страницы из GET-параметра
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы
    return render(request, "kyberapp/home.html", {"page_obj": page_obj})


def lessons(request):
    lessons_list = Lesson.objects.all()  # Получаем все уроки
    paginator = Paginator(lessons_list, 10)  # 10 уроков на страницу
    page_number = request.GET.get('page')  # Номер страницы
    page_obj = paginator.get_page(page_number)  # Получаем объект страницы
    return render(request, "kyberapp/lessons.html", {'page_obj': page_obj})


def lesson_detail(request, lesson_id):
    """
    Отображает страницу подробностей урока.

    Параметры:
    request: объект HttpRequest, содержащий информацию о запросе.
    lesson_id: ID урока, для которого требуется показать подробности.

    Возвращает:
    Отображение страницы с информацией о выбранном уроке и ссылке на тест (если он есть).
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)  # Получаем урок по ID, если не найдено, будет ошибка 404.

    # Проверка на наличие теста, связанного с лекцией.
    test = lesson.tests.first()  # Предполагаем, что у лекции может быть только один тест (если нужно, можно изменить логику).

    # Проверяем, авторизован ли пользователь, чтобы передать ему ссылку на тест.
    if test:
        if request.user.is_authenticated:  # Если пользователь авторизован
            test_link = f"/test/{test.id}/"  # Ссылка на прохождение теста
        else:
            test_link = f"/login/?next=/test/{test.id}/"  # Ссылка на тест с редиректом на страницу входа/регистрации
    else:
        test_link = None  # Если нет теста, то и ссылки нет.

    return render(request, "kyberapp/lesson_detail.html", {'lesson': lesson, 'test_link': test_link})
def achievements(request):
    """
    Отображает список достижений пользователя.

    Параметры:
    request: объект HttpRequest.

    Возвращает:
    Отображение страницы с достижениями пользователя.
    """
    user_achievements = UserAchievement.objects.filter(user=request.user)  # Получаем все достижения текущего пользователя
    return render(request, "kyberapp/achievements.html", {'user_achievements': user_achievements})
@login_required
def profile(request):
    """
    Отображает профиль пользователя, включая информацию о достигнутых достижениях и прогрессе.

    Параметры:
    request: объект HttpRequest.

    Возвращает:
    Отображение страницы профиля с достижениями и прогрессом пользователя.
    """
    user = request.user  # Получаем текущего пользователя
    user_achievements = UserAchievement.objects.filter(user=user)  # Все достижения пользователя
    earned_achievement_ids = user_achievements.values_list('achievement_id', flat=True)  # IDs достигнутых достижений

    all_tasks = Task.objects.select_related('lesson', 'achievement')  # Все задачи, связанные с уроками и достижениями
    tasks_with_status = []  # Список для хранения задач с их статусом (выполнил/не выполнил)

    # Для каждой задачи проверяем, выполнена ли она
    for task in all_tasks:
        is_completed = task.achievement_id in earned_achievement_ids if task.achievement else False
        tasks_with_status.append((task, is_completed))

    total_achievements = Achievement.objects.count()  # Всего достижений
    earned_achievements = user_achievements.count()  # Достигнутые достижения
    progress_percent = int((earned_achievements / total_achievements) * 100) if total_achievements else 0  # Процент выполненных достижений

    return render(
        request,
        "kyberapp/profile.html",
        {
            'user': user,
            'user_achievements': user_achievements,
            'progress_percent': progress_percent,
            'tasks_with_status': tasks_with_status,
        }
    )
def login_view(request):
    """
    Обрабатывает процесс входа пользователя.

    Параметры:
    request: объект HttpRequest.

    Возвращает:
    Отображение страницы входа с формой. Если вход успешен, редиректит на главную страницу.
    """
    if request.method == 'POST':  # Если форма отправлена
        form = AuthenticationForm(data=request.POST)  # Создаем форму с данными из POST-запроса
        if form.is_valid():  # Если форма валидна
            username = form.cleaned_data.get('username')  # Получаем имя пользователя
            password = form.cleaned_data.get('password')  # Получаем пароль
            user = authenticate(username=username, password=password)  # Пытаемся аутентифицировать пользователя
            if user is not None:  # Если пользователь найден
                login(request, user)  # Выполняем вход
                return redirect('home')  # Редиректим на главную страницу
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль.')  # Добавляем ошибку в форму
    else:
        form = AuthenticationForm()  # Создаем пустую форму для входа
    return render(request, 'kyberapp/login.html', {'form': form})


def register_view(request):
    """
    Обрабатывает процесс регистрации нового пользователя.

    Параметры:
    request: объект HttpRequest.

    Возвращает:
    Отображение страницы регистрации с формой. Если регистрация успешна, сразу выполняется вход.
    """
    if request.method == 'POST':  # Если форма отправлена
        form = CustomUserCreationForm(request.POST)  # Создаем форму с данными из POST-запроса
        if form.is_valid():  # Если форма валидна
            form.save()  # Сохраняем нового пользователя
            username = form.cleaned_data.get('username')  # Получаем имя пользователя
            password = form.cleaned_data.get('password1')  # Получаем пароль
            user = authenticate(username=username, password=password)  # Пытаемся аутентифицировать нового пользователя
            login(request, user)  # Выполняем вход
            return redirect('home')  # Редиректим на главную страницу
    else:
        form = CustomUserCreationForm()  # Создаем пустую форму для регистрации
    return render(request, 'kyberapp/register.html', {'form': form})
def logout_view(request):
    """
    Обрабатывает процесс выхода пользователя.

    Параметры:
    request: объект HttpRequest.

    Возвращает:
    Редирект на главную страницу после выхода.
    """
    logout(request)  # Выход пользователя
    return redirect('home')  # Редиректим на главную страницу


def admin_faq(request):
    """
    Отображает страницу с часто задаваемыми вопросами для администраторов.

    Параметры:
    request: объект HttpRequest.

    Возвращает:
    Отображение страницы FAQ для администраторов.
    """
    return render(request, "kyberapp/admin_faq.html")

@login_required
def take_test(request, test_id):
    """
    Страница для прохождения теста. Пользователь выбирает ответы на вопросы теста,
    и его результат сохраняется в базе данных.

    Параметры:
    request: объект HttpRequest, содержащий информацию о запросе.
    test_id: ID теста, который пользователь собирается пройти.

    Возвращает:
    Отображение страницы с тестом для прохождения и страницу с результатами теста после его завершения.
    """
    test = get_object_or_404(Test, id=test_id)  # Получаем тест по ID, если тест не найден, возвращаем 404 ошибку.
    questions = test.questions.all()  # Получаем все вопросы для данного теста.
    tasks = Task.objects.filter(lesson=test.lesson)  # Получаем задачи для текущей лекции, связанной с тестом.

    score = 0  # Изначальный балл теста (0 баллов).

    if request.method == 'POST':  # Если форма была отправлена
        # Обрабатываем ответы на каждый вопрос.
        for question in questions:
            selected_answers = request.POST.getlist(f'question_{question.id}')  # Получаем выбранные ответы пользователя.
            correct_answers_for_question = question.answers.filter(is_correct=True)  # Получаем правильные ответы для текущего вопроса.

            if question.question_type == 'one':  # Если вопрос одиночный (один правильный ответ)
                if len(selected_answers) == 1 and selected_answers[0] == str(
                        correct_answers_for_question.first().id):  # Проверяем правильность ответа
                    score += 1  # Увеличиваем балл, если ответ правильный.
            elif question.question_type == 'multiple':  # Если вопрос с несколькими правильными ответами
                correct_answer_ids = [str(answer.id) for answer in correct_answers_for_question]  # Получаем правильные ответы
                if sorted(selected_answers) == sorted(correct_answer_ids):  # Проверяем, совпадает ли выбранный ответ с правильными
                    score += 1  # Увеличиваем балл за правильные ответы.

        # Добавляем баллы за задачи, связанные с тестом.
        for task in tasks:
            if task.points in request.POST.getlist(f'task_{task.id}'):  # Проверяем, выбраны ли баллы задачи
                score += task.points  # Добавляем баллы задачи, если они выбраны.

        # Сохраняем результат теста в базе данных.
        test_result = TestResult.objects.create(user=request.user, test=test, score=score)
        test_result.save()  # Сохраняем результат теста.

        # Присваиваем достижение, если набрано достаточно баллов.
        if score >= test.total_points:  # Если пользователь набрал все возможные баллы в тесте
            # Присваиваем достижение для всех задач с достижением.
            for task in tasks:
                if task.achievement:  # Если у задачи есть достижение
                    achievement = task.achievement
                    test_result.achieved_achievement = achievement  # Присваиваем достижение теста
                    test_result.passed = True  # Отмечаем, что тест пройден успешно
                    test_result.save()

                    # Присваиваем достижение пользователю.
                    user_achievement, created = UserAchievement.objects.get_or_create(
                        user=request.user, achievement=achievement)
                    if created:
                        print(f"Достижение {achievement.title} присвоено пользователю {request.user.username}")
                    else:
                        print(f"Достижение {achievement.title} уже есть у пользователя {request.user.username}")

        # Отправляем результат теста на страницу.
        return render(request, 'kyberapp/test_result.html', {'test_result': test_result, 'score': score})

    # Если форма не была отправлена, показываем страницу с тестом.
    return render(request, 'kyberapp/take_test.html', {'test': test, 'questions': questions})
