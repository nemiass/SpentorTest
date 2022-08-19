from datetime import datetime

# from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models

####---- Page ------------------------------
DEFAULT_PERMISSION = "0"
PERMISSION_TYPE = [
    (DEFAULT_PERMISSION, "viewer"),
    ("1", "commenter"),
    ("2", "editor"),
]


class Page(models.Model):
    # Value for Field.choices
    ROLE_PARENT = "0"
    ROLE_CHILD = "1"
    ROLE_BOTH = "2"
    PAGE_ROLE = [
        (ROLE_PARENT, "Folder"),
        (ROLE_CHILD, "Note"),
        (ROLE_BOTH, "Folder and Note"),
    ]

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        date = datetime.now().strftime("%Y/%m/%d")
        return (
            f"user_{instance.owner.id}/page_property/images/{date}/{filename}"
        )

    # Relationship fields
    page_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="child_page",
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    # Own fields
    page_name = models.CharField(max_length=45)
    description = models.CharField(max_length=200, blank=True, null=True)
    level = models.IntegerField(default=0)
    page_role = models.CharField(
        max_length=1, choices=PAGE_ROLE, default=ROLE_PARENT
    )
    emoji = models.CharField(max_length=4, blank=True, null=True)
    cover = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True
    )
    hex_color = models.CharField(max_length=7, default="#0dcaf0")
    is_favourite = models.BooleanField(default=False)
    in_trash = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    moved_trash_at = models.DateTimeField(blank=True, null=True)

    guest_users = models.ManyToManyField(
        User,
        through="Access",
        through_fields=("page", "user"),
        related_name="shared_pages",
    )
    is_shared = models.BooleanField(default=False)
    sharing_permission = models.CharField(
        max_length=1, choices=PERMISSION_TYPE, blank=True, null=True
    )
    sharing_code = models.CharField(max_length=16, null=True)

    def __str__(self):
        return self.page_name


class Access(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(
        max_length=1, choices=PERMISSION_TYPE, default=DEFAULT_PERMISSION
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.page} - @{self.user} - {self.permission}"


####---- Page property ------------------------------
class PropertyType(models.Model):
    type_name = models.CharField(max_length=45)
    referenced_to = models.CharField(max_length=45)

    def __str__(self):
        return self.type_name


class PageProperty(models.Model):
    page_parent = models.ForeignKey("Page", on_delete=models.CASCADE)
    property_type = models.ForeignKey("PropertyType", on_delete=models.PROTECT)
    property_name = models.CharField(max_length=45)
    order_number = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.property_name


class Tag(models.Model):
    page_property = models.ForeignKey("PageProperty", on_delete=models.CASCADE)
    pages = models.ManyToManyField("Page")
    tag_name = models.CharField(max_length=45)

    def __str__(self):
        return self.tag_name


class WebmarkProperty(models.Model):
    page_property = models.OneToOneField(
        "PageProperty", on_delete=models.CASCADE
    )
    page = models.ForeignKey("Page", on_delete=models.CASCADE)
    webmark_name = models.CharField(max_length=100, blank=True, null=True)
    webmark_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.webmark_name


####---- Page content ------------------------------
class TextContent(models.Model):
    page = models.ForeignKey("Page", on_delete=models.CASCADE)
    blockindex = models.OneToOneField("BlockIndex", on_delete=models.CASCADE)
    # content_text 	= models.TextField(blank=True, null=True)
    # content_text 	= RichTextField(blank=True, null=True)
    content_text = RichTextUploadingField(
        blank=True, null=True, config_name="page_ckeditor"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.page}'s text"


class ImageContent(models.Model):
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/page_content/.../<filename>
        date = datetime.now().strftime("%Y/%m/%d")
        return f"user_{instance.page.owner.id}/page_content/images/{date}/{filename}"

    page = models.ForeignKey("Page", on_delete=models.CASCADE)
    blockindex = models.OneToOneField("BlockIndex", on_delete=models.CASCADE)
    image_content = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True
    )

    def __str__(self):
        return self.image_content.name


