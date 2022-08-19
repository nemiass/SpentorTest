from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from a01_note.models import Page

from .forms import CardModelForm, DeckModelForm
from .models import BoardDeck, Card, Deck, Score, Test

from a01_note.views import (  # isort:skip
    fetch_sidebar_data,
    generate_object_code,
    validate_page_owner,
)


####---- Own functions ------------------------------
def validate_deck_owner(deck_id, user):
    deck = Deck.objects.get(pk=deck_id)

    if deck.owner == user:
        return True
    elif user.is_superuser:
        return True
    else:
        return False


def validate_deck_access(deck_id, user):
    deck = Deck.objects.get(pk=deck_id)
    deck_access = {
        "has_access": False,
        "user_access": {
            "role": None,  # ('owner', 'superuser', 'guest', 'community member', 'anonymous')
            "permission": None,  # [ ('0', 'viewer'), ('1', 'commenter'), ('2', 'editor'), ]
            "permission_value": None,
        },
    }

    if deck.owner == user:
        deck_access["has_access"] = True
        deck_access["user_access"]["role"] = "owner"
        deck_access["user_access"]["permission"] = "2"
        deck_access["user_access"]["permission_value"] = "editor"

    elif user.is_superuser:
        deck_access["has_access"] = True
        deck_access["user_access"]["role"] = "superuser"
        deck_access["user_access"]["permission"] = "0"
        deck_access["user_access"]["permission_value"] = "viewer"

    elif user.is_authenticated:
        access_qs = deck.accessdeck_set.filter(user=user)

        if access_qs.count() == 1:
            deck_access["has_access"] = True
            deck_access["user_access"]["role"] = "guest"
            deck_access["user_access"][
                "permission"
            ] = access_qs.first().permission
            deck_access["user_access"][
                "permission_value"
            ] = access_qs.first().get_permission_display

        elif deck.is_shared == True:
            deck_access["has_access"] = True
            deck_access["user_access"]["role"] = "community member"
            deck_access["user_access"]["permission"] = deck.sharing_permission
            deck_access["user_access"][
                "permission_value"
            ] = deck.get_sharing_permission_display

    elif user.is_anonymous:
        if deck.is_shared == True:
            deck_access["has_access"] = True
            deck_access["user_access"]["role"] = "anonymous"
            deck_access["user_access"]["permission"] = deck.sharing_permission
            deck_access["user_access"][
                "permission_value"
            ] = deck.get_sharing_permission_display

    print(f"🧢️🧢️🧢️ {deck_access['user_access']['role']} 🧢️🧢️🧢️")
    return deck_access


def set_card_order(id_deck):
    # Set the card's order number according to the last order
    deck = Deck.objects.get(pk=id_deck)

    if deck.card_set.count() > 0:
        last_card = deck.card_set.order_by("order_number").last()
        card_order = last_card.order_number + 1
    else:
        card_order = 1

    return card_order


def update_card_quantity(card_id):
    # Update the quantities of deck's card before deleting one
    card = Card.objects.get(pk=card_id)
    deck_id = card.deck.id

    if card.status == "0":
        new_card_q = card.deck.new_card - 1
        Deck.objects.filter(pk=deck_id).update(new_card=new_card_q)
        return True

    elif card.status == "1":
        learning_card_q = card.deck.learning_card - 1
        Deck.objects.filter(pk=deck_id).update(learning_card=learning_card_q)
        return True

    elif card.status == "2":
        review_card_q = card.deck.review_card - 1
        Deck.objects.filter(pk=deck_id).update(review_card=review_card_q)
        return True

    else:
        return False


def get_customized_deck(user):
    if user.is_superuser:
        return Deck.objects.filter(Q(type="1") | Q(type="2")).order_by(
            "-created_at"
        )
    else:  # QUESTION: If a page is moved to the trash, the customized deck should be hidden too?
        return Deck.objects.filter(
            Q(owner=user), Q(type="1") | Q(type="2")
        ).order_by("-created_at")


