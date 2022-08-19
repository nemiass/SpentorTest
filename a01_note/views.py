import json

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.forms import inlineformset_factory, modelform_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView

from evaluation.models import Test

from .forms import (
    BlockIndexModelForm,
    DiseaseSummaryForm,
    FileContentModelForm,
    ImageContentModelForm,
    PageModelForm,
    PagePropertyForm,
    TagPropertyForm,
    TextContentModelForm,
    WebmarkContentModelForm,
    WebmarkPropertyModelForm,
)
from .models import (
    Access,
    BlockIndex,
    Cie10,
    Disease,
    Drug,
    FileContent,
    ImageContent,
    Page,
    PageProperty,
    PropertyType,
    Summary,
    Symptom,
    Tag,
    TextContent,
    WebmarkContent,
    WebmarkProperty,
)


####---- Own functions ------------------------------
def fetch_sidebar_data(page_owner):
    if page_owner.is_superuser:
        return (
            Page.objects.filter(level=0)
            .exclude(in_trash=True)
            .order_by("created_at")
        )
    else:
        return (
            Page.objects.filter(Q(owner=page_owner) & Q(level=0))
            .exclude(in_trash=True)
            .order_by("created_at")
        )


def generate_object_code(object_id):
    from hashlib import blake2b

    return blake2b(str(object_id).encode(), digest_size=8).hexdigest()


def validate_page_owner(page_id, user):
    # Validate if the current user is the page's owner
    page = Page.objects.get(pk=page_id)

    if page.owner == user:
        return True
    elif user.is_superuser:
        return True
    else:
        return False


def validate_page_access(page_id, user):
    page = Page.objects.get(pk=page_id)
    page_access = {
        "has_access": False,
        "user_access": {
            "role": None,  # ('owner', 'superuser', 'guest', 'community member', 'anonymous')
            "permission": None,  # [ ('0', 'viewer'), ('1', 'commenter'), ('2', 'editor'), ]
            "permission_value": None,
        },
    }

    if page.owner == user:
        page_access["has_access"] = True
        page_access["user_access"]["role"] = "owner"
        page_access["user_access"]["permission"] = "2"
        page_access["user_access"]["permission_value"] = "editor"

    elif user.is_superuser:
        page_access["has_access"] = True
        page_access["user_access"]["role"] = "superuser"
        page_access["user_access"]["permission"] = "0"
        page_access["user_access"]["permission_value"] = "viewer"

    elif user.is_authenticated:
        access_qs = page.access_set.filter(user=user)

        if access_qs.count() == 1:
            page_access["has_access"] = True
            page_access["user_access"]["role"] = "guest"
            page_access["user_access"][
                "permission"
            ] = access_qs.first().permission
            page_access["user_access"][
                "permission_value"
            ] = access_qs.first().get_permission_display

        elif page.is_shared == True:
            page_access["has_access"] = True
            page_access["user_access"]["role"] = "community member"
            page_access["user_access"]["permission"] = page.sharing_permission
            page_access["user_access"][
                "permission_value"
            ] = page.get_sharing_permission_display

    elif user.is_anonymous:
        if page.is_shared == True:
            page_access["has_access"] = True
            page_access["user_access"]["role"] = "anonymous"
            page_access["user_access"]["permission"] = page.sharing_permission
            page_access["user_access"][
                "permission_value"
            ] = page.get_sharing_permission_display

    return page_access


####---- Page ------------------------------
# List all main pages (level=0)
class Home(LoginRequiredMixin, ListView):
    # login_url = 'master:login-user'
    redirect_field_name = None

    model = Page
    template_name = "a01_note/home.html"
    # queryset 		= Page.objects.filter(Q(owner=1) & Q(level=0)).exclude(in_trash=True).order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_title"] = "Home | App Notes"
        context["page_title"] = "All pages"
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return (
                Page.objects.filter(level=0)
                .exclude(in_trash=True)
                .order_by("created_at")
            )
        else:
            return (
                Page.objects.filter(Q(owner=self.request.user) & Q(level=0))
                .exclude(in_trash=True)
                .order_by("created_at")
            )


# Create a page and its details
@login_required(redirect_field_name=None)
def PageCreateForm(request):
    PageparenFormSet = modelform_factory(
        Page,
        form=PageModelForm,
        fields=(
            "page_name",
            "description",
            "emoji",
            "cover",
            "hex_color",
            "is_favourite",
        ),
    )
    submitted = False

    if request.method == "POST":
        formset = PageparenFormSet(request.POST, request.FILES)
        if formset.is_valid():
            page = formset.save(commit=False)
            page.owner = request.user
            page.sharing_code = generate_object_code(page.id)
            page.save()
            return redirect(
                reverse("a01_note:page-detail", kwargs={"pk": page.id})
            )
    else:
        formset = PageModelForm

    context = {
        "formset": formset,
        "web_title": "Add pages | new",
        "page_title": "Add a new page",
        "sidebar_data": fetch_sidebar_data(request.user),
    }
    return render(request, "a01_note/page_create_form.html", context)


class PageDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    redirect_field_name = None  # A LoginRequiredMixin attribute

    model = Page
    template_name = "a01_note/page_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_access"] = validate_page_access(
            self.kwargs["pk"], self.request.user
        )["user_access"]
        context["web_title"] = "My page | detail"
        context["page_title"] = self.object.page_name
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)

        if self.object.is_shared or self.object.guest_users.count() > 0:
            page_url = reverse(
                "a01_note:page-access",
                kwargs={"sharing_code": self.object.sharing_code},
            )
            context[
                "page_url"
            ] = f"{self.request._current_scheme_host}{page_url}"

        # Fetch active test related to the page's deck
        if hasattr(self.object, "deck"):
            test_list = Test.objects.filter(
                Q(deck=self.object.deck.id) & Q(is_active=True)
            )
            if test_list.count() == 1:
                for test in test_list:
                    context["active_test"] = test
            else:
                context["active_test"] = False
        else:
            context["active_test"] = False

        return context

    def test_func(self):
        page_access = validate_page_access(
            self.kwargs["pk"], self.request.user
        )
        return page_access["has_access"]

    def handle_no_permission(self):
        raise PermissionDenied


class PageUpdateForm(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    redirect_field_name = None

    model = Page
    form_class = modelform_factory(
        Page,
        form=PageModelForm,
        fields=(
            "page_name",
            "description",
            "emoji",
            "cover",
            "hex_color",
            "is_favourite",
        ),
    )
    template_name = "a01_note/page_update_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_title"] = "My page | edit"
        context["page_title"] = self.object.page_name
        context["page"] = self.object
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_success_url(self):
        # return reverse_lazy('a01_note:page-update', kwargs={'pk': self.kwargs.get('pk')})
        return reverse_lazy(
            "a01_note:page-update", kwargs={"pk": self.object.pk}
        )

    def test_func(self):
        return validate_page_owner(self.kwargs["pk"], self.request.user)


# Delete a page based on its level
@login_required(redirect_field_name=None)
def PageDelete(request, pk):
    if validate_page_owner(pk, request.user):
        page = Page.objects.get(pk=pk)

        if page.in_trash == True:  # Delete page from trash section
            page.delete()
            return redirect(reverse("a01_note:page-trash-list"))
        elif page.level == 0:  # Delete main pages (level = 0)
            page.delete()
            return HttpResponseRedirect(reverse("a01_note:home"))
        else:  # Delete page children (level >= 1)
            page_parent_id = page.page_parent.id
            page.delete()
            return redirect(
                reverse("a01_note:page-detail", kwargs={"pk": page_parent_id})
            )
    else:
        raise PermissionDenied


# Search a page based on its page_name and tag fields
@login_required(redirect_field_name=None)
def PageSearch(request):
    context = {
        "web_title": "Search pages | all",
        "page_title": "Results for your search",
        "sidebar_data": fetch_sidebar_data(request.user),
    }

    if request.method == "POST":
        search_keyword = request.POST["search_keyword"]
        # Filter by page_name and its related tags. Besides, group the result queryset so that skip duplicated objects
        if request.user.is_superuser:
            searched_page = Page.objects.filter(
                Q(page_name__icontains=search_keyword)
                | Q(tag__tag_name__icontains=search_keyword),
                in_trash=False,
            ).annotate(Count("id"))
        else:
            searched_page = Page.objects.filter(
                Q(owner=request.user),
                Q(page_name__icontains=search_keyword)
                | Q(tag__tag_name__icontains=search_keyword),
                in_trash=False,
            ).annotate(Count("id"))

        context["search_keyword"] = search_keyword
        context["searched_page"] = searched_page
        return render(request, "a01_note/page_search.html", context)
    else:
        return render(request, "a01_note/page_search.html", context)


# Move a page to trash section
@login_required(redirect_field_name=None)
def PageTrash(request, pk):
    if validate_page_owner(pk, request.user):
        Page.objects.filter(pk=pk).update(
            in_trash=True,
            updated_at=timezone.now(),
            moved_trash_at=timezone.now(),
        )
        return redirect(reverse("a01_note:home"))
    else:
        raise PermissionDenied


