from django.shortcuts import render, redirect
# Import Dog model
from .models import Dog, Toy, Photo
# Add the following import
# Add UdpateView & DeleteView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
# Import the FeedingForm
from .forms import FeedingForm

import uuid
import botocore
import boto3
import os

# Add the following import
# Remove since we're not using it anymore.
# from django.http import HttpResponse

class DogCreate(CreateView):
  model = Dog
  fields = ['name', 'breed', 'description', 'age']
# same as   fields = ['name', 'breed', 'description', 'age']
# could use this as a redirect, but not scalable
# success_url = '/dogs/'
# This inherited method is called when a
# valid cat form is being submitted
  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class DogUpdate(UpdateView):
  model = Dog
  # Let's disallow the renaming of a dog by excluding the name field!
  fields = ['breed', 'description', 'age']

class DogDelete(DeleteView):
  model = Dog
  success_url = '/dogs/'

# Define the home view
def home(request):
    return render(request, 'home.html')

# about route
def about(request):
    return render(request, 'about.html')

# Add new view
# Remove for day two
# def dogs_index(request):
#     return render(request, 'dogs/index.html', { 'dogs': dogs })

# day two add
def dogs_index(request):
  dogs = Dog.objects.all()
  return render(request, 'dogs/index.html', { 'dogs': dogs })

# Add the Dog class & list and view function below the imports
# Remove as of day two models
# class Dog:  # Note that parens are optional if not inheriting from another class
#   def __init__(self, name, breed, description, age):
#     self.name = name
#     self.breed = breed
#     self.description = description
#     self.age = age

# dogs = [
#     Dog('Lolo', 'tabby', 'foul little demon', 3),
#     Dog('Sachi', 'tortoise shell', 'diluted tortoise shell', 0),
#     Dog('Raven', 'black tripod', '3 legged Dog', 4)
# ]
# day two models details

# update this view function
def dogs_detail(request, dog_id):
  dog = Dog.objects.get(id=dog_id)
  # Get the toys the dog doesn't have
  toys_dog_doesnt_have = Toy.objects.exclude(id__in = dog.toys.all().values_list('id'))
  feeding_form = FeedingForm()
  return render(request, 'dogs/detail.html', {
    'dog': dog, 'feeding_form': feeding_form,
    # Add the toys to be displayed
    'toys': toys_dog_doesnt_have
  })

# add this new function below dogs_detail
def add_feeding(request, dog_id):
  # create a ModelForm instance using the data in request.POST
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the dog_id assigned
    new_feeding = form.save(commit=False)
    new_feeding.dog_id = dog_id
    new_feeding.save()
  return redirect('detail', dog_id=dog_id)

def assoc_toy(request, dog_id, toy_id):
  # Note that you can pass a toy's id instead of the whole toy object
  Dog.objects.get(id=dog_id).toys.add(toy_id)
  return redirect('detail', dog_id=dog_id)

def unassoc_toy(request, dog_id, toy_id):
  Dog.objects.get(id=dog_id).toys.remove(toy_id)
  return redirect('detail', dog_id=dog_id)
class ToyList(ListView):
  model = Toy
class ToyDetail(DetailView):
  model = Toy
class ToyCreate(CreateView):
  model = Toy
  fields = '__all__'
class ToyUpdate(UpdateView):
  model = Toy
  fields = ['name', 'color']
class ToyDelete(DeleteView):
  model = Toy
  success_url = '/toys/'

def add_photo(request, dog_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # build the full url string
            url = f"{os.environ['S3_BASE_URL']}/{key}"
            print (url)
            # we can assign to Dog_id or Dog (if you have a Dog object)
            Photo.objects.create(url=url, dog_id=dog_id)
        except botocore.exceptions.ClientError as error:
            print('An error occurred uploading file to S3')
            # Put your error handling logic here
            raise error
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError('The parameters you provided are incorrect: {}'.format(error))
    return redirect('detail', dog_id=dog_id)