class FileContent(models.Model):
    def user_directory_path(instance, filename):
        date = datetime.now().strftime("%Y/%m/%d")
        return f"user_{instance.page.owner.id}/page_content/files/{date}/{filename}"

    page = models.ForeignKey("Page", on_delete=models.CASCADE)
    blockindex = models.OneToOneField("BlockIndex", on_delete=models.CASCADE)
    file_content = models.FileField(
        upload_to=user_directory_path, blank=True, null=True
    )

    def __str_(self):
        return self.file_content


class WebmarkContent(models.Model):
    page = models.ForeignKey("Page", on_delete=models.CASCADE)
    blockindex = models.OneToOneField("BlockIndex", on_delete=models.CASCADE)
    url_content = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.url_content


####---- Page index's content ------------------------------
class BlockType(models.Model):
    type_name = models.CharField(max_length=45)
    referenced_to = models.CharField(max_length=45)

    def __str__(self):
        return self.type_name


class BlockIndex(models.Model):
    page = models.ForeignKey("Page", on_delete=models.CASCADE)
    blocktype = models.ForeignKey("BlockType", on_delete=models.PROTECT)
    row = models.PositiveSmallIntegerField(default=0)
    column = models.PositiveSmallIntegerField(default=0)
    column_length = models.PositiveSmallIntegerField(
        default=12
    )  # Based on Bootstrap column numbers (1-12)

    def __str__(self):
        return f"row-{self.row} col-{self.column} clen-{self.column_length}"


####---- Page's summary ------------------------------
class Summary(models.Model):
    SUMMARY_TYPE = [
        (None, "Choose a type"),
        ("0", "Disease"),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    summary_type = models.CharField(max_length=1, choices=SUMMARY_TYPE)
    # description = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary ({self.get_summary_type_display()}): {self.page}"


class Cie10(models.Model):
    code = models.CharField(max_length=8)
    description = models.CharField(max_length=254)

    def __str__(self):
        return self.code


class Symptom(models.Model):
    description = models.CharField(max_length=250)

    def __str__(self):
        return self.description


class Drug(models.Model):
    name = models.CharField(max_length=250)
    concentration = models.CharField(max_length=250)
    pharmaceutical_form = models.CharField(max_length=250)
    pharmaceutical_short_form = models.CharField(max_length=250)
    presentation = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name} ─ {self.concentration}"


class TransmissionMode(models.Model):
    CONTACT_TYPE = [
        ("D", "Direct"),
        ("I", "Indirect"),
    ]
    description = models.CharField(max_length=150)
    contact = models.CharField(max_length=1, choices=CONTACT_TYPE)

    def __str__(self):
        return self.description


class Disease(models.Model):
    SEX_TYPE = [
        (None, "Choose a related sex"),
        ("M", "Male"),
        ("F", "Female"),
        ("B", "Both male and female"),
    ]

    summary = models.OneToOneField(Summary, on_delete=models.CASCADE)
    cie10 = models.ForeignKey(Cie10, on_delete=models.PROTECT)
    symptom = models.ManyToManyField(Symptom)
    drug = models.ManyToManyField(Drug)
    transmissionmode = models.ManyToManyField(TransmissionMode)
    cause = models.CharField(max_length=250, blank=True, null=True)
    diagnostic = models.CharField(max_length=250, blank=True, null=True)
    risk_factor = models.CharField(max_length=250, blank=True, null=True)
    prevention = models.CharField(max_length=250, blank=True, null=True)
    # Disease constraints
    min_age = models.PositiveSmallIntegerField(default=0)
    max_age = models.PositiveSmallIntegerField(default=0)
    sex = models.CharField(max_length=1, choices=SEX_TYPE, default="B")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Disease ({self.cie10})"