class PageTrashList(LoginRequiredMixin, ListView):
    redirect_field_name = None

    model = Page
    template_name = "a01_note/page_trash_list.html"
    context_object_name = "trash_page_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_title"] = "Trash | App Notes"
        context["page_title"] = "Pages moved to trash"
        context["sidebar_data"] = fetch_sidebar_data(
            self.request.user
        )  # Data for populating the ASIDE template
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Page.objects.filter(in_trash=True).order_by(
                "-moved_trash_at"
            )
        else:
            return Page.objects.filter(
                Q(owner=self.request.user) & Q(in_trash=True)
            ).order_by("-moved_trash_at")


# Restore the a page from TRASH section
@login_required(redirect_field_name=None)
def PageTrashUpdate(request, pk):
    if validate_page_owner(pk, request.user):
        Page.objects.filter(pk=pk).update(
            in_trash=False, updated_at=timezone.now()
        )
    else:
        raise PermissionDenied
    return redirect(reverse("a01_note:page-trash-list"))


####---- Page property ------------------------------
# Create page's property
@login_required(redirect_field_name=None)
def PropertyCreate(request, page_id):
    if validate_page_owner(page_id, request.user):

        page = Page.objects.get(pk=page_id)
        ## PropertyFormSet = inlineformset_factory(Page, PageProperty, form=PagePropertyForm, fields=('property_type', 'property_name', 'order_number'), extra=1)
        PropertyFormSet = inlineformset_factory(
            Page,
            PageProperty,
            form=PagePropertyForm,
            fields=("property_type", "property_name"),
            extra=1,
        )
        queryset = PageProperty.objects.none()
        submitted = False

        if request.method == "POST":
            formset = PropertyFormSet(request.POST, instance=page)
            if formset.is_valid():
                formset.save()
                redirect_to = (
                    f"/a01_note/property_create/{page.id}?submitted=True"
                )
                return HttpResponseRedirect(redirect_to)
        else:
            formset = PropertyFormSet(queryset=queryset, instance=page)
            if "submitted" in request.GET:
                submitted = True
        context = {
            "formset": formset,
            "submitted": submitted,
            "web_title": "Add property | new",
            "page_title": "Add a new property",
            "sidebar_data": fetch_sidebar_data(
                request.user
            ),  # Data for populating the ASIDE template
        }
        return render(request, "a01_note/property_create.html", context)
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def PropertyUpdate(request, pk):
    property = PageProperty.objects.get(pk=pk)

    if validate_page_owner(property.page_parent.id, request.user):
        ## PropertyFormSet = modelform_factory(PageProperty, form=PagePropertyForm, fields=('property_type', 'property_name', 'order_number'))
        PropertyFormSet = modelform_factory(
            PageProperty,
            form=PagePropertyForm,
            fields=("property_type", "property_name"),
        )
        formset = PropertyFormSet(request.POST or None, instance=property)

        if formset.is_valid():
            formset.save()
            return redirect(
                reverse(
                    "a01_note:page-detail",
                    kwargs={"pk": property.page_parent.id},
                )
            )
        context = {
            "formset": formset,
            "web_title": "Add property | edit",
            "page_title": "Edit property",
            "sidebar_data": fetch_sidebar_data(
                request.user
            ),  # Data for populating the ASIDE template
        }
        return render(request, "a01_note/property_update.html", context)
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def PropertyDelete(request, pk):
    property = PageProperty.objects.get(pk=pk)
    page_id = property.page_parent.id

    if validate_page_owner(page_id, request.user):
        property.delete()
        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page_id})
        )
    else:
        raise PermissionDenied


