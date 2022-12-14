import sys
import datetime
import json

print(f'Start Program hmmdecode: {datetime.datetime.now()}')

TEST_INPUT_FILE_PATH = sys.argv[1]
OUTPUT_FILE_PATH = 'hmmoutput.txt'
MODEL_PARAMETER_FILE_PATH = 'hmmmodel.txt'

# tag_word_dict:
# {tag_x: { word_y: (int) number of this word with this tag }}
tag_word_dict = {}
# all_tag_dict: 
# {tag_x: number of this tag in corpus}
all_tag_dict = {}
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

class Node: 
    def __init__(self, prob, tag, previous_node, count):
        self.prob = prob
        self.tag = tag
        self.previous_node = previous_node
        self.count = count

with open(MODEL_PARAMETER_FILE_PATH, 'rt') as f:
    lines = f.read()
    json_obj = json.loads(lines)
    tag_word_dict = json_obj['tag_word_dict']
    all_tag_dict = json_obj['all_tag_dict']
    all_word_dict = json_obj['all_word_dict']
    trans_dict = json_obj['trans_dict']
    emission_prob_dict = json_obj['emission_prob_dict']
    transition_prob_dict = json_obj['transition_prob_dict']
    open_class_tag_list = json_obj['open_class_tag_list']
    closed_class_tag_list = json_obj['closed_class_tag_list']
 
write_lines = ''
with open(TEST_INPUT_FILE_PATH, 'rt') as f:
    lines = f.readlines()
    for line in lines:
        words = line.strip().split(' ')
        tags = []
        all_tag_include_end = list(all_tag_dict.keys())
        all_tag_include_end.append(END_STATE)
        start_state_node = Node(prob=1, tag=START_STATE, previous_node=None, count=0)
        previous_node_list = [start_state_node]
        for word in words:
            this_layer_node_list = []
            list_for_loop_all_tag = []
            if word in all_word_dict: 
                list_for_loop_all_tag = all_tag_include_end
            else:
                list_for_loop_all_tag = open_class_tag_list

            for tag in list_for_loop_all_tag:
                if tag not in emission_prob_dict:
                    continue
                if word in all_word_dict and word not in emission_prob_dict[tag]:
                    continue
                max_probability = 0
                previous_node_for_max_probability = None
                for previous_node in previous_node_list:
                    previous_tag = previous_node.tag
                    previous_prob = previous_node.prob
                    if previous_tag == START_STATE and tag == END_STATE:
                        continue
                    # calculate prob
                    transition_probability = transition_prob_dict[previous_tag][tag]
                    total_probability = int
                    if word not in emission_prob_dict[tag]:
                        total_probability = transition_probability * previous_prob
                    else:
                        emission_probability = emission_prob_dict[tag][word]
                        total_probability = transition_probability * emission_probability * previous_prob
                    if total_probability > max_probability:
                        max_probability = total_probability
                        previous_node_for_max_probability = previous_node
                if max_probability == 0:
                    continue
                node = Node(prob=max_probability, tag=tag, previous_node=previous_node_for_max_probability, count=previous_node_for_max_probability.count+1)
                this_layer_node_list.append(node)
            previous_node_list = this_layer_node_list

        # find node with max prob in previous_node_list
        max_prob = 0
        node_for_max_prob = None
        for p in previous_node_list:
            if p.prob > max_prob:
                max_prob = p.prob
                node_for_max_prob = p
        node = node_for_max_prob
        count = node_for_max_prob.count
        while count > 0:
            tags.insert(0, node.tag)
            node = node.previous_node
            count = node.count
        new_line = ''
        if len(words) != len(tags):
            raise Exception('len of words in line is not equal to len of predict tag')
        for i in range(len(words)):
            word_with_tag = f'{words[i]}/{tags[i]}'
            new_line = f'{new_line} {word_with_tag}'
        write_lines = f'{write_lines}\n{new_line.strip()}'
write_lines = write_lines.strip()

with open(OUTPUT_FILE_PATH, 'wt') as f:
    f.write(write_lines)

print(f'Program hmmdecode finish: {datetime.datetime.now()}')



        