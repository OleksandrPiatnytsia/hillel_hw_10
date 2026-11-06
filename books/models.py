from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    categories = models.ManyToManyField(
        Category,
        through="BookCategory",
        related_name="books",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} — {self.author}"


class BookCategory(models.Model):
    """Link between Book and Category.

    An explicit through model lets us protect categories from deletion
    while they still contain books (plain M2M has no on_delete).
    """

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "book category"
        verbose_name_plural = "book categories"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "category"],
                name="unique_book_category",
            ),
        ]

    def __str__(self):
        return f"{self.book.title} → {self.category.name}"
