from transformers import BertTokenizer, BertForMaskedLM
from torch.utils.data import Dataset, DataLoader
import torch

model_path = '../alephbertgimmel/alephbertgimmel-small/ckpt_29400--Max128Seq'
fine_tuned = 'bert_fine_tuned.pt'
class TextCorrector:

    def __init__(self):
        device = torch.device('cpu')
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        #self.model = BertForMaskedLM.from_pretrained(model_path)
        #self.model.load_state_dict(torch.load('./bert_fine_tuned.pt', map_location=device))
        self.model = torch.load(fine_tuned)
        self.model.eval()

    def continue_sentence(self, partial_sentence ):
        input_ids = torch.tensor(self.tokenizer.encode(partial_sentence + " [MASK]", add_special_tokens=True)).unsqueeze(0)

        # Use the model to generate masked language model predictions
        with torch.no_grad():
            outputs = selfmodel(input_ids)
            prediction_scores = outputs[0]

        # Get the index of the predicted token for the masked token
        predicted_index = prediction_scores[0, -1].argmax().item()
        predicted_token = selftokenizer.convert_ids_to_tokens([predicted_index])[0]

        # Append the predicted token to the partial sentence
        generated_sentence = partial_sentence + " " + predicted_token

        print(generated_sentence)


    def rephrase(self, text):
        input_ids = torch.tensor(self.tokenizer.encode(text, add_special_tokens=True)).unsqueeze(0)
        with torch.no_grad():
            outputs = self.model(input_ids)
            prediction_scores = outputs[0]

        predicted_index = prediction_scores[0, -1].argmax().item()
        predicted_token  =  self.tokenizer.convert_ids_to_tokens([predicted_index])[0]
        generated_sentence = text + " " + predicted_token
        while predicted_token != self.tokenizer.sep_token:
            input_ids = torch.tensor(self.tokenizer.encode(generated_sentence, add_special_tokens=True)).unsqueeze(0)
            with torch.no_grad():
                outputs = self.model(input_ids)
                prediction_scores = outputs[0]
            predicted_index = prediction_scores[0, -1].argmax().item()
            predicted_token = self.tokenizer.convert_ids_to_tokens([predicted_index])[0]
            print(predicted_token)
            generated_sentence += " " + predicted_token
        print(generated_sentence)
        return generated_sentence
