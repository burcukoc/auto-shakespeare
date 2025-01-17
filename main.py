# -*- coding: utf-8 -*-
"""NN-MP2-Q2-PyTorch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AcgZNMTDNLizYsmH7GvBYbT8T1ziwoWk
"""

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
from matplotlib import pyplot as plt
import argparse

import numpy as np
import time

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

with open('shakespeare.txt') as file:
    raw_data = file.read()

# Limit the dataset to make training lighter
limited_data = 50000 
raw_data = raw_data[:limited_data]

# Create the vocabulary of all the existing characters and the mapping to their
# respective integer indices
vocab = sorted(list(set(raw_data)))
char2int = dict((char, i) for i, char in enumerate(vocab))
int2char = vocab
embedding_size = len(vocab)

# Two helper functions that convert from a list of integers that represent
# characters to a string, and back
def string_to_int_list(str):
  return list(map(lambda x: char2int[x], str))

def int_list_to_string(int_list):
  result = ''
  for i in int_list:
    result += int2char[i]
  return result

# Use the helper function defined above to convert the data into a list
# of integers
data = string_to_int_list(raw_data)

# Two helper functions that turn a list of integers to their corresponding
# one-hot representation and back
def one_hot_encode(int_list: list):
  result = []
  for i in int_list:
    one_hot_rep = torch.zeros(embedding_size)
    one_hot_rep[i] = 1.
    result.append(one_hot_rep.unsqueeze(0))
  return torch.cat(result).to(device)

def one_hot_decode(list: torch.Tensor):
  return torch.argmax(list, dim=-1)

# This is a Dataset that receives a string, and chops it to smaller pieces
# according to seq_length and shift_length and then returns these smaller
# pieces when __getitem__ is called
class CharSequenceDataset(Dataset):
    def __init__(self, data: str, seq_length = 100, shift_length = 1):
        self.seq_length = seq_length
        self.shift_length = shift_length
        self.data = one_hot_encode(data)
    
    def _split_input_target(self, sequence):
        return sequence[:-self.shift_length], sequence[self.shift_length:]

    def __getitem__(self, i):
        return self._split_input_target(
            self.data[i * self.seq_length : (i+1) * self.seq_length])
    
    def __len__(self):
        return int(self.data.shape[0] / self.seq_length)

class Model(nn.Module):
    def __init__(self, input_size, output_size, hidden_dim,
                 recurrent_module="rnn", dropout_probability = None):
        super(Model, self).__init__()
        self.hidden_dim = hidden_dim

        self.embedding = nn.Embedding(embedding_size, embedding_size)

        # contruct the recurrent module:
        if recurrent_module == "rnn":
          self.recurrent_module = nn.RNN(input_size, hidden_dim, batch_first=True) 
        elif recurrent_module == "lstm":
          self.recurrent_module = nn.LSTM(input_size, hidden_dim, batch_first=True) 
        elif recurrent_module == "gru":
          self.recurrent_module = nn.GRU(input_size, hidden_dim, batch_first=True) 

        if dropout_probability != None:
          self.dp = nn.Dropout(dropout_probability)  
          self.has_dropout = True
        else:
          self.has_dropout = False

        self.fc = nn.Linear(hidden_dim, output_size)
    
    def forward(self, x):
        x = self.embedding(x.argmax(dim=2))
        out, _ = self.recurrent_module(x)
        if self.has_dropout:
          out = self.dp(out)
        out = self.fc(out)
        return out
    
    def forward_single(self, x):
      # Add a fake batch dimension, call forward, then remove the batch dimension
      return self.forward(x.unsqueeze(0))[0] 

    def forward_string(self, str):
      # convert the string to a suitable format before calling forward
      one_hot_rep = one_hot_encode(string_to_int_list(str))
      out = self.forward_single(one_hot_rep)
      # decode the result into a string
      return int_list_to_string(one_hot_decode(out))

# A helper class to compute averages
class AverageMeter:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = 0.
        self.count = 0

    def update(self, value):
        self.value += value
        self.count += 1

    def get(self):
        return self.value / self.count

# A helper function to generate text from a trained model `model`, using
# `starting_text` as the initial input to the model. this function needs to
# know what `shift_length` the model was trained with.
def generate_text(model, starting_text, shift_length, output_size):
  with torch.no_grad():
    model.eval()
    current_text = starting_text
    while len(current_text) < output_size:
      out = model.forward_string(current_text)
      new_text = out[-shift_length:] # select only the new part of the text
      current_text += new_text
    current_text = current_text[:output_size] # remove any exceeding text
  return current_text

