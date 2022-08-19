from django.urls import path

from . import views

app_name = "a01_note"  # Convention variable's name
urlpatterns = [  # Contiene todas las URLs de la app
    ####---- Page ------------------------------
    path("", views.Home.as_view(), name="home"),
    path("page_create/", views.PageCreateForm, name="page-create"),
    path(
        "page_detail/<int:pk>/", views.PageDetail.as_view(), name="page-detail"
    ),
    path(
        "page_update/<int:pk>/",
        views.PageUpdateForm.as_view(),
        name="page-update",
    ),
    path("page_delete/<int:pk>/", views.PageDelete, name="page-delete"),
    path("page_search/", views.PageSearch, name="page-search"),
    path("page/<int:pk>/trash/", views.PageTrash, name="page-trash"),
    path(
        "page/trash/list/",
        views.PageTrashList.as_view(),
        name="page-trash-list",
    ),
    path(
        "page/<int:pk>/trash/update/",
        views.PageTrashUpdate,
        name="page-trash-update",
    ),
    ####---- Page property ------------------------------
    path(
        "property_create/<int:page_id>/",
        views.PropertyCreate,
        name="property-create",
    ),
    path(
        "property_update/<int:pk>/",
        views.PropertyUpdate,
        name="property-update",
    ),
    path(
        "property_delete/<int:pk>/",
        views.PropertyDelete,
        name="property-delete",
    ),
    ####---- Page property item ------------------------------
    path(
        "tag_property_form/<int:pageproperty_id>&<int:page_id>/",
        views.TagPropertyCreateUpdate,
        name="tag-property-form",
    ),
    path(
        "webmark_property_create/<int:page_id>/",
        views.WebmarkPropertyCreate,
        name="webmark-property-create",
    ),
    path(
        "webmark_property_update/<int:pk>/",
        views.WebmarkPropertyUpdate.as_view(),
        name="webmark-property-update",
    ),
    path(
        "webmark_property_delete/<int:pk>/",
        views.WebmarkPropertyDelete,
        name="webmark-property-delete",
    ),
    ####---- Page summary ------------------------------
    path(
        "page/<int:page_id>/summary/create/",
        views.PageSummaryCreate,
        name="page-summary-create",
    ),
    path(
        "page/summary/<int:pk>/delete/",
        views.PageSummaryDelete,
        name="page-summary-delete",
    ),
    ####---- Page summary item ------------------------------
    path(
        "page/summary/<int:summary_id>/disease/upsert/",
        views.DiseaseSummaryUpsert,
        name="disease-summary-upsert",
    ),
    ####---- Page index's content ------------------------------
    path(
        "block_index_create/<int:page_id>/",
        views.BlockIndexCreate,
        name="block-index-create",
    ),  # TODO: is posible to update block_index in order to turn it into other content type
    path(
        "block_index_delete/<int:pk>/",
        views.BlockIndexDelete,
        name="block-index-delete",
    ),
    ####---- Page content ------------------------------
    path(
        "text_content_form/<int:blockindex_id>&<int:page_id>/",
        views.TextContentCreateUpdate,
        name="text-content-form",
    ),
    path(
        "image_content_form/<int:blockindex_id>&<int:page_id>/",
        views.ImageContentCreateUpdate,
        name="image-content-form",
    ),
    path(
        "file_content_form/<int:blockindex_id>&<int:page_id>/",
        views.FileContentCreateUpdate,
        name="file-content-form",
    ),
    path(
        "webmark_content_form/<int:blockindex_id>&<int:page_id>/",
        views.WebmarkContentCreateUpdate,
        name="webmark-content-form",
    ),
    ####---- Page children ------------------------------
    path(
        "child_page_create/<int:page_id>/",
        views.ChildPageCreate,
        name="child-page-create",
    ),
    ####---- Page community ------------------------------
    path(
        "page/community/", views.PageCommunity.as_view(), name="page-community"
    ),
    path("page/<int:pk>/share/", views.PageShare, name="page-share"),
    path("page/<int:pk>/invite/", views.PageInvite, name="page-invite"),
    path(
        "page/<int:pk>/guest/<int:user_id>/delete/",
        views.PageGuestDelete,
        name="page-guest-delete",
    ),
    path(
        "page/<str:sharing_code>/access/", views.PageAccess, name="page-access"
    ),
    ####---- API ------------------------------
    path("api/cie10/", views.Cie10ApiList, name="cie10-api-list"),
    path("api/symptom/", views.SymptomApiList, name="symptom-api-list"),
    path("api/drug/", views.DrugApiList, name="drug-api-list"),
]