####---- Page property item ------------------------------
# Tag form (create and update)			# FIXME: Add delete view for Tag and set related page manually
@login_required(redirect_field_name=None)
def TagPropertyCreateUpdate(request, pageproperty_id, page_id):
    if validate_page_owner(page_id, request.user):
        property = PageProperty.objects.get(pk=pageproperty_id)
        page = Page.objects.get(pk=page_id)
        TagPropertyFormSet = inlineformset_factory(
            PageProperty,
            Tag,
            form=TagPropertyForm,
            fields=("pages", "tag_name"),
            widgets={"pages": forms.SelectMultiple(attrs={"hidden": "True"})},
            extra=1,
            labels={"pages": "", "tag_name": "Your tag"},
        )

        if request.method == "POST":
            formset = TagPropertyFormSet(request.POST, instance=property)
            if formset.is_valid():
                formset.save()
                return redirect(
                    reverse(
                        "a01_note:page-detail",
                        kwargs={"pk": property.page_parent.id},
                    )
                )
        else:
            formset = TagPropertyFormSet(
                initial=[{"pages": page}], instance=property
            )

        context = {
            "formset": formset,
            "web_title": "Add tag property | add & edit",
            "page_title": "Add your tags",
            "sidebar_data": fetch_sidebar_data(
                request.user
            ),  # Data for populating the ASIDE template
        }
        return render(request, "a01_note/tag_property_form.html", context)
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def WebmarkPropertyCreate(request, page_id):
    if validate_page_owner(page_id, request.user):
        WebmarkFormSet = modelform_factory(
            WebmarkProperty,
            form=WebmarkPropertyModelForm,
            fields=(
                "webmark_name",
                "webmark_url",
            ),
        )

        if request.method == "POST":
            form = WebmarkFormSet(request.POST)
            if form.is_valid():
                # Create a page property record
                page = Page.objects.get(pk=page_id)
                property_type = PropertyType.objects.get(type_name="Webmark")
                property = PageProperty.objects.create(
                    page_parent=page,
                    property_type=property_type,
                    property_name="Bibliography",
                )
                # Create the webmark property
                webmark = WebmarkProperty(
                    page_property=property,
                    page=page,
                    webmark_name=form.cleaned_data["webmark_name"],
                    webmark_url=form.cleaned_data["webmark_url"],
                )
                webmark.save()
                return redirect(
                    reverse("a01_note:page-detail", kwargs={"pk": page_id})
                )
        else:
            form = WebmarkFormSet

        context = {
            "form": form,
            "page": Page.objects.get(pk=page_id),
            "web_title": "Bibliography | add",
            "page_title": "Add your bibliography",
            "sidebar_data": fetch_sidebar_data(request.user),
        }
        return render(request, "a01_note/webmark_property_form.html", context)
    else:
        raise PermissionDenied


class WebmarkPropertyUpdate(
    LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    redirect_field_name = None

    model = WebmarkProperty
    form_class = modelform_factory(
        WebmarkProperty,
        form=WebmarkPropertyModelForm,
        fields=(
            "webmark_name",
            "webmark_url",
        ),
    )
    template_name = "a01_note/webmark_property_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_title"] = "Bibliography | edit"
        context["page_title"] = "Edit your bibliography"
        context["page"] = self.object.page  # For breadcrumb and go back
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_success_url(self):
        return reverse_lazy(
            "a01_note:page-detail", kwargs={"pk": self.object.page.id}
        )

    def test_func(self):
        webmark = WebmarkProperty.objects.get(pk=self.kwargs["pk"])
        return validate_page_owner(webmark.page.id, self.request.user)


@login_required(redirect_field_name=None)
def WebmarkPropertyDelete(request, pk):
    webmark = WebmarkProperty.objects.get(pk=pk)
    page_id = webmark.page.id

    if validate_page_owner(page_id, request.user):
        PageProperty.objects.get(webmarkproperty=webmark).delete()
        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page_id})
        )
    else:
        raise PermissionDenied


####---- Page summary ------------------------------
@login_required(redirect_field_name=None)
def PageSummaryCreate(request, page_id):
    if validate_page_owner(page_id, request.user):
        # TODO: Use a form and a standalone template if its required

        if request.method == "POST":
            page = Page.objects.get(pk=page_id)
            summary_type = request.POST.get("summary_type", None)

            if summary_type == "0":  # [("0", "Disease")]
                Summary.objects.create(page=page, summary_type=summary_type)

        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page_id})
        )
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def PageSummaryDelete(request, pk):
    summary_instance = Summary.objects.get(pk=pk)
    page_id = summary_instance.page.id

    if validate_page_owner(page_id, request.user):
        summary_instance.delete()
        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page_id})
        )
    else:
        raise PermissionDenied


