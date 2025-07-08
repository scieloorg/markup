import requests
from django.db import transaction
from markup_doc.models import CollectionValuesModel, JournalModel, CollectionModel

def sync_collection_from_api():
    url = "https://core.scielo.org/api/v2/pid/collection"
    all_results = []

    while url:
        response = requests.get(url, headers={"Accept": "application/json"})
        data = response.json()
        all_results.extend(data['results'])
        url = data['next']

    # Borra todo
    CollectionModel.objects.all().delete()
    deleted_count, _ = CollectionValuesModel.objects.all().delete()
    print(f">>> Se borraron {deleted_count} elementos de CollectionValuesModel")

    for item in all_results:
        acron = item.get('acron3')
        name = item.get('main_name', '').strip()
        if acron and name:
            CollectionValuesModel.objects.update_or_create(
                acron=acron,
                defaults={'name': name}
            )


def sync_journals_from_api():
    journals = JournalModel.objects.all()
    if journals.exists():
        deleted_count, _ = journals.delete()
        print(f"{deleted_count} registros eliminados.")
    else:
        print("No hay registros para eliminar.")


    obj = CollectionModel.objects.select_related('collection').first()

    acron_selected = obj.collection.acron if obj and obj.collection else None

    new_journals = []

    if acron_selected:

        url = "https://core.scielo.org/api/v2/pid/journal"

        while url:
            response = requests.get(url, headers={"Accept": "application/json"})
            try:
                data = response.json()

                for item in data["results"]:
                    title = item.get("title", None)
                    short_title = item.get("short_title", None)
                    acronym = item.get("acronym", None)
                    pissn = item.get("issn_print", None)
                    eissn = item.get("issn_electronic", None)
                    acronym = item.get("acronym", None)
                    pubname = item.get("publisher", [])
                    title_in_database = item.get("title_in_database", [])
                    title_nlm = None

                    if title_in_database:
                        for t in title_in_database:
                            if t.get("name", None) == 'MEDLINE':
                                title_nlm = t.get("title", None)

                    if pubname:
                        pubname = pubname[0].get("name", None)

                    scielo_journals = item.get("scielo_journal", [])

                    # Obtener la primera colección asociada, si existe
                    collection_acron = None
                    if scielo_journals:
                        collection_acron = scielo_journals[0].get("collection_acron")
                        issn_scielo = scielo_journals[0].get("issn_scielo", None)

                    if not title or acron_selected != collection_acron:
                        continue  # Saltar si falta el título

                    #collection_instance = None
                    #if collection_acron:
                    #    collection_instance, _ = CollectionModel.objects.get_or_create(
                    #        acron=collection_acron,
                    #        defaults={'name': collection_acron.upper()}
                    #    )

                    # Crear o actualizar el journal
                    print(title)
                    journal = JournalModel(
                        title=title,
                        short_title=short_title or None,
                        title_nlm = title_nlm or None,
                        acronym=acronym or None,
                        issn=issn_scielo or None,
                        pissn=pissn or None,
                        eissn=eissn or None,
                        pubname=pubname or None,
                    #    collection=collection_instance,
                    #    defaults={}
                    )
                    new_journals.append(journal)

                url = data.get("next")
            except:
                print('********************************ERROR')
                print(url)
                url = None

        # Guardar todo junto
        if new_journals:
            with transaction.atomic():
                JournalModel.objects.bulk_create(new_journals)
            print(f"{len(new_journals)} registros insertados.")
        else:
            print("No se encontraron registros válidos.")

