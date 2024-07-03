import csv, re, json, time
import mappings
import xwbi

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

inventory_filename = 'sense_inventories/elexis-wsd-en_sense-inventory.tsv'
language_wikicode = 'en'
try:
    with open(f'sense_inventories/{language_wikicode}-lexeme-mapping.csv', 'r') as mappingcsv:
        donelist = mappingcsv.read().split('\n')
        done_items = []
        for row in donelist:
            done_items.append(row.split('\t')[0])
except:
    done_items = []


with open(inventory_filename) as tsvfile:
    senses_data = csv.DictReader(tsvfile, delimiter="\t")
    line_count = 0
    upload_data = {}

    for line in senses_data:
        line_count += 1
        print(f"\n[{line_count}] Now processing: {line}")
        lempos = line['lemma']+'_'+line['upos']
        if lempos not in upload_data:
            upload_data[lempos] = {line['sense_id']: line}
            print(f"Found new lempos '{lempos}', added sense {line['sense_id']}")
        else:
            upload_data[lempos][line['sense_id']] = line
            print(f"Found repeated lempos '{lempos}', added sense {line['sense_id']}")
    with open(inventory_filename.replace(".tsv", ".json"), 'w') as jsonfile:
        json.dump(upload_data, jsonfile, indent=2)
        print(f"Saved data to upload to JSON.")

    count = 0
    for lempos in upload_data:
        count += 1
        print(f"\n[{count}] Now uploading {lempos}...")
        if lempos in done_items:
            print(f"{lempos} was done in a previous run, skipped.")
            continue
        lemma = lempos.split("_")[0]
        upos = lempos.split("_")[1]
        wikibase_pos = mappings.upos_mapping[upos]
        wikibase_language = mappings.lang_mapping[language_wikicode]
        newlexeme = xwbi.wbi.lexeme.new(lexical_category=wikibase_pos, language=wikibase_language)

        newlexeme.lemmas.set(language=language_wikicode, value=lemma)
        # claim = String(prop_nr='P7', value="TODO") # TODO: lemma ID??
        # newlexeme.claims.add(claim)
        for sense_id in upload_data[lempos]:
            print(sense_id)
            newsense = Sense()
            newsense.glosses.set(language=language_wikicode, value=upload_data[lempos][sense_id]['definition'])
            claim = String(prop_nr='P7', value=sense_id)
            newsense.claims.add(claim)
            newlexeme.senses.add(newsense)

        done = False
        while not done:
            try:
                newlexeme.write()
                done = True
                print("Upload successful.")
                time.sleep(0.2)
            except Exception as ex:
                if "404 Client Error" in str(ex):
                    print('Got 404 response from wikibase, will wait and try again...')
                    time.sleep(10)
                else:
                    print('Unexpected error:\n' + str(ex))
                    sys.exit()

        with open(f'sense_inventories/{language_wikicode}-lexeme-mapping.csv', 'a') as mappingcsv:
            mappingcsv.write(lempos + '\t' + newlexeme.id + '\n')
        print('Finished processing ' + newlexeme.id)