####---- Page summary item ------------------------------
@login_required(redirect_field_name=None)
def DiseaseSummaryUpsert(request, summary_id):
    """Create or update a disease summary item

    UPDATE:
        Given that a One to One (O2O) relationship is used
        between Disease and Summary models.
    CREATE:
        If there is not a related Disease Summary instance.
    """

    summary_instance = Summary.objects.get(pk=summary_id)

    if validate_page_owner(summary_instance.page.id, request.user):
        context = {}

        # Retrieve disease summary's data for being updated
        # and populate the form with it.
        if hasattr(summary_instance, "disease"):
            disease_instance = Disease.objects.get(summary=summary_instance)
            cie10_instance = disease_instance.cie10
            symptom_list = disease_instance.symptom.all()
            drug_list = disease_instance.drug.all()
            symptom_id_list = ",".join(
                [str(symptom_instance.id) for symptom_instance in symptom_list]
            )
            drug_id_list = ",".join(
                [str(drug_instance.id) for drug_instance in drug_list]
            )
            page_title = f"Disease ─ {cie10_instance.code}"

            form = DiseaseSummaryForm(
                request.POST or None, instance=disease_instance
            )
            context.update(
                {
                    "page_title": page_title,
                    "disease": disease_instance,
                    "cie10": cie10_instance,
                    "symptom_list": symptom_list,
                    "drug_list": drug_list,
                    "symptom_id_list": symptom_id_list,
                    "drug_id_list": drug_id_list,
                }
            )
        # Instantiate a new disease summary form
        else:
            form = DiseaseSummaryForm(request.POST or None)
            context.update({"page_title": "Add your disease summary"})

        # Validate the form for being created or updated
        if request.method == "POST":
            # Validate Cie10's form data
            cie10_id = request.POST.get("cie10", None)
            if cie10_id:

                if form.is_valid():
                    cie10_instance = Cie10.objects.get(pk=cie10_id)

                    disease_instance = form.save(commit=False)
                    disease_instance.cie10 = cie10_instance
                    # Only set related summary during creation
                    if hasattr(summary_instance, "disease") == False:
                        disease_instance.summary = summary_instance
                    disease_instance.save()
                    form.save_m2m()

                    # Add Disease's symptoms
                    symptom_id_list = request.POST.get("symptom", None)
                    if symptom_id_list:
                        symptom_id_list = symptom_id_list.split(",")
                        for symptom_id in symptom_id_list:
                            symptom_instance = Symptom.objects.get(
                                pk=symptom_id
                            )
                            disease_instance.symptom.add(symptom_instance)

                    # Add Disease's drugs
                    drug_id_list = request.POST.get("drug", None)
                    if drug_id_list:
                        drug_id_list = drug_id_list.split(",")
                        for drug_id in drug_id_list:
                            drug_instance = Drug.objects.get(pk=drug_id)
                            disease_instance.drug.add(drug_instance)

                    return redirect(
                        reverse(
                            "a01_note:page-detail",
                            kwargs={"pk": summary_instance.page.id},
                        )
                    )
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Oh! There was an error saving the form. Please try again.",
                        extra_tags="disease_summary_error",
                    )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Oh! There was an error. Please choose a valid CIE-10 code.",
                    extra_tags="disease_summary_error",
                )

        context.update(
            {
                "form": form,
                "page": summary_instance.page,
                "web_title": "Disease Summary | Add & Edit",
                "sidebar_data": fetch_sidebar_data(request.user),
            }
        )
        return render(request, "a01_note/disease_summary_form.html", context)
    else:
        raise PermissionDenied


####---- Page index's content ------------------------------
# Manage the list of page's contents (set the order and type)
@login_required(redirect_field_name=None)
def BlockIndexCreate(request, page_id):
    if validate_page_owner(page_id, request.user):
        # BlockIndexForm = modelform_factory(BlockIndex, form=BlockIndexModelForm, exclude=('page',))
        BlockIndexForm = modelform_factory(
            BlockIndex, form=BlockIndexModelForm, fields=("blocktype",)
        )

        if request.method == "POST":
            formset = BlockIndexForm(request.POST)
            if formset.is_valid():
                page = Page.objects.get(pk=page_id)
                block = BlockIndex(
                    page=page,
                    blocktype=formset.cleaned_data["blocktype"],
                    # row 			= formset.cleaned_data['row'],					# FIXME: Row, column and column_length must be set automatically
                    # column 			= formset.cleaned_data['column'],
                    # column_length 	= formset.cleaned_data['column_length'],
                )
                block.save()
                return redirect(
                    reverse("a01_note:page-detail", kwargs={"pk": page_id})
                )
        else:
            formset = BlockIndexForm

        context = {
            "formset": formset,
            "page": Page.objects.get(pk=page_id),  # for going BACK
            "web_title": "Content type | add",
            "page_title": "Choose a content type",
            "sidebar_data": fetch_sidebar_data(request.user),
        }
        return render(request, "a01_note/block_index_create.html", context)
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def BlockIndexDelete(request, pk):
    blockindex = BlockIndex.objects.get(pk=pk)
    page_id = blockindex.page.id

    if validate_page_owner(page_id, request.user):
        blockindex.delete()
        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page_id})
        )
    else:
        raise PermissionDenied


