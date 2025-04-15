from django.db import models

# Create your models here.
class Course(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    duration=models.IntegerField(help_text='Duration in hours')
    thumbnail=models.ImageField(upload_to='course_thumbnail/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + '(' + str(self.duration) + ')'

    
    
class Lesson(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='lessons')
    video_url = models.URLField(null=True, blank=True)
    completion_status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class Student(models.Model):
    name=models.CharField(max_length=200)
    email=models.EmailField(unique=True)
    enrolled_courses=models.ManyToManyField(Course,related_name='students')  
    completed_lessons = models.ManyToManyField('Lesson', related_name='completed_by', blank=True)

    def __str__(self):
        return self.name    
