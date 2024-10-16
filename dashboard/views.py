from django.contrib.sites import requests
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from django.contrib.auth.decorators import login_required
import requests



# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')


def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
        messages.success(request, f"{request.user.username}, Your notes have been saved.")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)


def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes


def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished

            )

            homeworks.save()
            messages.success(request, f"{request.user.username}, Your homeworks have been saved.")
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {
        'homeworks': homework,
        'homeworks_done': homework_done,
        'form': form,
    }
    return render(request, 'dashboard/homework.html', context)


def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')


def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished
            )
            todos.save()
            messages.success(request, f"{request.user.username}, Your todo have been saved.")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'form': form,
        'todos': todo,
        'todos_done': todos_done
    }
    return render(request, "dashboard/todo.html", context)


def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect("todo")


def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")


def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(len(answer.get('items', []))):
            volume_info = answer['items'][i]['volumeInfo']
            image_link = volume_info.get('imageLinks')

            result_dict = {
                'title': volume_info.get('title'),
                'subtitle': volume_info.get('subtitle'),
                'description': volume_info.get('description'),
                'count': volume_info.get('pageCount'),
                'categories': volume_info.get('categories'),
                'rating': volume_info.get('averageRating'),
                'thumbnail': image_link.get('thumbnail') if image_link else None,
                'preview': volume_info.get('previewLink')
            }
            result_list.append(result_dict)
            context = {
                'form': form,
                'results': result_list
            }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, 'dashboard/books.html', context)


import requests
from django.shortcuts import render
from .forms import DashboardForm

import requests
from django.shortcuts import render
from .forms import DashboardForm

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '').strip()  # Strip whitespace for clean input
        api_key = "b27a1c5b-0f42-4081-ba58-e0b96c33db4f"
        url = f"https://dictionaryapi.com/api/v3/references/thesaurus/json/{text}?key={api_key}"

        if not text:
            context = {
                'form': form,
                'input': '',
                'error': 'Please enter a word to search.'
            }
            return render(request, "dashboard/dictionary.html", context)

        try:
            r = requests.get(url)
            print("Request URL:", url)  # Log the request URL
            print("Status Code:", r.status_code)  # Log the status code
            r.raise_for_status()  # Raise an error for bad status codes
            answer = r.json()
            print("API Response:", answer)  # Log the full API response

            if isinstance(answer, list) and answer:
                word_data = answer[0]

                if isinstance(word_data, dict):
                    definition = word_data.get('shortdef', ['No definition available'])[0]
                    synonyms = word_data.get('meta', {}).get('syns', [[]])[0]

                    context = {
                        'form': form,
                        'input': text,
                        'definition': definition,
                        'synonyms': synonyms or ['No synonyms available'],
                    }
                else:
                    context = {'form': form, 'input': 'No results found'}
            else:
                context = {'form': form, 'input': 'No results found'}

        except requests.exceptions.HTTPError as http_err:
            context = {
                'form': form,
                'input': '',
                'error': f"HTTP error occurred: {http_err} (Status Code: {http_err.response.status_code})"
            }
        except requests.exceptions.RequestException as req_err:
            context = {
                'form': form,
                'input': '',
                'error': f"Error fetching data from the API: {str(req_err)}"
            }
        except Exception as e:
            context = {
                'form': form,
                'input': '',
                'error': f"An unexpected error occurred: {str(e)}"
            }

        return render(request, "dashboard/dictionary.html", context)

    else:
        form = DashboardForm()
        return render(request, "dashboard/dictionary.html", {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            # Optionally redirect after successful registration
            return redirect('login')  # Adjust 'login' to your actual login URL name
    else:
        form = UserRegistrationForm()

    # Ensure context is defined for both POST and GET methods
    context = {
        'form': form
    }
    return render(request, "dashboard/register.html", context)


def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    homeworks_done = len(homeworks) == 0
    todos_done = len(todos) == 0

    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homeworks_done': homeworks_done,
        'todos_done': todos_done
    }
    return render(request, "dashboard/profile.html", context)