####---- Page content ------------------------------
# Create and Update page's TEXT content
@login_required(redirect_field_name=None)
def TextContentCreateUpdate(request, blockindex_id, page_id):
    if validate_page_owner(page_id, request.user):
        TextFormSet = modelform_factory(
            TextContent, form=TextContentModelForm, fields=("content_text",)
        )
        block = BlockIndex.objects.get(pk=blockindex_id)

        if hasattr(
            block, "textcontent"
        ):  # UPDATE text content (Only work due to the OneToOne relationships [textcontent - blockindex])
            text_instance = TextContent.objects.get(blockindex=blockindex_id)
            formset = TextFormSet(request.POST or None, instance=text_instance)

            if formset.is_valid():
                formset.save()
                return redirect(
                    reverse("a01_note:page-detail", kwargs={"pk": page_id})
                )
        else:  # INSERT text content
            if request.method == "POST":
                formset = TextFormSet(request.POST)

                if formset.is_valid():
                    page = Page.objects.get(pk=page_id)
                    text = TextContent(
                        page=page,
                        blockindex=block,
                        content_text=formset.cleaned_data["content_text"],
                    )
                    text.save()
                    return redirect(
                        reverse("a01_note:page-detail", kwargs={"pk": page_id})
                    )
            else:
                formset = TextFormSet

        context = {
            "formset": formset,
            "page": Page.objects.get(
                pk=page_id
            ),  # Data added in order to go BACK inside the template
            "web_title": "Text content | add & edit",
            "page_title": "Add your text content",
            "sidebar_data": fetch_sidebar_data(
                request.user
            ),  # Data for populating the ASIDE template
        }
        return render(request, "a01_note/text_content_form.html", context)
    else:
        raise PermissionDenied


# Create and Update page's IMAGE content
@login_required(redirect_field_name=None)
def ImageContentCreateUpdate(request, blockindex_id, page_id):
    if validate_page_owner(page_id, request.user):
        ImageFormSet = modelform_factory(
            ImageContent, form=ImageContentModelForm, fields=("image_content",)
        )
        block = BlockIndex.objects.get(pk=blockindex_id)
        context = {}

        if hasattr(block, "imagecontent"):  # UPDATE image content
            image_instance = ImageContent.objects.get(blockindex=blockindex_id)

            if request.method == "POST":
                formset = ImageFormSet(
                    request.POST, request.FILES, instance=image_instance
                )

                if formset.is_valid():
                    formset.save()
                    return redirect(
                        reverse("a01_note:page-detail", kwargs={"pk": page_id})
                    )
            else:
                formset = ImageFormSet(instance=image_instance)
                context[
                    "image_url"
                ] = (
                    image_instance.image_content.url
                )  # Path sent in order to show the image inside the form

        else:  # INSERT image content
            if request.method == "POST":
                formset = ImageFormSet(request.POST, request.FILES)

                if formset.is_valid():
                    page = Page.objects.get(pk=page_id)
                    image = ImageContent(
                        page=page,
                        blockindex=block,
                        image_content=formset.cleaned_data["image_content"],
                    )
                    image.save()
                    return redirect(
                        reverse("a01_note:page-detail", kwargs={"pk": page_id})
                    )
            else:
                formset = ImageFormSet

        context["formset"] = formset
        context["page"] = Page.objects.get(
            pk=page_id
        )  # Data added in order to go BACK inside the template
        context["web_title"] = "Image content | add & edit"
        context["page_title"] = "Add your image content"
        context["sidebar_data"] = fetch_sidebar_data(
            request.user
        )  # Data for populating the ASIDE template
        return render(request, "a01_note/image_content_form.html", context)
    else:
        raise PermissionDenied


# Create and Update page's FILE content
@login_required(redirect_field_name=None)
def FileContentCreateUpdate(request, blockindex_id, page_id):
    if validate_page_owner(page_id, request.user):
        FileFormSet = modelform_factory(
            FileContent, form=FileContentModelForm, fields=("file_content",)
        )
        block = BlockIndex.objects.get(pk=blockindex_id)
        context = {}

        if hasattr(block, "filecontent"):  # UPDATE file content
            file_instance = FileContent.objects.get(blockindex=blockindex_id)

            if request.method == "POST":
                formset = FileFormSet(
                    request.POST, request.FILES, instance=file_instance
                )

                if formset.is_valid():
                    formset.save()
                    return redirect(
                        reverse("a01_note:page-detail", kwargs={"pk": page_id})
                    )
            else:
                formset = FileFormSet(instance=file_instance)
                context["file_url"] = file_instance.file_content.url

        else:  # INSERT file content
            if request.method == "POST":
                formset = FileFormSet(request.POST, request.FILES)

                if formset.is_valid():
                    page = Page.objects.get(pk=page_id)
                    file = FileContent(
                        page=page,
                        blockindex=block,
                        file_content=formset.cleaned_data["file_content"],
                    )
                    file.save()
                    return redirect(
                        reverse("a01_note:page-detail", kwargs={"pk": page_id})
                    )
            else:
                formset = FileFormSet

        context["formset"] = formset
        context["page"] = Page.objects.get(pk=page_id)
        context["web_title"] = "File content | add & edit"
        context["page_title"] = "Add your file content"
        context["sidebar_data"] = fetch_sidebar_data(
            request.user
        )  # Data for populating the ASIDE template
        return render(request, "a01_note/file_content_form.html", context)
    else:
        raise PermissionDenied


