from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.views import generic
import requests


# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')


def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, **form.cleaned_data)
            notes.save()
            messages.success(request, f"{request.user.username}, your notes have been saved.")
            return redirect("notes")  # Redirect after successful save
    else:
        form = NotesForm()

    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)


def delete_note(request, pk=None):
    try:
        note = Notes.objects.get(id=pk, user=request.user)
        note.delete()
        messages.success(request, "Note deleted successfully.")
    except Notes.DoesNotExist:
        messages.error(request, "Note does not exist.")
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes


def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            homework_instance = Homework(
                user=request.user,
                **form.cleaned_data
            )
            homework_instance.save()
            messages.success(request, f"{request.user.username}, your homework has been saved.")
            return redirect("homework")  # Redirect after successful save
    else:
        form = HomeworkForm()

    homework_list = Homework.objects.filter(user=request.user)
    context = {
        'homeworks': homework_list,
        'homeworks_done': not homework_list.exists(),
        'form': form,
    }
    return render(request, 'dashboard/homework.html', context)


def update_homework(request, pk=None):
    try:
        homework = Homework.objects.get(id=pk)
        homework.is_finished = not homework.is_finished  # Toggle the finished status
        homework.save()
        messages.success(request, "Homework status updated.")
    except Homework.DoesNotExist:
        messages.error(request, "Homework does not exist.")
    return redirect('homework')


def delete_homework(request, pk=None):
    try:
        homework = Homework.objects.get(id=pk)
        homework.delete()
        messages.success(request, "Homework deleted successfully.")
    except Homework.DoesNotExist:
        messages.error(request, "Homework does not exist.")
    return redirect("homework")


def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo_instance = Todo(
                user=request.user,
                **form.cleaned_data
            )
            todo_instance.save()
            messages.success(request, f"{request.user.username}, your todo has been saved.")
            return redirect("todo")  # Redirect after successful save
    else:
        form = TodoForm()

    todo_list = Todo.objects.filter(user=request.user)
    context = {
        'form': form,
        'todos': todo_list,
        'todos_done': not todo_list.exists()
    }
    return render(request, "dashboard/todo.html", context)


def update_todo(request, pk=None):
    try:
        todo = Todo.objects.get(id=pk)
        todo.is_finished = not todo.is_finished  # Toggle the finished status
        todo.save()
        messages.success(request, "Todo status updated.")
    except Todo.DoesNotExist:
        messages.error(request, "Todo does not exist.")
    return redirect("todo")


def delete_todo(request, pk=None):
    try:
        todo = Todo.objects.get(id=pk)
        todo.delete()
        messages.success(request, "Todo deleted successfully.")
    except Todo.DoesNotExist:
        messages.error(request, "Todo does not exist.")
    return redirect("todo")


import time
import requests
from django.shortcuts import render
from .forms import DashboardForm


def books(request):
    context = {}
    form = DashboardForm(request.POST or None)
    context['form'] = form  # Add form to context early

    if request.method == "POST" and form.is_valid():
        text = form.cleaned_data['text']
        url = f"https://www.googleapis.com/books/v1/volumes?q={text}"

        try:
            # Introduce a small delay to avoid triggering rate limits too quickly
            time.sleep(1)  # 1 second delay
            r = requests.get(url)
            r.raise_for_status()  # Raises an exception for non-200 responses
            answer = r.json()

            # Prepare the result list from the API response
            result_list = [
                {
                    'title': item['volumeInfo'].get('title', 'No Title'),
                    'subtitle': item['volumeInfo'].get('subtitle', 'No Subtitle'),
                    'description': item['volumeInfo'].get('description', 'No Description'),
                    'count': item['volumeInfo'].get('pageCount', 'N/A'),
                    'categories': item['volumeInfo'].get('categories', ['N/A']),
                    'rating': item['volumeInfo'].get('averageRating', 'N/A'),
                    'thumbnail': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
                    'preview': item['volumeInfo'].get('previewLink', '#')
                }
                for item in answer.get('items', [])
            ]
            context['results'] = result_list  # Add results to the context

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Google Books API: {e}")
            context['results'] = []  # Empty results in case of error

    return render(request, 'dashboard/books.html', context)


def dictionary(request):
    context = {}
    form = DashboardForm(request.POST or None)

    if request.method == "POST":
        text = request.POST.get('text', '').strip()  # Get the input text and strip whitespace

        if not text:
            context['error'] = 'Please enter a word to search.'
        else:
            api_key = "b27a1c5b-0f42-4081-ba58-e0b96c33db4f"
            url = f"https://dictionaryapi.com/api/v3/references/thesaurus/json/{text}?key={api_key}"

            print(f"Requesting URL: {url}")  # Debug: Print the URL being requested

            try:
                r = requests.get(url)
                r.raise_for_status()  # Raise an error for bad status codes
                answer = r.json()

                # Debugging: Print the raw answer from the API
                print(f"API Response: {answer}")

                if isinstance(answer, list) and answer:
                    word_data = answer[0]
                    if isinstance(word_data, dict):
                        definition = word_data.get('shortdef', ['No definition available'])[0]
                        synonyms = word_data.get('meta', {}).get('syns', [[]])[0]
                        context.update({
                            'definition': definition,
                            'synonyms': synonyms if synonyms else ['No synonyms available'],
                            'input': text,  # Store the input word for display
                        })
                    else:
                        context['error'] = 'No valid data returned from API.'
                else:
                    context['error'] = 'No results found.'

            except requests.exceptions.HTTPError as http_err:
                context['error'] = f"HTTP error occurred: {http_err}"
            except requests.exceptions.RequestException as req_err:
                context['error'] = f"Error fetching data from the API: {str(req_err)}"
            except Exception as e:
                context['error'] = f"An unexpected error occurred: {str(e)}"

    context['form'] = form
    return render(request, "dashboard/dictionary.html", context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! You are now able to log in.')
            return redirect('login')  # Adjust 'login' to your actual login URL name
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, "dashboard/register.html", context)


def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homeworks_done': not homeworks.exists(),
        'todos_done': not todos.exists()
    }
    return render(request, "dashboard/profile.html", context)