def train(model, seq_length, shift_length, loss_function_string="cross_entropy", optimizer_string="adam"):
  n_epochs = 600
  lr = 0.005

  if loss_function_string == "cross_entropy":
    loss_function = nn.CrossEntropyLoss()
  elif loss_function_string == "mse":
    loss_function = nn.MSELoss()

  if optimizer_string == "adam":
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
  elif optimizer_string == "sgd":
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)

  # Instantiates a Dataset that was defined above, and uses it to create
  # a Dataloader to make training easier.
  batch_size = 256
  ds = CharSequenceDataset(data, seq_length, shift_length)
  dl = DataLoader(ds, batch_size = batch_size, shuffle=True)

  # The main training loop:
  loss_history = []
  for epoch in range(1, n_epochs + 1):
      loss_average = AverageMeter()
      for input_seq, target_seq in dl:
        optimizer.zero_grad() # Clears existing gradients from previous epoch
        #input_seq = input_seq.to(device)
        output = model(input_seq)
        output = output.view(-1, embedding_size)

        if loss_function_string == "cross_entropy":
          target_seq = target_seq.view(-1, embedding_size).argmax(1)
        elif loss_function_string == "mse":
          target_seq = target_seq.view(-1, embedding_size)

        # print('shape: ')
        # print(input_seq.shape)
        # print(output.shape)
        # print(target_seq.shape)

        # loss = criterion(output, target_seq.view(-1).long())
        loss = loss_function(output, target_seq)
        loss.backward()
        optimizer.step() 

        loss_average.update(loss.item())

      # record values for later use
      loss_history.append(loss_average.get())
      if epoch % 100 == 0:
          print('Epoch: {}/{} ........'.format(epoch, n_epochs), end=' ')
          print("Loss: {:.4f}".format(loss_average.get()))

  return loss_history

# What Follows contains the codes of different parts of the question.
# if you want to run a particular part, just uncomment it and run.


#     def __init__(self, input_size, output_size, hidden_dim,
#                  recurrent_module="rnn", dropout_probability = None):

# def train(model, seq_length, shift_length, loss_function_string="cross_entropy", optimizer_string="adam"):

# def generate_text(model, starting_text, shift_length, output_size):


if __name__=="__main__":
    parser = argparse.ArgumentParser('This program will generate some shakespear-style text from a piece of starting text that you provide. ' + 
        'If --use_pretrained is not "none", then a new model will be trained before generation begins, otherwise a pre-trained model is used.')
    parser.add_argument('--starting_text', '-s', default="MENENIUS", help="piece of text used as starting point for generation")
    parser.add_argument('--output_size', '-o', default=500, type=int, help="length of text to generate (in characters)")
    parser.add_argument('--use_pretrained', default="gru", help="which pretrained model to use?", choices=['none', 'rnn', 'gru', 'lstm'])
    parser.add_argument('--recurrent_module', '-r', default="gru", help="type of recurrent module used for training", choices=['rnn', 'gru', 'lstm'])
    parser.add_argument('--dropout', '-d', default=0., type=float, help="how much dropout to use for training (between 0 and 1)")
    args = parser.parse_args()


    if args.use_pretrained != 'none':
        model = Model(embedding_size, embedding_size, 500, args.use_pretrained, args.dropout).to(device)
        model.load_state_dict(torch.load(args.use_pretrained + '.pth'))

    else:
        model = Model(embedding_size, embedding_size, 500, args.recurrent_module, args.dropout).to(device)

        # print the structure of the model
        print('structure of the model:')
        print(model)

        # Train the model:
        start_time = time.time()
        loss_history = train(model, 100, 1)
        title = "final loss: {:.3f}".format(loss_history[-1])
        print('training finished in {:.1f} seconds'.format(time.time() - start_time))

        plt.plot(loss_history)
        plt.xlabel('epoch')
        plt.ylabel('loss')
        plt.title(title)

        # show the result:
        plt.show()

    # Generate text using the trained models:
    model.eval()
    print('generated text:')
    print(generate_text(model, args.starting_text, 1, args.output_size))
    print('\n\n')