def fetch_score_test(deck_id):
    # Retrieve and prepare test's scores for displaying them using an Apex Chart
    test_list = Test.objects.filter(deck=deck_id).order_by("created_at")
    score_list = {
        "NR": [],
        "HR": [],
        "ER": [],
        "NR_all": 0,
        "HR_all": 0,
        "ER_all": 0,
        "all_card": 0,
    }

    for test in test_list:
        score_list["NR"].append(test.score_nr)
        score_list["HR"].append(test.score_hr)
        score_list["ER"].append(test.score_er)
        score_list["NR_all"] += test.score_nr
        score_list["HR_all"] += test.score_hr
        score_list["ER_all"] += test.score_er

    score_list["all_card"] = (
        score_list["NR_all"] + score_list["HR_all"] + score_list["ER_all"]
    )

    return score_list


def fecth_active_test(deck_id):
    test_list = Test.objects.filter(Q(deck=deck_id) & Q(is_active=True))

    if test_list.count() == 1:
        for test in test_list:
            return test
    else:
        return False


####---- Deck ------------------------------
## Deck types: [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
## 		Basic:		a deck related to ONLY ONE PAGE
## 		Customized:	a deck that was created with at least one deck
## 		Customized from community:	a deck created using pined decks from deck community


@login_required(redirect_field_name=None)
def DeckUpsert(request, page_id):
    # UPdate and inSERT the page's deck
    if validate_page_owner(page_id, request.user):
        page = Page.objects.get(pk=page_id)
        DeckForm = modelform_factory(
            Deck, form=DeckModelForm, fields=("description",)
        )
        context = {}

        if hasattr(
            page, "deck"
        ):  # UPDATE deck's details (it works thanks to the one to one relationship)
            deck = Deck.objects.get(page=page_id)
            form = DeckForm(request.POST or None, instance=deck)
            context["deck"] = deck

            if form.is_valid():
                form.save()
                return redirect(
                    reverse("a01_note:page-detail", kwargs={"pk": page_id})
                )
        else:  # INSERT the page's deck
            if request.method == "POST":
                form = DeckForm(request.POST)

                if form.is_valid():
                    new_deck = form.save(commit=False)
                    new_deck.page = Page.objects.get(pk=page_id)
                    new_deck.owner = request.user
                    new_deck.deck_name = f"{new_deck.page}'s deck"
                    new_deck.sharing_code = generate_object_code(new_deck.id)
                    new_deck.save()
                    return redirect(
                        reverse("a01_note:page-detail", kwargs={"pk": page_id})
                    )
            else:
                form = DeckModelForm

        context["form"] = form
        context["page"] = page
        context["web_title"] = "Page deck | add & edit"
        context["page_title"] = "Add your deck"
        context["sidebar_data"] = fetch_sidebar_data(request.user)
        return render(request, "evaluation/deck_form.html", context)
    else:
        raise PermissionDenied


class DeckDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    redirect_field_name = None

    model = Deck
    template_name = "evaluation/deck_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_access"] = validate_deck_access(
            self.kwargs["pk"], self.request.user
        )["user_access"]
        context["card_status"] = dict(Card.CARD_STATUS)
        context["active_test"] = fecth_active_test(self.object.id)
        context["web_title"] = "Deck detail | view"
        context["page_title"] = self.object.deck_name
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)

        if "from" in self.kwargs.keys():
            if self.kwargs["from"] == "d":
                context["from_community"] = "from_deck_community"
            else:
                context["from_community"] = "not_defined"

        return context

    def test_func(self):
        return validate_deck_access(self.kwargs["pk"], self.request.user)[
            "has_access"
        ]


