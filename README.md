
# AutoShakespeare

This program generates shakespear-style text from a piece of starting text that you provide. This is a pytorch implementation of the tensorflow tutorial on [generating text with an RNN](https://www.tensorflow.org/tutorials/text/text_generation).


## Usage
You just need to run `main.py` script to run the program. Here are the arguments the program can receive:
```
usage:
       [-h] [--starting_text STARTING_TEXT] [--output_size OUTPUT_SIZE]
       [--use_pretrained {none,rnn,gru,lstm}]
       [--recurrent_module {rnn,gru,lstm}] [--dropout DROPOUT]

optional arguments:
  -h, --help            show this help message and exit
  --starting_text STARTING_TEXT, -s STARTING_TEXT
                        piece of text used as starting point for generation
  --output_size OUTPUT_SIZE, -o OUTPUT_SIZE
                        length of text to generate (in characters)
  --use_pretrained {none,rnn,gru,lstm}
                        which pretrained model to use?
  --recurrent_module {rnn,gru,lstm}, -r {rnn,gru,lstm}
                        type of recurrent module used for training
  --dropout DROPOUT, -d DROPOUT
                        how much dropout to use for training (between 0 and 1)
```

If `--use_pretrained` is not `none`, then a new model will be trained before generation begins, otherwise the specified pre-trained model is used.

## Dependencies

```
* PyTorch - 1.5
* matplotlib - 3.2
* numpy - 1.18
```

The versions provided above are those the program was tested with. The dependency is very light however, since the features used are very basic. 

## Sample Output
Here are three 500-character long texts generated by the pretrained models, using `MENENIUS` as the starting text:

**RNN**:
```
Ha! Marcius coming home!

VOLUMNIA:
Ay, worthy Menenius; and with most prosperous
approbate
approbied is not unknown to the senate; they have
had inkling this fortnight what we interior survey of your good selves!
O that you could!

BRUTUS:
What then?
'Fore me, this fellow speaks! who come to destre consuberand, if they are trust?

COMINIUS:
As I guess, Marcius,
Their bands i' the vaward are the Antiate, who cell not
Be grafted to have the general food at will with me trigure
There as 
```
**LSTM**:
```
MENENIUS:
Ha! Marcius coming home!

VOLUMNIA:
Ay, worthy Menenius; and with most prosperous
approbate in this afternoob.

MENENIUS:
There was a netth doust;
And make my wars on you: look to't: come on;
If not this sound arm that have
fall enemy take him seek
danger where he was like to find fame. To a cruel
war I sent him; from whence he receive
But it proceed an hour timps: the noble senate, who,
answere yet deed to doubh to your worships have
delivered the matter well, when I find the air of t
```
**GRU**:
```
MENENIUS:
O, true-bred!

First Senator:
Your company to the Capitol; where, I know,
Our greatest friends! Come, blow thy blast.
Tutus Aufidius, is he within your walls?

First Senator:
Speak, good Cominius:
Leave nothing out for length, and his actions
in their hearts, that for their tongues to be
silent, and not confess shall plaines; and their pluckings; well forth proverbs,
That hunger broke stone walls, that dogs must eat,
That meat fit in it.

MENENIUS:
A lay our good word, that is as enemy
```
It can be seen that all three models have a solid understanding of the structure of a play: they keep creating blocks of text which are preceded by the name of the speaker in all-capitals (except when there's a title instead of a name, in which case it is merely capitalized). Also, most of the sentences are grammatical. But, since the model is character-based, it hasn't understood the meaning of words, and as a result most sentences are semantically incorrect.

## Authors

* **Ahmad Pourihosseini** -  [ahmad-PH](https://github.com/ahmad-PH)

## Acknowledgments

* The idea of this project is inspired by the tensorflow tutorial on [generating text with an RNN](https://www.tensorflow.org/tutorials/text/text_generation) and that is also were the dataset is downloaded from.
