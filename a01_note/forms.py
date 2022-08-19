from django import forms
from django.forms import ModelForm

from .models import (
    BlockIndex,
    Disease,
    FileContent,
    ImageContent,
    Page,
    PageProperty,
    Tag,
    TextContent,
    TransmissionMode,
    WebmarkContent,
    WebmarkProperty,
)


####---- Page ------------------------------
class PageModelForm(ModelForm):
    class Meta:
        model = Page
        fields = [
            "page_parent",
            "page_name",
            "description",
            "level",
            "page_role",
            "emoji",
            "cover",
            "hex_color",
            "is_favourite",
            "in_trash",
            "moved_trash_at",
        ]
        labels = {
            "page_name": "Nombre",
            "description": "Page description",
            "emoji": "Emoji",
            "cover": "Cover",
            "hex_color": "Background color",
            "is_favourite": "Favourite",
            "in_trash": "Move to trash",
        }
        widgets = {
            "page_name": forms.TextInput(
                attrs={
                    "class": "form-control bg-transparent border-0 fs-2 text-muted",
                    "placeholder": "Untitled",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Add a short description...",
                }
            ),
            "page_role": forms.Select(attrs={"is_hidden": True}),
            "emoji": forms.TextInput(
                attrs={
                    "class": "form-control emojiPicker",
                    "placeholder": "Add your emoji...",
                }
            ),
            "cover": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Add a image...",
                }
            ),
            "hex_color": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                    "title": "Choose your color",
                }
            ),
            "is_favourite": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        help_texts = {
            "emoji": "Add a emoji",
            "description": "Add your description",
            "cover": "Add a cover",
            "hex_color": "Set your background color",
            "is_favourite": "Is your favourite page?",
        }
        error_messages = {
            "page_name": {
                "max_length": "This name is too long...😬️",
            },
            "description": {
                "max_length": "It seems to be longer than expected...😬️"
            },
        }


####---- Page property ------------------------------
class PagePropertyForm(ModelForm):
    class Meta:
        model = PageProperty
        fields = "__all__"
        widgets = {
            "page_parent": forms.Select(
                attrs={"class": "form-control", "placeholder": "Page..."}
            ),
            "property_type": forms.Select(
                attrs={"class": "form-control", "placeholder": "Type..."}
            ),
            "property_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Property name...",
                }
            ),
            "order_number": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "A order number...",
                }
            ),
        }


class TagPropertyForm(ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"
        widgets = {
            "page_property": forms.Select(
                attrs={"class": "form-control", "placeholder": "Property..."}
            ),
            "pages": forms.SelectMultiple(
                attrs={"class": "form-control", "placeholder": "Pages..."}
            ),
            "tag_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your tag..."}
            ),
        }


class WebmarkPropertyModelForm(ModelForm):
    class Meta:
        model = WebmarkProperty
        fields = "__all__"
        widgets = {
            "page_property": forms.Select(
                attrs={"class": "form-control", "placeholder": "Property..."}
            ),
            "page": forms.SelectMultiple(
                attrs={"class": "form-control", "placeholder": "Pages..."}
            ),
            "webmark_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Webmark name...",
                }
            ),
            "webmark_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.example.com",
                }
            ),
        }


####---- Page content ------------------------------
class BlockIndexModelForm(ModelForm):
    class Meta:
        model = BlockIndex
        fields = "__all__"
        widgets = {
            "page": forms.Select(
                attrs={"class": "form-control", "placeholder": "Page..."}
            ),
            "blocktype": forms.Select(
                attrs={"class": "form-control", "placeholder": "Block type..."}
            ),
            "row": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Row..."}
            ),
            "column": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Column..."}
            ),
            "column_length": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Column length...",
                }
            ),
        }


class TextContentModelForm(ModelForm):
    class Meta:
        model = TextContent
        fields = ["page", "blockindex", "content_text"]
        widgets = {
            "page": forms.Select(
                attrs={"class": "form-control", "placeholder": "Page..."}
            ),
            "blockindex": forms.Select(
                attrs={"class": "form-control", "placeholder": "Block..."}
            ),
            "content_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Text content...",
                }
            ),
        }


class ImageContentModelForm(ModelForm):
    class Meta:
        model = ImageContent
        fields = "__all__"
        widgets = {
            "page": forms.Select(
                attrs={"class": "form-control", "placeholder": "Page..."}
            ),
            "blockindex": forms.Select(
                attrs={"class": "form-control", "placeholder": "Block..."}
            ),
            "image_content": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Image content...",
                }
            ),
        }


class FileContentModelForm(ModelForm):
    class Meta:
        model = FileContent
        fields = "__all__"
        widgets = {
            "page": forms.Select(
                attrs={"class": "form-control", "placeholder": "Page..."}
            ),
            "blockindex": forms.Select(
                attrs={"class": "form-control", "placeholder": "Block..."}
            ),
            "file_content": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "File content...",
                }
            ),
        }


class WebmarkContentModelForm(ModelForm):
    class Meta:
        model = WebmarkContent
        fields = "__all__"
        widgets = {
            "page": forms.Select(
                attrs={"class": "form-control", "placeholder": "Page..."}
            ),
            "blockindex": forms.Select(
                attrs={"class": "form-control", "placeholder": "Block..."}
            ),
            "url_content": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.example.com",
                }
            ),
        }


####---- Page summary ------------------------------
class DiseaseSummaryForm(ModelForm):
    # Given that some related models (cie10, symptom and drug) have
    # more than 100 instances, they should be rendered and loaded
    # using external scripts.

    transmissionmode = forms.ModelMultipleChoiceField(
        queryset=TransmissionMode.objects.all(),
        required=False,
        label="Transmission mode",
        widget=forms.SelectMultiple(
            attrs={"class": "form-control"},
        ),
    )

    class Meta:
        model = Disease
        fields = [
            "transmissionmode",
            "cause",
            "diagnostic",
            "risk_factor",
            "prevention",
            "min_age",
            "max_age",
            "sex",
        ]
        widgets = {
            "cause": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Cause...",
                }
            ),
            "diagnostic": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Diagnostic..."}
            ),
            "risk_factor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Risk factor...",
                }
            ),
            "prevention": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Prevention...",
                }
            ),
            "min_age": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "max_age": forms.NumberInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "sex": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }
