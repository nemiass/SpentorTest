# 🔰️ Spentor Documentation

A basic guide file for understanting the whole web applicacition.

## Django's apps

- a01_note
- evaluation
- master

## Main core: a01_note

- Key words

  - page: mean a note file.
  - deck: set of questions related to a note file.
  - card: involve a short question and its answer.

- Main components
  > A page (note) could have the following components:
  - Property: such as title, description, etc.
  - Content: for instance, text, image, etc.
  - Deck: a set of questions related to the page.
  - Summary: a short summary of the page.
  - Subpage: many sub pages.

## Requirements

- [jQuery v3.6.0](https://jquery.com/)
- [Bootstrap v5.1.3](https://getbootstrap.com/)
- [Python v3.8.10](https://www.python.org/)
- [Django v4.0.2](https://www.djangoproject.com/)
- [Nice Admin - Free bootstrap admin HTML template](https://bootstrapmade.com/demo/NiceAdmin/)

## Resources

- [DB diagram](https://drive.google.com/file/d/1sMI2bGOroq_5_PMa5jLrvx0iDitgFUHm/view?usp=sharing)

## Installation

- Clone the repository.
- (optional) Set up a virtual environment.
- Install the requirements.
  - run `pip install -r requirements.txt` in the root directory.
- Create a database.
- Update app settings.
  - Update DB NAME, DB USER, DB PASSWORD in `settings.py`.
- Run the server.
  - run `python manage.py runserver` in the root directory.
- Visit the server.
  - Go to `http://localhost:8000/` in your browser.

## Working directory

```
  app_Notes
  ├── a01_note
  │   ├── admin.py
  │   ├── apps.py
  │   ├── forms.py
  │   ├── __init__.py
  │   ├── migrations
  │   ├── models.py
  │   ├── static
  │   │   └── a01_note
  │   │       ├── css
  │   │       │   └── my_style.css
  │   │       └── js
  │   │           └── my_script.js
  │   ├── templates
  │   │   └── a01_note
  │   │       ├── base.html
  │   │       ├── block_index_create.html
  │   │       ├── disease_summary_form.html
  │   │       ├── file_content_form.html
  │   │       ├── home.html
  │   │       ├── image_content_form.html
  │   │       ├── layout
  │   │       │   ├── modal_confirm_delete.html
  │   │       │   ├── modal_show_disease_summary.html
  │   │       │   ├── sidebar.html
  │   │       │   └── sidebar_page_item.html
  │   │       ├── page_community.html
  │   │       ├── page_create_form.html
  │   │       ├── page_detail.html
  │   │       ├── page_search.html
  │   │       ├── page_trash_list.html
  │   │       ├── page_update_form.html
  │   │       ├── property_create.html
  │   │       ├── property_update.html
  │   │       ├── tag_property_form.html
  │   │       ├── text_content_form.html
  │   │       ├── webmark_content_form.html
  │   │       └── webmark_property_form.html
  │   ├── tests.py
  │   ├── urls.py
  │   ├── utils.py
  │   └── views.py
  ├── annotations.py
  ├── app_Notes
  │   ├── asgi.py
  │   ├── __init__.py
  │   ├── settings.py
  │   ├── urls.py
  │   └── wsgi.py
  ├── data
  │   ├── cie10.csv
  │   ├── drug.csv
  │   ├── symptom.csv
  │   └── transmissionmode.csv
  ├── doc.md
  ├── evaluation
  │   ├── admin.py
  │   ├── apps.py
  │   ├── forms.py
  │   ├── __init__.py
  │   ├── migrations
  │   ├── models.py
  │   ├── static
  │   │   └── evaluation
  │   │       ├── css
  │   │       │   └── my_style.css
  │   │       └── js
  │   │           └── my_script.js
  │   ├── templates
  │   │   └── evaluation
  │   │       ├── card_form.html
  │   │       ├── deck_community.html
  │   │       ├── deck_detail.html
  │   │       ├── deck_form.html
  │   │       ├── deck_list.html
  │   │       ├── layout
  │   │       │   ├── cell_shared_deck_item.html
  │   │       │   ├── dropdown_deck_option.html
  │   │       │   ├── list_custom_deck_item.html
  │   │       │   ├── list_deck_item.html
  │   │       │   └── list_pined_deck_item.html
  │   │       ├── test_detail.html
  │   │       ├── test_list.html
  │   │       └── test_start.html
  │   ├── tests.py
  │   ├── urls.py
  │   └── views.py
  ├── manage.py
  ├── master
  │   ├── admin.py
  │   ├── apps.py
  │   ├── forms.py
  │   ├── __init__.py
  │   ├── migrations
  │   ├── models.py
  │   ├── templates
  │   │   └── master
  │   │       ├── base.html
  │   │       ├── login.html
  │   │       └── register.html
  │   ├── tests.py
  │   ├── urls.py
  │   └── views.py
  ├── pyproject.toml
  ├── README.md
  ├── static
  │   ├── css
  │   │   └── style.css
  │   ├── img
  │   ├── js
  │   │   └── main.js
  │   └── vendor
  │       ├── apexcharts
  │       ├── bootstrap
  │       ├── bootstrap-icons
  │       ├── boxicons
  │       ├── clipboard-js
  │       ├── emojione-area
  │       ├── jquery
  │       ├── jquery-ui-1.13.2
  │       ├── jquery-ui-1.13.2.BK
  │       ├── remixicon
  │       └── simple-datatables
  └── upload
```
