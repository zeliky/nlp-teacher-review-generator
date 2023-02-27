import torch
import torch.nn as nn
import nltk
from transformers import BertTokenizer

model_path = '../alephbertgimmel/alephbertgimmel-small/ckpt_29400--Max128Seq'
nltk.download('punkt')
tokenizer = BertTokenizer.from_pretrained(model_path)


class StyleTransferModel(nn.Module):
    def __init__(self):
        super(StyleTransferModel, self).__init__()
        self.encoder = BertForMaskedLM.from_pretrained(model_path)
        self.decoder = nn.Linear(768, 768)

    def forward(self, input_ids, attention_mask, target_style):

        encoded_text = self.encoder(input_ids, attention_mask)[1]
        # Extract the style from the encoded text
        style = self.decoder(encoded_text)
        # Encode the target style
        target_style = self.encoder(target_style)[1]
        # Transfer the style from the input text to the target style
        output_style = target_style + (style - target_style)
        return output_style

def preprocess(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove stop words
    stop_words = set(nltk.corpus.stopwords.words('english'))
    words = nltk.word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    # Stem the words
    stemmer = nltk.PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    return ' '.join(words)

# Load the human-written text and the openai generated text
human_text = open('human.txt').read()
openai_text = open('openai.txt').read()

# Preprocess the text
human_text = preprocess(human_text)
openai_text = preprocess(openai_text)

# Train the style transfer model
model = StyleTransferModel()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()
for i in range(100):
    input_ids = torch.tensor(tokenizer.encode(openai_text)).unsqueeze(0)
    attention_mask = torch.tensor([1] * len(input_ids))
    target_ids = torch.tensor(tokenizer.encode(human_text)).unsqueeze(0)
    target_mask = torch.tensor([1] * len(target_ids))
    optimizer.zero_grad()
    output_style = model(input_ids, attention_mask, target_ids)
    loss = criterion(output_style, target_style)
    loss.backward()
    optimizer.step()

# Generate improved text
improved_text = tokenizer.decode(output_style.squeeze().argmax(axis=-1))
print(improved_text)