@login_required(redirect_field_name=None)
def DeckDelete(request, pk):
    # Works for both basic and customized deck
    deck = Deck.objects.get(pk=pk)

    if validate_deck_owner(deck.id, request.user):
        if (
            deck.type == "0"
        ):  # [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
            page_id = deck.page.id
            deck.delete()
            return redirect(
                reverse("a01_note:page-detail", kwargs={"pk": page_id})
            )
        else:
            deck.delete()
            return redirect(reverse("evaluation:deck-list"))
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def DeckShare(request, pk):
    # Works for both basic and customized deck
    deck = Deck.objects.get(pk=pk)

    if validate_deck_owner(deck.id, request.user):
        if request.method == "POST":
            Deckform = modelform_factory(Deck, fields=("is_shared",))
            form = Deckform(request.POST, instance=deck)

            if form.is_valid():
                deck_obj = form.save(commit=False)

                if deck_obj.is_shared == True:
                    deck_obj.sharing_permission = "0"  # [ ('0', 'viewer'), ('1', 'commenter'), ('2', 'editor'), ]
                else:
                    deck_obj.sharing_permission = None

                deck_obj.save()

        if (
            deck.type == "0"
        ):  # [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
            if (
                "source_template" in request.POST.keys()
            ):  # redirect to a single template for basic deck
                if request.POST["source_template"] == "from_deck_detail":
                    return redirect(
                        reverse(
                            "evaluation:deck-detail", kwargs={"pk": deck.id}
                        )
                    )
                else:
                    raise Http404
            else:
                return redirect(
                    reverse(
                        "a01_note:page-detail", kwargs={"pk": deck.page.id}
                    )
                )
        else:
            return redirect(
                reverse("evaluation:deck-detail", kwargs={"pk": deck.id})
            )
    else:
        raise PermissionDenied


class DeckList(LoginRequiredMixin, ListView):
    redirect_field_name = None

    model = Page
    template_name = "evaluation/deck_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deck_customized_list"] = get_customized_deck(
            self.request.user
        )
        context["web_title"] = "Deck list | view"
        context["page_title"] = "Deck list"
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Page.objects.filter(
                Q(in_trash=False) & Q(deck__isnull=False)
            ).order_by("-created_at")
        else:
            return Page.objects.filter(
                Q(owner=self.request.user),
                Q(in_trash=False) & Q(deck__isnull=False),
            ).order_by("-created_at")


@login_required(redirect_field_name=None)
def DeckCustomizedCreate(request):
    extra_key = (
        "source_template"  # Use for redirecting to deck list or deck community
    )
    len_post = len(request.POST)

    # Set variables for the deck creation and further redirection
    if extra_key in request.POST.keys():
        if request.POST[extra_key] == "from_deck_community":
            len_post = (
                len_post - 2
            )  # source_template data is set in the 2nd place
            redirect_to = "evaluation:deck-community"
        else:
            len_post = -1
            redirect_to = "evaluation:deck-community"
    else:
        len_post = len_post - 1  # csrf_token data is set in the 1st place
        redirect_to = "evaluation:deck-list"

    if request.method == "POST":

        # Evaluate the lenght of request context in order to start the process
        if len_post > 0:
            chkbx_name_prefix = (
                f"chkbx_id_deck-"  # prefix used for  the checkbox name
            )
            selected_decks = []
            new_card_all = 0

            # Fecth the selected decks
            for key in request.POST.keys():
                if chkbx_name_prefix in key:
                    deck = Deck.objects.get(pk=request.POST[key])
                    deck_cards = deck.card_set.all()
                    selected_decks.append([deck, deck_cards])
                    new_card_all += len(deck_cards)

            # Create the new customized deck object
            customized_deck = Deck.objects.create(
                owner=request.user,
                new_card=new_card_all,
            )

            if request.POST.get(extra_key, None) == "from_deck_community":
                customized_deck.deck_name = f"Deck community: new customized deck from {len(selected_decks)} decks"
                customized_deck.type = "2"  # [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
            else:
                customized_deck.deck_name = (
                    f"A customized deck from {len(selected_decks)} decks"
                )
                customized_deck.type = "1"

            customized_deck.sharing_code = generate_object_code(
                customized_deck.id
            )
            customized_deck.save()

            # Bind the seleted decks with the new customized_deck
            for s_deck in selected_decks:
                # Set the relationship
                customized_deck.deck_parts.add(s_deck[0])
                # Copy the related deck's card
                for d_card in s_deck[1]:
                    Card.objects.create(
                        deck=customized_deck,
                        front=d_card.front,
                        back=d_card.back,
                        extra_info=d_card.extra_info,
                    )

            messages.add_message(
                request,
                messages.SUCCESS,
                "Done! Your customized deck was created successfully.",
                extra_tags="customized_deck_success",
            )

            return redirect(reverse(redirect_to))
        else:
            if len_post == -1:
                msg = "Oh! There was an error. Please try again."
            else:
                msg = (
                    "Mmmm. You have not seleted any deck. Choose at least one."
                )
            messages.add_message(
                request,
                messages.ERROR,
                msg,
                extra_tags="customized_deck_error",
            )

    return redirect(reverse(redirect_to))


