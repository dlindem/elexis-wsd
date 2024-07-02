import re

with open('corpora/elexis-wsd-sl_corpus.conllu') as conll_file:
    conll_lines = conll_file.read()
    conll_sentences = conll_lines.split('# text = ')
    conll_sentences.pop(0)

sentence_count = 0
for sentence in conll_sentences:
    sentence_count += 1
    sentence_sections = sentence.split('# sent_id = ')
    sentence_text = sentence_sections[0][:-1]
    sentence_info = re.search(r'^([0-9]+)\.([a-z]+)', sentence_sections[1])
    sentence_number = sentence_info.group(1)
    sentence_langcode = sentence_info.group(2)
    print(f"\n[{sentence_count}] Now processessing sentence #{sentence_number} in language '{sentence_langcode}': '{sentence_text}'")
    for line in sentence_sections[1].split('\n'):
        if re.search(r'^[0-9]+\t', line):
            columns = line.split('\t')
            tokendata = {
                'nr': columns[0],
                'form': columns[1],
                'lemma': columns[2],
                'upos': columns[3],
                'annotations': columns[9].split('|')
            }
            print(tokendata)

