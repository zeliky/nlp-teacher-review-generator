from lib.review_generator import ReviewGenerator
from enums.request_enums import  ReviewRequest
from lib.fine_tune import  ModelFineTuner
import json


rg = ReviewGenerator(req=None)

limit =3

def extract_features_for_prompt(limit):
    i = 0
    with open("train_dataset.txt", 'r', encoding='utf-8-sig', newline='') as in_f:
        with open("features.jsonl", 'w', encoding='utf-8-sig', newline='') as out_f:
            for line in in_f:
                line = line.strip('\"')
                if len(line)< 50:
                    continue
                features = rg.extract_features(line)
                f_str = "Generate TRFD for:\n"
                for k,v in features.items():
                    f_str += "{}={},    ".format(k, v)
                prompt_line = {
                    "prompt": f_str,
                    "completion": line  + " END"
                }
                json.dump(prompt_line, out_f)
                out_f.write('\n')
                i +=1
                if i ==limit:
                    break

def extract_features(limit):
    i = 0
    with open("train_dataset.txt", 'r', encoding='utf-8-sig', newline='') as in_f:
        with open("features.json", 'w', encoding='utf-8-sig', newline='') as out_f:
            for line in in_f:
                line = line.strip('\"')
                if len(line)< 50:
                    continue
                features = rg.extract_features(line)
                data = {
                    "features": features,
                    "human_text": line
                }
                json.dump(data, out_f)
                out_f.write('\n')
                i +=1
                if i ==limit:
                    break

def generate_reviews_based_on_features(features):

    req = ReviewRequest(
        first_name=features['name'] if 'name' in features else '[name]',
        gender=features['gender']  if 'gender' in features else '[gender]',
        good_characteristic=features['characteristics']  if 'characteristics' in features else '',
        great_achievement=str(features['positive']) if 'positive' in features and features['positive'] != 'לא נמצא' else '',
        behavior_problem=str(features['negative']) if  'negative' in features and  features['negative'] != 'לא נמצא' else '',
        low_subject =""
    )



    rg = ReviewGenerator(req)
    result = rg.generate(1)
    print(result)
    return result

def generate_human_ai_comparison():
    with open("features.json", 'r', encoding='utf-8-sig', newline='') as in_f:
        with open("human-ai-texts.json", 'a', encoding='utf-8-sig', newline='') as out_f:
            for line in in_f:
                f_data = json.loads(line)


                ai_review = generate_reviews_based_on_features(f_data['features'])

                data = {
                    "ai_text": ai_review[0]['text'],
                    "human_text": f_data['human_text'].trim("\n\"")
                }
                json.dump(data, out_f)
                out_f.write('\n')


def fine_tune_model():

    with open("features.json", 'r', encoding='utf-8-sig', newline='') as in_f:
        data = []
        for line in in_f:
            f_data = json.loads(line)
            data.append(f_data)
        mft = ModelFineTuner()
        mft.fine_tune(model_name='review_generator',data=data)

#extract_features(1)
#generate_human_ai_comparison()

fine_tune_model()








