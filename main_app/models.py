from django.db import models
from django.urls import reverse
from datetime import date

# Import the User
from django.contrib.auth.models import User

# Define this above the models

MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)

# Create your models here.

class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('toys_detail', kwargs={'pk': self.id})

class Dog(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    toys = models.ManyToManyField(Toy)
    # Add the foreign key linking to a user instance
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'dog_id': self.id})
    def fed_for_today(self):
        return self.feeding_set.filter(date=date.today()).count() >= len(MEALS)

class Feeding(models.Model):
    date = models.DateField()
    meal = models.CharField(
    max_length=1,
	 choices=MEALS,
	 default=MEALS[0][0]
  )
  # Create a Dog_id FK
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_meal_display()} on {self.date}"
    # change the default sort
    class Meta:
        ordering = ['-date']

class Photo(models.Model):
    url = models.CharField(max_length=200)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for dog_id: {self.dog_id} @{self.url}"
