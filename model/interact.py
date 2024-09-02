import torch
import torch.nn.functional as F

import random
import pytorch_lightning as pl
from itertools import chain
from argparse import ArgumentParser
from model.personachat import PersonaChatModel
from model.data import SPECIAL_TOKENS, build_input_from_segments
from model.utils import get_dataset

import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def top_filtering(logits, top_k=0., top_p=0.9, threshold=-float('Inf'), filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k, top-p (nucleus) and/or threshold filtering
        Args:
            logits: logits distribution shape (vocabulary size)
            top_k: <=0: no filtering, >0: keep only top k tokens with highest probability.
            top_p: <=0.0: no filtering, >0.0: keep only a subset S of candidates, where S is the smallest subset
                whose total probability mass is greater than or equal to the threshold top_p.
                In practice, we select the highest probability tokens whose cumulative probability mass exceeds
                the threshold top_p.
            threshold: a minimal threshold to keep logits
    """
    assert logits.dim() == 1  # Only work for batch size 1 for now - could update but it would obfuscate a bit the code
    top_k = min(top_k, logits.size(-1))
    if top_k > 0:
        # Remove all tokens with a probability less than the last token in the top-k tokens
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        # Compute cumulative probabilities of sorted tokens
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probabilities = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probabilities > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        # Back to unsorted indices and set them to -infinity
        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value

    indices_to_remove = logits < threshold
    logits[indices_to_remove] = filter_value

    return logits


def sample_sequence(personality, history, tokenizer, model, hparams, current_output=None):
    special_tokens_ids = tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS)
    if current_output is None:
        current_output = []

    for i in range(hparams.max_length):
        instance = build_input_from_segments(personality, history, current_output, tokenizer, with_eos=False)

        #input_ids = torch.tensor(instance["input_ids"], device=hparams.device).unsqueeze(0)
        #token_type_ids = torch.tensor(instance["token_type_ids"], device=hparams.device).unsqueeze(0)
        input_ids = torch.tensor(instance["input_ids"]).unsqueeze(0)
        token_type_ids = torch.tensor(instance["token_type_ids"]).unsqueeze(0)

        logits = model(input_ids, token_type_ids=token_type_ids).logits
        if isinstance(logits, tuple):  # for gpt2 and maybe others
            logits = logits[0]
        logits = logits[0, -1, :] / hparams.temperature
        logits = top_filtering(logits, top_k=hparams.top_k, top_p=hparams.top_p)
        probs = F.softmax(logits, dim=-1)

        prev = torch.topk(probs, 1)[1] if hparams.no_sample else torch.multinomial(probs, 1)
        if i < hparams.min_length and prev.item() in special_tokens_ids:
            while prev.item() in special_tokens_ids:
                if probs.max().item() == 1:
                    warnings.warn("Warning: model generating special token with probability 1.")
                    break  # avoid infinitely looping over special token
                prev = torch.multinomial(probs, num_samples=1)

        if prev.item() in special_tokens_ids:
            break
        current_output.append(prev.item())

    return current_output


#def run():   
    # ------------
    # args
    # ------------   
parser = ArgumentParser()
parser.add_argument("--dataset_path", type=str, default="data/personachat_self_original_comet_preprocessed.json", help="Path or url of the dataset. If empty download from S3.")
parser.add_argument("--dataset_cache", type=str, default='personachat_self_comet', help="Path or url of the dataset cache")
parser.add_argument("--experiment", type=str, default="./experiments/version_13-05-2021--15-01-45/", help="Path name of checkpoint")
parser.add_argument("--max_history", type=int, default=2, help="Number of previous utterances to keep in history")
parser.add_argument("--no_sample", action='store_true', help="Set to use greedy decoding instead of sampling")
parser.add_argument("--max_length", type=int, default=20, help="Maximum length of the output utterances")
parser.add_argument("--min_length", type=int, default=1, help="Minimum length of the output utterances")
parser.add_argument("--seed", type=int, default=1234, help="Seed")
parser.add_argument("--temperature", type=int, default=0.7, help="Sampling softmax temperature")
parser.add_argument("--top_k", type=int, default=0, help="Filter top-k tokens before sampling (<=0: no filtering)")
parser.add_argument("--top_p", type=float, default=0.9, help="Nucleus filtering (top-p) before sampling (<=0.0: no filtering)")
parser.add_argument("--comet_greedy", action='store_true', help="Use top-most comet expansion")
hparams = parser.parse_args()

#pl.seed_everything(hparams.seed)

model = PersonaChatModel.load_from_experiment(hparams.experiment)
tokenizer = model.tokenizer

dataset = get_dataset(tokenizer, hparams.dataset_path, hparams.dataset_cache)
# personalities = [dialog["personality"] for dataset in dataset.values() for dialog in dataset]
dialogs = [dialog for dataset in dataset.values() for dialog in dataset]
dialog =  random.choice(dialogs)
# personality = random.choice(personalities)
personality = dialog['personality']
# comet_annotations = dialog["coment_annotation"]
# for sent in comet_annotations:
#     sent_beams = []
#     for effect in sent['comet'].items():
#         # not sure is ' .' should be added or '.'
#         # tokenizer realize different tokens for each of the above options
#         # beams = [x+' .' for x in effect[1]['beams']]
#         if hparams.comet_greedy:
#             sent_beams += [effect[1]['beams'][0]]
#         else:
#             sent_beams += effect[1]['beams']
# personality += sent_beams
# print(personality)
# print(tokenizer.decode(chain(*personality)))

# history = []
# personality = [[1820, 4004, 4097, 318, 257, 3734, 31934, 764], [72, 588, 9015, 299, 26550, 764], [72, 1842, 3555, 764], [72, 670, 379, 257, 7541, 764]]
# print(personality)
# print(tokenizer.decode(chain(*personality)))# tokenizer.decode解出personality
# while True:
#     raw_text = input(">>> ")
#     while not raw_text:
#         print('Prompt should not be empty!')
#         raw_text = input(">>> ")
#     history.append(tokenizer.encode(raw_text))
#     with torch.no_grad():
#         out_ids = sample_sequence(personality, history, tokenizer, model, hparams)
#     history.append(out_ids)
#     history = history[-(2*hparams.max_history+1):]
#     out_text = tokenizer.decode(out_ids, skip_special_tokens=True)
#     print(out_text)

# x = tokenizer.decode(chain(*personality))
# print(tokenizer.encode(x))
# y = [1820, 3367, 318, 257, 4346, 2137, 13],[72, 1101, 281, 45630, 272, 9511, 13]
# print(tokenizer.decode(chain(*y)))