class DeckCustomizedUpdate(
    LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    model = Deck
    form_class = modelform_factory(
        Deck,
        form=DeckModelForm,
        fields=(
            "deck_name",
            "description",
        ),
    )
    template_name = "evaluation/deck_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_title"] = "Page deck | edit"
        context["page_title"] = self.object.deck_name
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_success_url(self):
        return reverse_lazy(
            "evaluation:deck-detail", kwargs={"pk": self.object.id}
        )

    def test_func(self):
        return validate_deck_owner(self.kwargs["pk"], self.request.user)


####---- Card ------------------------------
@login_required(redirect_field_name=None)
def CardCreate(request, deck_id):
    # Works for both basic and customized deck
    deck = Deck.objects.get(pk=deck_id)

    if validate_deck_owner(deck_id, request.user):

        if fecth_active_test(deck_id) == False:
            if request.method == "POST":
                form = CardModelForm(request.POST)

                if form.is_valid():
                    new_card = form.save(commit=False)
                    new_card.deck = deck
                    new_card.order_number = set_card_order(deck_id)
                    new_card.save()

                    # Update the quantity of new card
                    Deck.objects.filter(pk=deck_id).update(
                        new_card=(deck.new_card + 1)
                    )

                    if (
                        deck.type == "0"
                    ):  # [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
                        return redirect(
                            reverse(
                                "a01_note:page-detail",
                                kwargs={"pk": deck.page.id},
                            )
                        )
                    else:
                        return redirect(
                            reverse(
                                "evaluation:deck-detail",
                                kwargs={"pk": deck.id},
                            )
                        )
            else:
                form = CardModelForm

            context = {
                "form": form,
                "deck": deck,  # Used for go back and populate the breadcrumb
                "web_title": "Deck card | add",
                "page_title": "Add your card",
                "sidebar_data": fetch_sidebar_data(request.user),
            }
            return render(request, "evaluation/card_form.html", context)

        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Oh! You have a scheduled test. Finish it before adding new cards.",
                extra_tags="creation_card_error",
            )

            if (
                deck.type == "0"
            ):  # [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
                return redirect(
                    reverse(
                        "a01_note:page-detail", kwargs={"pk": deck.page.id}
                    )
                )
            else:
                return redirect(
                    reverse("evaluation:deck-detail", kwargs={"pk": deck.id})
                )
    else:
        raise PermissionDenied


class CardUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Works for both basic and customized deck
    redirect_field_name = None

    model = Card
    form_class = CardModelForm
    template_name = "evaluation/card_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "deck"
        ] = self.object.deck  # Used for go back and populate the breadcrumb
        context["web_title"] = "Edit card | edit"
        context["page_title"] = "Edit your card"
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_success_url(self):
        if self.object.deck.type == "0":
            return reverse(
                "a01_note:page-detail", kwargs={"pk": self.object.deck.page.id}
            )
        else:
            return reverse(
                "evaluation:deck-detail", kwargs={"pk": self.object.deck.id}
            )

    def test_func(self):
        card = Card.objects.get(pk=self.kwargs["pk"])
        return validate_deck_owner(card.deck.id, self.request.user)


