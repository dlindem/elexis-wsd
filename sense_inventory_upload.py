import csv, re, json
import mappings

# from wikibaseintegrator import wbi_login, WikibaseIntegrator
from wikibaseintegrator.datatypes.string import String
# from wikibaseintegrator.datatypes.externalid import ExternalID
# from wikibaseintegrator.datatypes.item import Item
# from wikibaseintegrator.datatypes.monolingualtext import MonolingualText
# from wikibaseintegrator.datatypes.time import Time
# from wikibaseintegrator.datatypes.globecoordinate import GlobeCoordinate
# from wikibaseintegrator.datatypes.url import URL
from wikibaseintegrator.models import Reference, References, Form, Sense
from wikibaseintegrator.entities import lexeme
# from wikibaseintegrator.wbi_config import config as wbi_config
# from wikibaseintegrator import wbi_helpers
# from wikibaseintegrator.wbi_enums import ActionIfExists, WikibaseSnakType
# from wikibaseintegrator.models.claims import Claims
# from wikibaseintegrator.models.qualifiers import Qualifiers


inventory_filename = 'sense_inventories/elexis-wsd-sl_sense-inventory.tsv'
language_wikicode = 'sl'


with open(inventory_filename) as tsvfile:
    senses_data = csv.DictReader(tsvfile, delimiter="\t")
    line_count = 0
    upload_data = {}

    for line in senses_data:
        line_count += 1
        print(f"\n[{line_count}] Now processing: {line}")
        if line['lemma'] not in upload_data:
            upload_data[line['lemma']] = {'upos': line['upos'], 'senses': {line['sense_id']: line}}
            print(f"Found new lemma '{line['lemma']}', added sense {line['sense_id']}")
        else:
            upload_data[line['lemma']]['senses'][line['sense_id']] = line
            print(f"Found repeated lemma '{line['lemma']}', added sense {line['sense_id']}")
    with open(inventory_filename.replace(".tsv", ".json"), 'w') as jsonfile:
        json.dump(upload_data, jsonfile, indent=2)
        print(f"Saved data to upload to JSON.")

    for lemma in upload_data: # TODO: what if same lemma different POS??

        wikibase_pos = mappings.upos_mapping[upload_data[lemma]['upos']]
        wikibase_language = mappings.lang_mapping[language_wikicode]
        newlexeme = lexeme(lexical_category=wikibase_pos, language=wikibase_language)

        newlexeme.lemmas.set(language=language_wikicode, value=lemma)
        claim = String(prop_nr='P6', value="TODO") # TODO: lemma ID??
        newlexeme.claims.add(claim)
        for sense_id in upload_data[lemma]:
            newsense = Sense()
            newsense.glosses.set(language=language_wikicode, value=upload_data[lemma][sense_id]['definition'])
            claim = String(prop_nr='P6', value=sense_id)
            newsense.claims.add(claim)
            newlexeme.add(newsense)

        print(lexeme.get_json)








