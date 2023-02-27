import pandas as pd
import subprocess
import openai
openai.api_key = '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'
class ModelFineTuner:
    def __init__(self):
        self.model_name  = None
        self.data = None
        pass

    def fine_tune(self, model_name, data):
        self.model_name = model_name
        self.data = data
        self.generate_fine_tune_csv()
        self.generate_model()

    def generate_model(self):
        src_file = self.model_name + '.csv'
        cmd = 'openai tools fine_tunes.prepare_data --file {} --quiet'.format(src_file)
        subprocess.run(cmd.split())

        ## Start fine-tuning
        src_file = self.model_name + '_prepared.jsonl'
        suffix = self.model_name
        cmd = 'openai api fine_tunes.create --training_file {} --model davinci --suffix "{}"'.format(src_file,self.model_name)
        subprocess.run(cmd.split())



    def generate_fine_tune_csv(self):
        df = pd.DataFrame()
        for row in self.data:
            features = row['features']
            if "name" not in features:
                continue
            f_text = ''
            for key, value in features.items():
                key = key.strip('_')
                f_text += "{}:{}\n".format(key, value)
            new_row = {
                'prompt': f_text,
                'completion': row['human_text']
            }
            new_row = pd.DataFrame([new_row])
            df = pd.concat([df, new_row], axis=0, ignore_index=True)
        out_file = self.model_name + '.csv'
        df.to_csv(out_file)