@login_required(redirect_field_name=None)
def CardDelete(request, pk):
    # Works for both basic and customized deck
    card = Card.objects.get(pk=pk)
    deck = card.deck

    if validate_deck_owner(deck.id, request.user):
        update_card_quantity(card.id)
        card.delete()

        if (
            deck.type == "0"
        ):  # [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
            return redirect(
                reverse("a01_note:page-detail", kwargs={"pk": deck.page.id})
            )
        else:
            return redirect(
                reverse("evaluation:deck-detail", kwargs={"pk": deck.id})
            )
    else:
        raise PermissionDenied


####---- Test ------------------------------
class TestList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    # Works for both basic and customized deck
    redirect_field_name = None

    model = Test
    template_name = "evaluation/test_id_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deck"] = Deck.objects.get(pk=self.kwargs["deck_id"])
        context["score_type"] = dict(Score.SCORE_TYPE)
        context["score_list"] = fetch_score_test(self.kwargs["deck_id"])
        context["web_title"] = "Test List | view"
        context["page_title"] = "Test List"
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_queryset(self):
        return Test.objects.filter(deck=self.kwargs["deck_id"]).order_by(
            "-created_at"
        )

    def test_func(self):
        return validate_deck_owner(self.kwargs["deck_id"], self.request.user)


class TestDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    # Works for both basic and customized deck
    redirect_field_name = None

    model = Test
    template_name = "evaluation/test_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["score_type"] = dict(Score.SCORE_TYPE)
        context["web_title"] = "Test detail | view"
        context["page_title"] = self.object
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def test_func(self):
        test = Test.objects.get(pk=self.kwargs["pk"])
        deck_id = test.deck.id
        return validate_deck_owner(deck_id, self.request.user)


