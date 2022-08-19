from django.urls import path

from . import views

app_name = "evaluation"
urlpatterns = [
    ####---- Deck ------------------------------
    path(
        "deck/upsert/<int:page_id>/", views.DeckUpsert, name="deck-upsert"
    ),  # UPdate and inSERT
    path(
        "deck/detail/<int:pk>/", views.DeckDetail.as_view(), name="deck-detail"
    ),
    path("deck/delete/<int:pk>/", views.DeckDelete, name="deck-delete"),
    path("deck/share/<int:pk>/", views.DeckShare, name="deck-share"),
    path("deck/list/", views.DeckList.as_view(), name="deck-list"),
    path(
        "deck/customized/create/",
        views.DeckCustomizedCreate,
        name="deck-customized-create",
    ),
    path(
        "deck/customized/update/<int:pk>/",
        views.DeckCustomizedUpdate.as_view(),
        name="deck-customized-update",
    ),
    ####---- Card ------------------------------
    path("card/create/<int:deck_id>/", views.CardCreate, name="card-create"),
    path(
        "card/update/<int:pk>/", views.CardUpdate.as_view(), name="card-update"
    ),
    path("card/delete/<int:pk>/", views.CardDelete, name="card-delete"),
    ####---- Test ------------------------------
    path(
        "test/list/<int:deck_id>/", views.TestList.as_view(), name="test-list"
    ),
    path(
        "test/detail/<int:pk>/", views.TestDetail.as_view(), name="test-detail"
    ),
    path("test/create/<int:deck_id>/", views.TestCreate, name="test-create"),
    path("test/start/<int:pk>/", views.TestStart, name="test-start"),
    ####---- Deck community ------------------------------
    path(
        "community/deck/", views.DeckCommunity.as_view(), name="deck-community"
    ),
    path(
        "community/deck/<int:pk>/detail/<str:from>/",
        views.DeckDetail.as_view(),
        name="deck-community-detail",
    ),
    path(
        "community/deck/<int:pk>/pin/",
        views.DeckCommunityPin,
        name="deck-community-pin",
    ),
]
