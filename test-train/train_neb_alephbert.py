from transformers import BertTokenizer, BertForMaskedLM
from torch.utils.data import Dataset, DataLoader

import torch

model_path = '../alephbertgimmel/alephbertgimmel-small/ckpt_29400--Max128Seq'

tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForMaskedLM.from_pretrained(model_path)

train_on_gpu = torch.cuda.is_available()
print("train on GPU: %s" % train_on_gpu)

if train_on_gpu:
  device = torch.device("cuda")
else:
  device = torch.device('cpu')

model.to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

def reviews_loader(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield line[:128]



input_ids = []
attention_masks = []
for sentence in reviews_loader('train_dataset.txt'):
    encoded_dict = tokenizer.encode_plus(
                        sentence,
                        add_special_tokens=True,
                        max_length=128,
                        truncation=True,
                        pad_to_max_length=True,
                        return_attention_mask=True
                   )
    input_ids.append(encoded_dict['input_ids'])
    attention_masks.append(encoded_dict['attention_mask'])

# Convert the lists to tensors
input_ids = torch.tensor(input_ids)
attention_masks = torch.tensor(attention_masks)



# Create a custom dataset class to pass the data to the dataloader
class TextDataset(Dataset):
    def __init__(self, input_ids, attention_masks):
        self.input_ids = input_ids
        self.attention_masks = attention_masks

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, item):
        return {
            'input_ids': self.input_ids[item],
            'attention_mask': self.attention_masks[item]
        }
# Create an instance of the custom dataset
training_dataset = TextDataset(input_ids, attention_masks)

# Create a dataloader to pass the data to the model
dataloader = DataLoader(training_dataset, batch_size=8, shuffle=True)

# Fine-tune the model
for epoch in range(1):
    model.train()
    for i, batch in enumerate(dataloader):
        input_ids = batch['input_ids'].to(device)
        attention_masks = batch['attention_mask'].to(device)

        # Clear any previously calculated gradients
        model.zero_grad()

        # Pass the input data to the model
        outputs = model(input_ids, attention_mask=attention_masks, labels=input_ids)
        loss, logits = outputs[:2]

        # Backpropagate the loss to update the model's parameters
        loss.backward()

        # Update the model's parameters using optimizer
        optimizer.step()
        #Print the loss and accuracy of the model for every 100 batches
        if i % 100 == 0:
            print("Epoch {}/{}, Batch {}/{}, Loss: {:.4f}".format(
                epoch + 1, 5, i, len(dataloader), loss.item()
            ))


torch.save(model.state_dict(), 'bert_fine_tuned.pt')


# Evaluate the fine-tuned model
model.eval()


# Convert the evaluation data to input IDs and attention masks
eval_input_ids = []
eval_attention_masks = []
for sentence in reviews_loader('test_dataset.txt'):
    encoded_dict = tokenizer.encode_plus(
                        sentence,
                        add_special_tokens=True,
                        max_length=512,
                        pad_to_max_length=True,
                        return_attention_mask=True
                   )
    eval_input_ids.append(encoded_dict['input_ids'])
    eval_attention_masks.append(encoded_dict['attention_mask'])

# Convert the lists to tensors
eval_input_ids = torch.tensor(eval_input_ids)
eval_attention_masks = torch.tensor(eval_attention_masks)

# Create an instance of the custom dataset for the evaluation data
eval_dataset = TextDataset(eval_input_ids, eval_attention_masks)

# Create a dataloader to pass the evaluation data to the model
eval_dataloader = DataLoader(eval_dataset, batch_size=32, shuffle=False)

# Calculate the accuracy of the fine-tuned model on the evaluation data
accuracy = 0
for i, batch in enumerate(eval_dataloader):
    input_ids = batch['input_ids'].to(device)
    attention_masks = batch['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_masks)
        logits = outputs[0]

    predictions = torch.argmax(logits, dim=2)
    accuracy += (predictions == input_ids).mean()

print("Accuracy of the fine-tuned model on the evaluation data: {:.4f}".format(accuracy / len(eval_dataloader)))