@login_required(redirect_field_name=None)
def TestCreate(request, deck_id):
    # Works for both basic and customized deck

    if validate_deck_owner(deck_id, request.user):
        deck = Deck.objects.get(pk=deck_id)

        if request.method == "POST":

            if deck.test_set.filter(is_active=True):
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Oh! You have a scheduled test. Finish it before starting a new one.",
                    extra_tags="creation_test_error",
                )

            else:
                # Create a test
                test = Test.objects.create(deck=deck)

                # Create the test's items (include ALL CARDS, doesn't matter the current status)
                card_list = deck.card_set.all()
                for card in card_list:
                    test.cards.add(card)
                    card.status = "1"  # [('0', 'New'), ('1', 'Learning'), ('2', 'To review'),]
                    card.save()

                # Update the related test's deck
                if deck.new_card > 0:
                    new_card_q = deck.new_card
                    deck.new_card = 0
                    deck.learning_card = new_card_q
                else:
                    review_card_q = deck.review_card
                    deck.review_card = 0
                    deck.learning_card = review_card_q
                deck.save()

                return redirect(
                    reverse("evaluation:test-detail", kwargs={"pk": test.id})
                )

        # redirect to
        if (
            deck.type == "0"
        ):  # [('0', 'Basic'), ('1', 'Customized'), ('2', 'Customized from community'),]
            return redirect(
                reverse("a01_note:page-detail", kwargs={"pk": deck.page.id})
            )
        else:
            return redirect(
                reverse("evaluation:deck-detail", kwargs={"pk": deck.id})
            )
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def TestStart(request, pk):
    # Works for both basic and customized deck
    test = Test.objects.get(pk=pk)
    deck_id = test.deck.id

    if validate_deck_owner(deck_id, request.user):
        card_list = Card.objects.filter(test__id=test.id).order_by("?")

        # Form settings
        in_name_card = "id_card-"  # Prefix used for the input hidden (related to the card)
        in_name_answer = "card_answer-"  # Prefix used for the name of the card's input answer
        score_type = (
            Score.SCORE_TYPE
        )  # {('NR', "Not remembered"), ('HR', 'Hardly remembered'), ('ER', 'Easily remembered')}

        if request.method == "POST":
            answer_summary = [0, 0, 0]

            for card in card_list:
                # Build the input's names (related to the card and it answer)
                in_card = f"{in_name_card}{card.id}"
                in_answer = f"{in_name_answer}{card.id}"

                # Fetch input values
                card_id = request.POST[in_card]
                score = request.POST[in_answer]

                # Count the number of answer according to its score type
                if score == score_type[0][0]:  # ('NR', "Not remembered")
                    answer_summary[0] += 1
                elif score == score_type[1][0]:  # ('HR', 'Hardly remembered')
                    answer_summary[1] += 1
                elif score == score_type[2][0]:  # ('ER', 'Easily remembered')
                    answer_summary[2] += 1

                # Save scores inside SCORE model
                test.score_set.filter(card=card_id).update(score=score)

                # Update CARD fields
                card.times_reviewed = card.times_reviewed + 1
                card.status = "2"  # {('0', 'New'), ('1', 'Learning'), ('2', 'To review')}
                card.save()

            # Update TEST fields
            test.is_active = False
            test.score_nr = answer_summary[0]
            test.score_hr = answer_summary[1]
            test.score_er = answer_summary[2]
            test.held_on = datetime.now()
            test.save()

            # Update DECK fields: learning_card and review_card will be affected by len(card_list)
            learning_card_q = test.deck.learning_card
            review_card_q = test.deck.review_card
            Deck.objects.filter(pk=deck_id).update(
                learning_card=0, review_card=review_card_q + learning_card_q
            )

            messages.success(
                request, ("Done! Your test was successfully saved.")
            )
            return redirect(
                reverse("evaluation:test-detail", kwargs={"pk": test.id})
            )

        context = {
            "card_list": card_list,
            "test": test,  # Used for go back
            "web_title": "Test start | start",
            "page_title": "Start your test",
            "sidebar_data": fetch_sidebar_data(request.user),
            # Form variables
            "in_name_card": in_name_card,
            "in_name_answer": in_name_answer,
            "score_nr": score_type[0][0],
            "score_nr_value": score_type[0][1],
            "score_hr": score_type[1][0],
            "score_hr_value": score_type[1][1],
            "score_er": score_type[2][0],
            "score_er_value": score_type[2][1],
        }
        return render(request, "evaluation/test_start.html", context)
    else:
        raise PermissionDenied


####---- Deck community ------------------------------
class DeckCommunity(LoginRequiredMixin, ListView):
    redirect_field_name = None

    model = Deck
    template_name = "evaluation/deck_community.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_title"] = "Deck community | App Notes"
        context["page_title"] = "Deck community"
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_queryset(self):
        return Deck.objects.filter(is_shared=True).order_by("deck_name")


@login_required(redirect_field_name=None)
def DeckCommunityPin(request, pk):
    # Add or remove the request deck from a default board
    deck = Deck.objects.get(pk=pk)

    if request.method == "POST" or request.method == "GET":
        board_qs = request.user.boarddeck_set.all()

        if board_qs.count() == 0:
            board = BoardDeck.objects.create(
                owner=request.user,
                name="default",
            )
            board.decks.add(deck)

        elif board_qs.count() == 1:
            board = board_qs.first()
            pined_deck = board.decks.filter(pk=deck.id)

            # pin deck
            if pined_deck.count() == 0:
                board.decks.add(deck)
            # unpin deck
            elif pined_deck.count() == 1:
                board.decks.remove(deck)

        return redirect(reverse("evaluation:deck-community"))
    else:
        raise PermissionDenied


# return HttpResponse(f"Working perfectly ;D ...<br>")
# return HttpResponse(f"Working perfectly ;D ...<br> {text}")
# return HttpResponse(f"ERROR: {formset.errors}")
# return HttpResponse(f"Working perfectly ;D ...<br>")
# print(f"🐝️🐝️🐝️ {} 🐝️🐝️🐝️")
