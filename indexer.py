#!/usr/bin/env python
# coding: utf-8
#from tqdm import tqdm
import re
import sys
import pickle

def process():
    with open("queries_all.txt") as file:
        for line in file:
	    #каждая строка - запрос        
            query = line[:-1].lower().split('\t')
            right = re.findall(re.compile(r'\w+', re.U), query[-1])
            if not right:
                continue
            last = right[0]
            #dict_w - словарь биграмм. ключ - слово, значение пара(число и словарь)
            #число - сколько раз слово раз встретилось
            #словарь - ключ - второе слово, значение - сколько раз оно встречалось после первого
            if last in dict_w:
                dict_w[last][0] += 1
            else:
                dict_w[last] = [1, {}]
            for word in right[1:]:
                if word in dict_w:
                    dict_w[word][0] += 1
                else:
                    dict_w[word] = [1, {}]
                last_dict = dict_w[last][1]
                if word in last_dict:
                    last_dict[word] += 1
                else:
                    last_dict[word] = 1
                last = word
            for word in right:
            	#count_of_words - словарь(длина-сколько слов такой длины)
                length = len(word)
                if length in count_of_words:
                    count_of_words[length] += 1
                else:
                    count_of_words[length] = 1
                word += ' '
                #dict_p - дерево префиксов. каждая вершина соотвествует префиксу, в ней хранится последняя буква префикса и сколько раз он встречался
                dict_ = dict_p
                l = len(word)
                for c in word:
                    if c in dict_:
                        dict_[c][0] += l
                    else:
                        dict_[c] = [l, {}]
                    dict_ = dict_[c][1]
                    l -= 1

if __name__ == "__main__":
    sys.setrecursionlimit(50000)
    dict_w = {}
    dict_p = {}
    count_of_words = {}
    process()

    count_of_prefix = {}
    #count_of_prefix - словарь(длина - сколько префиксов такой длины)
    s = 0
    for i in range(max(count_of_words), 0, -1):
        if i in count_of_words:
            s += count_of_words[i]
        count_of_prefix[i] = s

    with open("__dict_w__", 'wb') as f:
        pickle.dump(dict_w, f)
    with open("__dict_p__", 'wb') as f:
        pickle.dump(dict_p, f)
    with open("__count_of_prefix__", 'wb') as f:
        pickle.dump(count_of_prefix, f)
