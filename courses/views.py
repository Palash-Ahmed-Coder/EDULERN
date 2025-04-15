from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson
from .forms import CourseForm, LessonForm
from django.contrib import messages
from . forms import CourseEnrollmentForm
from . models import Student
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from . forms import UserUpdateForm

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializer

from .models import Student

# Course List
@login_required
#def course_list(request):
 #   courses = Course.objects.all()
  #  return render(request, 'courses/course_list.html', {'courses': courses})

# Course Detail
#def course_detail(request, course_id):
 #   course = get_object_or_404(Course, id=course_id)
  #  lessons = course.lessons.all()
   # return render(request, 'courses/course_detail.html', {'course': course, 'lessons': lessons})

# Create Course
#def course_create(request):
 #   if request.method == "POST":
  #      form = CourseForm(request.POST, request.FILES)
   #     if form.is_valid():
    #        form.save()
     #       messages.success(request, "Course created successfully!")
      #      return redirect('course_list')
    #else:
     #   form = CourseForm()
    #return render(request, 'courses/course_form.html', {'form': form})

# Update Course
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form})

# Delete Course
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

# Create Lesson
def lesson_create(request):
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('course_list')
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form})

# Update Lesson
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('course_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form})

# Delete Lesson
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

def enroll_student(request):
    if request.method == 'POST':
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            student_name = form.cleaned_data['student_name']
            student_email = form.cleaned_data['student_email']
            course = form.cleaned_data['course']

            # Get or create the student
            student, created = Student.objects.get_or_create(email=student_email)

            if created:
                student.name = student_name
                student.save()

            # Check if the student is already enrolled in the course
            if student.enrolled_courses.filter(id=course.id).exists():
                return render(request, 'courses/enrollment_failed.html', {'student': student, 'course': course})

            # Enroll the student in the course
            student.enrolled_courses.add(course)

            return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
    else:
        form = CourseEnrollmentForm()

    return render(request, 'courses/enroll_student.html', {'form': form})

def view_students(request, course_id):
    course = Course.objects.get(id=course_id)
    students = course.students.all()  # Adjust this based on your model relationships
    return render(request, 'courses/view_students.html', {'students': students})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('/')
    else:  # This should be properly indented
        form = UserCreationForm()
    
    return render(request, 'courses/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'courses/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'courses/profile.html', {'form': form})

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

class CourseCreateView(CreateView):
    model = Course
    fields = ['title', 'description', 'duration', 'thumbnail']
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list') 


class CourseListAPI(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class CourseDetailAPI(APIView):
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
class EnrollStudentAPI(APIView):
    def post(self, request):
        student_email = request.data.get('email')
        course_id = request.data.get('course_id')

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        student, created = Student.objects.get_or_create(email=student_email)
        student.enrolled_courses.add(course)

        return Response({'message': f'{student.email} has been enrolled in {course.title}'})    