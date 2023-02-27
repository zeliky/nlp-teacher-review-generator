import json



import six
from google.cloud import translate_v2 as translate





def fix_data():
    replaced = []
    subjects_list = ["Art", "Literacy", "Music", "Math", "Dance", "Science", "Technology", "sports"]
    length = len(subjects_list)
    with open('recomendations.json', 'r') as json_file:
        reco_list = json.load(json_file)
        for idx, d in enumerate(reco_list):
            i= idx % length
            d["subject"] = subjects_list[i]
        replaced.append(d)
    return replaced


def translate_generated_texts(source_filename, key):
    res = []
    prompts_filename = "tra.jsonl"
    with open(source_filename, 'r') as json_file:
        data_list = json.load(json_file)
        for idx, d in enumerate(data_list):
            d[key + '-he'] = translate(d[key])
            res.append(d)
    return res


def translate(text, target='he'):
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    result = translate_client.translate(text, target_language=target)
    return result['translatedText']




def build_translations():
    translation_filename = "data/translation.jsonl"
    with open(translation_filename, 'a') as out_file:
        out_file.write("[")
        """
        with open("reviews-from-gpt3.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                d['translated'] = translate(d['review'])
                out_file.write("%s,\n" % d)
            out_file.write("]")
        
        with open("recommendation.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                d['translated'] = translate(d['recommendation'])
                out_file.write("%s,\n" % d)        
        with open("imprevements.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                d['translated'] = translate(d['review'])
                out_file.write("%s,\n" % d)
        """
        with open("data/quotes.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                d['translated'] = translate(d['ending'])
                out_file.write("%s,\n" % d)

def build_prompts():
    prompts_filename = "data/review-prompts.jsonl"
    with open(prompts_filename, 'w') as out_file:
        with open("data/reviews-from-gpt3.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                out_file.write('{"prompt": "write TRFD opening for %s ->", "completion": " %s"}\n' % (d['mtbi'], d['review']))
        with open("data/recommendation.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                out_file.write('{"prompt": "write TRFD praise for %s in %s ->", "completion": " %s"}\n' % (d['mtbi'], d['subject'],d['recommendation']))
        with open("data/imprevements.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                out_file.write('{"prompt": "write TRFD improvement for %s is %s ->", "completion": " %s"}\n' % (d['mtbi'],d['subject'] , d['review']))
        with open("data/quotes.json", 'r') as json_file:
            data_list = json.load(json_file)
            for idx, d in enumerate(data_list):
                out_file.write('{"prompt": "write TRFD quote for %s ->", "completion": " %s"}\n' % (d['mtbi'],d['ending']))

# print(json.dumps(replaced, indent=1))


build_translations()

#print(json.dumps(translated, indent=1))
#build_prompts()

#openai.finetune
