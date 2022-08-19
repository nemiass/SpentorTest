from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models

from a01_note.models import DEFAULT_PERMISSION, PERMISSION_TYPE, Page


####---- Deck ------------------------------
class Deck(models.Model):
    DEFAULT_DECK = "0"
    DECK_TYPE = [
        (DEFAULT_DECK, "Basic"),
        ("1", "Customized"),
        ("2", "Customized from community"),
    ]

    page = models.OneToOneField(
        Page, on_delete=models.CASCADE, blank=True, null=True
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    deck_parts = models.ManyToManyField("self", blank=True)
    deck_name = models.CharField(max_length=52, null=True)

    description = models.CharField(max_length=150, blank=True, null=True)
    type = models.CharField(
        max_length=1, choices=DECK_TYPE, default=DEFAULT_DECK
    )
    new_card = models.PositiveSmallIntegerField(default=0)
    learning_card = models.PositiveSmallIntegerField(default=0)
    review_card = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    guest_users = models.ManyToManyField(
        User,
        through="AccessDeck",
        through_fields=("deck", "user"),
        related_name="share_decks",
    )
    is_shared = models.BooleanField(default=False)
    sharing_permission = models.CharField(
        max_length=1,
        choices=PERMISSION_TYPE,
        default=DEFAULT_PERMISSION,
        blank=True,
        null=True,
    )
    sharing_code = models.CharField(max_length=16, null=True)

    def __str__(self):
        return self.deck_name


class AccessDeck(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(
        max_length=1, choices=PERMISSION_TYPE, default=DEFAULT_PERMISSION
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.deck} - @{self.user} - {self.permission}"


####---- Card ------------------------------
class Card(models.Model):
    DEFAULT_STATUS = "0"
    CARD_STATUS = [
        (DEFAULT_STATUS, "New"),
        ("1", "Learning"),
        ("2", "To review"),
    ]

    # Relationship fields
    deck = models.ForeignKey("Deck", on_delete=models.CASCADE)
    # Own fields
    front = RichTextUploadingField(
        blank=True, null=True, config_name="card_ckeditor"
    )
    back = RichTextUploadingField(
        blank=True, null=True, config_name="card_ckeditor"
    )
    extra_info = RichTextUploadingField(
        blank=True, null=True, config_name="card_ckeditor"
    )
    order_number = models.PositiveSmallIntegerField(default=1)
    times_reviewed = models.PositiveIntegerField(default=0)
    # times_forgotten	= models.PositiveIntegerField(default=0)
    status = models.TextField(
        max_length=1, choices=CARD_STATUS, default=DEFAULT_STATUS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Card of {self.deck}"


class CardTag(models.Model):
    cards = models.ManyToManyField("Card")
    tag_name = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        return self.tag_name


####---- Test ------------------------------
class Test(models.Model):
    DEFAULT_SORT = "0"
    SORT_TYPE = [
        (DEFAULT_SORT, "Randomly"),
        ("1", "Ascending"),
        ("2", "Descending"),
    ]

    deck = models.ForeignKey("Deck", on_delete=models.CASCADE)
    cards = models.ManyToManyField(
        "Card", through="Score", through_fields=("test", "card")
    )

    # description		= models.CharField(max_length=45, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sorted_by = models.TextField(
        max_length=1, choices=SORT_TYPE, default=DEFAULT_SORT
    )
    # total_duration	= models.DecimalField(max_digits=7, decimal_places=2, default=0)
    score_nr = models.PositiveSmallIntegerField(
        default=0
    )  # ('NR', "Not remembered")
    score_hr = models.PositiveSmallIntegerField(
        default=0
    )  # ('HR', 'Hardly remembered')
    score_er = models.PositiveSmallIntegerField(
        default=0
    )  # ('ER', 'Easily remembered')
    held_on = models.DateTimeField(blank=True, null=True)
    # scheduled_for	= models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Test from {self.deck}"


class Score(models.Model):
    DEFAULT_SCORE = "NR"
    SCORE_TYPE = [
        (DEFAULT_SCORE, "Not remembered"),
        ("HR", "Hardly remembered"),
        ("ER", "Easily remembered"),
    ]

    test = models.ForeignKey("Test", on_delete=models.CASCADE)
    card = models.ForeignKey("Card", on_delete=models.CASCADE)

    score = models.TextField(
        max_length=2, choices=SCORE_TYPE, default=DEFAULT_SCORE
    )
    # duration	= models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def __str__(self):
        # return f"{self.score} - {self.duration}"
        return self.score


####---- Deck community ------------------------------
class BoardDeck(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    decks = models.ManyToManyField(Deck)

    name = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner} - {self.name}"