# Create and Update page's WEBMARK content
@login_required(redirect_field_name=None)
def WebmarkContentCreateUpdate(request, blockindex_id, page_id):
    if validate_page_owner(page_id, request.user):
        WebmarkFormSet = modelform_factory(
            WebmarkContent,
            form=WebmarkContentModelForm,
            fields=("url_content",),
        )
        block = BlockIndex.objects.get(pk=blockindex_id)

        if hasattr(block, "webmarkcontent"):  # UPDATE file content
            webmark_instance = WebmarkContent.objects.get(
                blockindex=blockindex_id
            )
            formset = WebmarkFormSet(
                request.POST or None, instance=webmark_instance
            )

            if formset.is_valid():
                formset.save()
                return redirect(
                    reverse("a01_note:page-detail", kwargs={"pk": page_id})
                )
        else:  # INSERT file content
            if request.method == "POST":
                formset = WebmarkFormSet(request.POST)

                if formset.is_valid():
                    page = Page.objects.get(pk=page_id)
                    webmark = WebmarkContent(
                        page=page,
                        blockindex=block,
                        url_content=formset.cleaned_data["url_content"],
                    )
                    webmark.save()
                    return redirect(
                        reverse("a01_note:page-detail", kwargs={"pk": page_id})
                    )
            else:
                formset = WebmarkFormSet

        context = {
            "formset": formset,
            "page": Page.objects.get(pk=page_id),
            "web_title": "Webmark content | add & edit",
            "page_title": "Add your webmark content",
            "sidebar_data": fetch_sidebar_data(
                request.user
            ),  # Data for populating the ASIDE template
        }
        return render(request, "a01_note/webmark_content_form.html", context)
    else:
        raise PermissionDenied


####---- Page children ------------------------------
# Create a child page (its field are gonna change acording to the page parent)
@login_required(redirect_field_name=None)
def ChildPageCreate(request, page_id):
    if validate_page_owner(page_id, request.user):
        ChildPageForm = modelform_factory(
            Page,
            form=PageModelForm,
            fields=(
                "page_name",
                "description",
                "emoji",
                "cover",
                "hex_color",
                "is_favourite",
            ),
        )
        submitted = False

        if request.method == "POST":
            formset = ChildPageForm(request.POST)
            if formset.is_valid():
                page = Page.objects.get(pk=page_id)
                child = Page(  # FIXME: Try to use commit=False for setting new model fields
                    page_parent=page,
                    owner=request.user,
                    page_name=formset.cleaned_data["page_name"],
                    description=formset.cleaned_data["description"],
                    emoji=formset.cleaned_data["emoji"],
                    cover=formset.cleaned_data["cover"],
                    hex_color=formset.cleaned_data["hex_color"],
                    is_favourite=formset.cleaned_data["is_favourite"],
                    level=(page.level + 1),
                    page_role="1",  # {'0': 'Folder', '1': 'Note', '2': 'Folder and Note'}	# FIXME: Evaluate and set the right page_role
                )
                child.save()
                child.sharing_code = generate_object_code(child.id)
                child.save()

                return redirect(
                    reverse("a01_note:page-detail", kwargs={"pk": child.id})
                )
        else:
            formset = ChildPageForm

        context = {
            "formset": formset,
            "submitted": submitted,
            "web_title": "Add child pages | new",
            "page_title": "Add a child page",
            "sidebar_data": fetch_sidebar_data(
                request.user
            ),  # Data for populating the ASIDE template
        }
        return render(request, "a01_note/page_create_form.html", context)
    else:
        raise PermissionDenied


####---- Page community ------------------------------
class PageCommunity(LoginRequiredMixin, ListView):
    # Show shared pages to whoever authenticated user
    redirect_field_name = None

    model = Page
    template_name = "a01_note/page_community.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web_title"] = "Page community | App Notes"
        context["page_title"] = "Page community"
        context["sidebar_data"] = fetch_sidebar_data(self.request.user)
        return context

    def get_queryset(self):
        return Page.objects.filter(
            Q(in_trash=False) & Q(is_shared=True)
        ).order_by("page_name")


