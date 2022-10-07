import sys
import datetime
import json

print(f'Start Program hmmlearn: {datetime.datetime.now()}')
TRAIN_TAGGED_INPUT_FILE_PATH = sys.argv[1]

OUTPUT_FILE_PATH = 'hmmmodel.txt'

# tag_word_dict:
# {tag_x: { word_y: (int) number of this word with this tag }}
tag_word_dict = {}
# all_tag_dict: 
# {tag_x: number of this tag in corpus}
all_tag_dict = {}
# all_word_dict: 
# {word_x: number of this word in corpus}
all_word_dict = {}
# trans_dict:
# {start_tag: {end_tag: number of transition from 'start tag' to 'end tag'}}
trans_dict = {}
START_STATE = '|start|'
END_STATE = '|end|'
# Emission matrix
emission_prob_dict = {}
# transition matrix
transition_prob_dict = {}
# distinct_word_tag_dict:
# {tag_x: number of distinct words using this tag}
distinct_word_tag_dict = {}

open_class_tag_list = []
closed_class_tag_list = []

## read training tagged data

def split_word_from_tagged_format(word):
    slash_index = word.rindex('/')
    return word[:slash_index], word[slash_index+1:]
        
lines = []
with open(TRAIN_TAGGED_INPUT_FILE_PATH, 'rt') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()
    words = line.split(' ')
    for i in range(len(words)):
        word = words[i]
        only_word, tag = split_word_from_tagged_format(word)

        # fill values in all_tag_dict
        if tag in all_tag_dict: 
            all_tag_dict[tag] = all_tag_dict[tag] + 1
        else:
            all_tag_dict[tag] = 1
        # fill values in all_word_dict
        if only_word in all_word_dict: 
            all_word_dict[only_word] = all_word_dict[only_word] + 1
        else:
            all_word_dict[only_word] = 1
        #fill values in word_tag_dict
        if tag in tag_word_dict:
            if only_word in tag_word_dict[tag]:
                tag_word_dict[tag][only_word] = tag_word_dict[tag][only_word] + 1
            else:
                tag_word_dict[tag][only_word] = 1
        else:
            tag_word_dict[tag] = {f'{only_word}': 1}

    for i in range(len(words) + 1):
        #fill values in trans_dict
        if i == 0:
            previous_tag = START_STATE
            _, next_tag = split_word_from_tagged_format(words[i])
        elif i == len(words):
            _, previous_tag = split_word_from_tagged_format(words[i-1])
            next_tag = END_STATE
        else:
            _, previous_tag = split_word_from_tagged_format(words[i-1])
            _, next_tag = split_word_from_tagged_format(words[i])

        if previous_tag in trans_dict:
            if next_tag in trans_dict[previous_tag]:
                trans_dict[previous_tag][next_tag] = trans_dict[previous_tag][next_tag] + 1
            else:
                trans_dict[previous_tag][next_tag] = 1
        else:
            trans_dict[previous_tag] = {f'{next_tag}': 1}


for key_tag, value in tag_word_dict.items():
    for key_word, num in value.items():
        if key_tag not in emission_prob_dict:
            emission_prob_dict[key_tag] = {}
        emission_prob_dict[key_tag][key_word] = tag_word_dict[key_tag][key_word] / all_tag_dict[key_tag]

    distinct_word_tag_dict[key_tag] = len(value)


# finding open-class, closed-class tag
NUM_OF_OPEN_CLASS = 5

all_tag_list = list(all_tag_dict.keys())
all_tag_list = sorted(all_tag_list, key=lambda x: distinct_word_tag_dict[x], reverse=True)

if NUM_OF_OPEN_CLASS > len(all_tag_list):
    NUM_OF_OPEN_CLASS = len(all_tag_list)
open_class_tag_list = all_tag_list[0:NUM_OF_OPEN_CLASS]
closed_class_tag_list = all_tag_list[NUM_OF_OPEN_CLASS:]


# smoothing for transition probability
# adding 1 to every transition stage
tag_with_start = list(all_tag_dict.keys())
tag_with_start.append(START_STATE)
tag_with_end = list(all_tag_dict.keys())
tag_with_end.append(END_STATE)

for start_stage in tag_with_start:
    for end_stage in tag_with_end:
        if start_stage == START_STATE and end_stage == END_STATE:
            continue
        if start_stage not in trans_dict:
            trans_dict[start_stage] = {}
            trans_dict[start_stage][end_stage] = 1
        elif end_stage not in trans_dict[start_stage]:
            trans_dict[start_stage][end_stage] = 1
        else:
            trans_dict[start_stage][end_stage] = trans_dict[start_stage][end_stage] + 1

for start_state, value in trans_dict.items():
    for end_state, num in value.items():
        if start_state not in transition_prob_dict:
            transition_prob_dict[start_state] = {}
        transition_prob_dict[start_state][end_state] = trans_dict[start_state][end_state] / sum(trans_dict[start_state].values())

json_obj = {}
json_obj['tag_word_dict'] = tag_word_dict
json_obj['all_tag_dict'] = all_tag_dict
json_obj['all_word_dict'] = all_word_dict
json_obj['trans_dict'] = trans_dict
json_obj['emission_prob_dict'] = emission_prob_dict
json_obj['transition_prob_dict'] = transition_prob_dict
json_obj['open_class_tag_list'] = open_class_tag_list
json_obj['closed_class_tag_list'] = closed_class_tag_list


str_to_file = json.dumps(json_obj, sort_keys=True, indent=4)
with open(OUTPUT_FILE_PATH, "wt") as f:
    f.write(str_to_file)

print(f'Program hmmlearn finish: {datetime.datetime.now()}')
