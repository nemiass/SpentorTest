"""Useful script for working on background settings.

Almost all current script should be executed from the 
default Django's pythton shell. For example:

>>> python3 manage.py shell
>>> ...

Besides, given that each script is standalone, set
yours preferences and executed them one by one.
"""

"""Set default data for page's sharing_code."""
from a01_note.models import Page
from a01_note.views import generate_object_code

page_list = Page.objects.all()

for page in page_list:
    page.sharing_code = generate_object_code(page.id)
    page.save()
    print(f"{page.sharing_code} - {page.page_name}")


"""Set name for basic decks."""
from evaluation.models import Deck

deck_list = Deck.objects.filter(
    type="0"
)  # [('0', 'Basic'), ('1', 'Customized'),]

for deck in deck_list:
    deck.deck_name = f"{deck.page}'s deck"
    deck.save()
    print(f"{deck.deck_name}")

print(f"{deck_list.count()} decks were affected")


from a01_note.views import generate_object_code


"""Set default data for deck's sharing_code."""
from evaluation.models import Deck

deck_list = Deck.objects.all()

for deck in deck_list:
    deck.sharing_code = generate_object_code(deck.id)
    deck.save()
    print(f"{deck.sharing_code} - {deck.deck_name}")

print(f"{deck_list.count()} decks were affected")


"""Set default sharing_permission for shared decks (is_shared=True)."""
from evaluation.models import Deck

shared_decks = Deck.objects.filter(is_shared=True)

for deck in shared_decks:
    deck.sharing_permission = (
        "0"  # [ ('0', 'viewer'), ('1', 'commenter'), ('2', 'editor'), ]
    )
    deck.save()
    print(f"{deck.sharing_permission} - {deck.deck_name}")

print(f"{shared_decks.count()} decks were affected")


"""Set is_shared field to False for all created deck."""
from evaluation.models import Deck

shared_deck_list = Deck.objects.filter(is_shared=True)

for deck in shared_deck_list:
    deck.is_shared = False
    deck.save()
    print(f"{deck.is_shared} - {deck.deck_name}")

print(f"{shared_deck_list.count()} decks were affected")


"""Add default data for page's disease summary

It involves adding pre-cleaned data for:
    - Cie10
        International Statistical Classification of Diseases 
        and Related Health Problems - 10th Revision
    - Symptom
        General symptoms for diseases
    - Drug
        Medicine for handling diseases
    - TransmissionMode
        Modes of disease transmission
"""

# Cie10 creation
import pandas as pd

from a01_note.models import Cie10

data_path = "data/cie10.csv"
cie10_dataset = pd.read_csv(data_path, dtype="str", keep_default_na=False)
dataframe_len = len(cie10_dataset)

for i in range(dataframe_len):
    cie10_item = cie10_dataset.iloc[i]
    code = cie10_item["code"]
    description = cie10_item["description"]
    cie10_instance = Cie10.objects.create(code=code, description=description)
    print(f"Done! {cie10_instance.id} - {cie10_instance.code}")

print(f"{dataframe_len} items were created")


# Symtom creation
import pandas as pd

from a01_note.models import Symptom

data_path = "data/symptom.csv"
symptom_dataset = pd.read_csv(data_path, dtype="str", keep_default_na=False)
dataframe_len = len(symptom_dataset)

for i in range(dataframe_len):
    symptom_item = symptom_dataset.iloc[i]
    description = symptom_item["description"]
    symptom_instance = Symptom.objects.create(description=description)
    print(f"Done! {symptom_instance.id}")

print(f"{dataframe_len} items were created")


# Drug creation
import pandas as pd

from a01_note.models import Drug

data_path = "data/drug.csv"
drug_dataset = pd.read_csv(data_path, dtype="str", keep_default_na=False)
dataframe_len = len(drug_dataset)

for i in range(dataframe_len):
    drug_item = drug_dataset.iloc[i]
    name = drug_item["name"]
    concentration = drug_item["concentration"]
    pharm_form = drug_item["pharmaceutical_form"]
    pharm_short_form = drug_item["pharmaceutical_short_form"]
    presentation = drug_item["presentation"]
    drug_instance = Drug.objects.create(
        name=name,
        concentration=concentration,
        pharmaceutical_form=pharm_form,
        pharmaceutical_short_form=pharm_short_form,
        presentation=presentation,
    )
    print(f"Done! {drug_instance.id}")

print(f"{dataframe_len} items were created")


# TransmissionMode creation
import pandas as pd

from a01_note.models import TransmissionMode

data_path = "data/transmissionmode.csv"
transmissionmode_dataset = pd.read_csv(
    data_path, dtype="str", keep_default_na=False
)
dataframe_len = len(transmissionmode_dataset)

for i in range(dataframe_len):
    transmissionmode_item = transmissionmode_dataset.iloc[i]
    description = transmissionmode_item["description"]
    contact = transmissionmode_item["contact"]
    transmissionmode_instance = TransmissionMode.objects.create(
        description=description,
        contact=contact,
    )
    print(f"Done! {transmissionmode_instance.id}")

print(f"{dataframe_len} items were created")


####---- DELETE test instances ------------------------------------------------
from evaluation.models import Deck, Card, Test

test_instance = Test.objects.get(id=63)
deck_instance = test_instance.deck
page = deck_instance.page

test_instance.delete()


# Update cards status
card_list = Card.objects.filter(deck=deck_instance)
card_list.update(status="0")

# UPdate deck fields satus
total_new_card = len(card_list)

deck_instance.new_card = total_new_card
deck_instance.learning_card = 0
deck_instance.review_card = 0