@login_required(redirect_field_name=None)
def PageShare(request, pk):
    page = Page.objects.get(pk=pk)

    if validate_page_owner(pk, request.user):
        if request.method == "POST":
            PageForm = modelform_factory(Page, fields=("is_shared",))
            form = PageForm(request.POST, instance=page)

            if form.is_valid():
                page_obj = form.save(commit=False)

                if page_obj.is_shared == True:
                    page_obj.sharing_permission = "0"  # [ ('0', 'viewer'), ('1', 'commenter'), ('2', 'editor'), ]
                else:
                    page_obj.sharing_permission = None

                page_obj.save()

        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page.id})
        )
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def PageInvite(request, pk):
    page = Page.objects.get(pk=pk)

    if validate_page_owner(pk, request.user):
        if request.method == "POST":

            if request.POST["username"] is not None:
                username = request.POST["username"]

                try:
                    user = User.objects.get(username=username)

                    # Share the current page excluding its own user
                    if user != request.user:
                        access_qs = Access.objects.filter(
                            Q(page=page) & Q(user=user)
                        ).count()

                        if access_qs == 1:
                            messages.add_message(
                                request,
                                messages.ERROR,
                                f"Oh! The current page has already been shared with @{username}",
                                extra_tags="invite_user_error",
                            )
                        elif access_qs == 0:
                            Access.objects.create(
                                page=page,
                                user=user,
                                permission="0",  # [ ('0', 'viewer'), ('1', 'commenter'), ('2', 'editor'), ]
                            )
                            messages.add_message(
                                request,
                                messages.SUCCESS,
                                f"Done! The current page was successfully shared with @{username}",
                                extra_tags="invite_user_success",
                            )

                except User.DoesNotExist:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Oh! There isn't any user called @{username}",
                        extra_tags="invite_user_error",
                    )

        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page.id})
        )
    else:
        raise PermissionDenied


@login_required(redirect_field_name=None)
def PageGuestDelete(request, pk, user_id):
    page = Page.objects.get(pk=pk)
    user = User.objects.get(pk=user_id)

    if validate_page_owner(pk, request.user):
        access_qs = Access.objects.filter(Q(page=page) & Q(user=user))

        if access_qs.count() == 1:
            access_qs.first().delete()
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Done! @{user.get_username()} was successfully remove from page's guests.",
                extra_tags="remove_pageguest_success",
            )

        return redirect(
            reverse("a01_note:page-detail", kwargs={"pk": page.id})
        )

    else:
        raise PermissionDenied


def PageAccess(request, sharing_code):
    page = get_object_or_404(Page, sharing_code=sharing_code)
    page_access = validate_page_access(page.id, request.user)

    if page_access["has_access"] == True:

        if page_access["user_access"]["role"] == "anonymous":
            return HttpResponse(
                f"<br><h1 style='color: #6c757d;'>ANONYMOUS</h1><p>Page in progess : )</p> "
            )
        elif page_access["user_access"]["role"] is not None:
            return redirect(
                reverse("a01_note:page-detail", kwargs={"pk": page.id})
            )
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


####---- API ------------------------------
# TODO: Use Django REST Framework for handling API views
def Cie10ApiList(request):
    # Some words (term, label and value) are key values
    # of jQuery-UI autocomplete plugin.
    key_word = request.GET.get("term")
    data = []

    cie10_list = Cie10.objects.filter(
        Q(code__icontains=key_word) | Q(description__icontains=key_word)
    )
    for cie10_instance in cie10_list:
        cie10_detail = f"{cie10_instance.code} ─ {cie10_instance.description}"
        data.append(
            {
                "label": cie10_detail,
                "value": cie10_instance.id,
            }
        )
    requested_data = json.dumps(data)

    mimetype = "application/json"
    return HttpResponse(requested_data, mimetype)


def SymptomApiList(request):
    key_word = request.GET.get("term")
    data = []

    symptom_list = Symptom.objects.filter(description__icontains=key_word)
    for symptom_instance in symptom_list:
        data.append(
            {
                "label": symptom_instance.description,
                "value": symptom_instance.id,
            }
        )
    requested_data = json.dumps(data)

    mimetype = "application/json"
    return HttpResponse(requested_data, mimetype)


def DrugApiList(request):
    key_word = request.GET.get("term")
    data = []

    drug_list = Drug.objects.filter(name__icontains=key_word)
    for drug_instance in drug_list:
        drug_detail = "{} ({}) ─ {}".format(
            drug_instance.name,
            drug_instance.concentration,
            drug_instance.pharmaceutical_short_form,
        )
        data.append(
            {
                "label": drug_detail,
                "value": drug_instance.id,
            }
        )
    requested_data = json.dumps(data)

    mimetype = "application/json"
    return HttpResponse(requested_data, mimetype)


# return HttpResponse(f"Working perfectly ;D ...<br>")
# return HttpResponse(f"Working perfectly ;D ...<br> {text}")
# return HttpResponse(f"ERROR: {formset.errors}")
# return HttpResponse(f"Working perfectly ;D ...<br>")
# print(f"🐝️🐝️🐝️ {} 🐝️🐝️🐝️")
