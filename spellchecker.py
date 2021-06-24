#!/usr/bin/env python
# coding: utf-8
import sys
import re
import numpy as np
import pickle
import Levenshtein

def generate_word(word):
    #функция идет по дереву префиксов и выдает 20 слов, наиболее близких к исходному
    length = 0
    pref = (dict_p, "")
    queue = [pref]
    result = []
    dists = []
    while queue:
        length += 1
        next_queue = []
        probs = []
        for prefix in queue:
            for key in prefix[0]:
                if key == ' ':
                    result.append(prefix[1])
                    dists.append(alpha ** -Levenshtein.distance(word, prefix[1]))
                else:
                    pr = prefix[1] + key
                    l1 = prefix[0][key][0] / count_of_prefix[length]
                    l2 = alpha ** -Levenshtein.distance(word[:length], pr)
                    if not l1 or not l2:
                        continue
                    probs.append(beta * np.log2(l1) + np.log2(l2)) #b * log2(frequency) + log2(a^(-leven))
                    next_queue.append((prefix[0][key][1], pr))
        queue = []
        for i in np.argsort(probs)[-N:]:
            queue.append(next_queue[i])
    res = []
    for i in np.argsort(dists)[-20:]:
        res.append(result[i])
    return res

def generate_join(words, query, orig_words):
    #функция выдает возможные исправления запроса, когда два соседних слова исходного запроса соединяются
    punct = re.findall(re.compile(r'\W+', re.U),' ' +  query + ' ')
    new_words = []
    for word in words[:-1]:
        new_words.append(word)
    for i in range(len(new_words)-1,-1,-1):
        if i != len(new_words)-1:
            new_words[i+1] = words[i+2]
        if not punct[i+1].isspace():
            continue
        string = punct[0][1:] + orig_words[0]
        for j in range(i):
            string += punct[j+1] + orig_words[j+1]
        for j in range(i+1, len(words)):
            string += orig_words[j] + punct[j+1]
        new_words[i] = words[i] + words[i+1]
        yield (new_words, string[:-1])

def generate_split(words, query, orig_words):
    #функция выдает возможные исправления запроса, когда слово исходного запроса делится на два
    punct = re.findall(re.compile(r'\W+', re.U),' ' +  query + ' ')
    new_words = []
    for word in words:
        new_words.append(word)
    new_words.append("")
    for i in range(len(words)-1, -1, -1):
        s1 = punct[0][1:]
        for j in range(i):
            s1 += orig_words[j] + punct[j+1]
        s3 = ""
        for j in range(i+1, len(words)):
            s3 += punct[j] + orig_words[j]
        s3 += punct[-1][:-1]
        if i != len(words)-1:
            new_words[i+2] = words[i+1]
        for j in range(1, len(words[i])):
            new_words[i] = words[i][:j]
            new_words[i+1] =  words[i][j:]
            s2 = new_words[i] + ' ' + new_words[i+1]
            yield (new_words, s1+s2+s3)

def probability(words, flag=False):
    #функция выдает вероятность исправленного запроса на основе словесных биграмм
    if not flag:    
        for word in words:
            if word not in dict_w:
                return 0
    p = 0.25
    last_word = words[0]
    last_word_exist = last_word in dict_w
    if last_word_exist:
        p = dict_w[last_word][0]
    for wd in words[1:]:
        p2 = 0.000001
        if last_word_exist:
            dw = dict_w[last_word]
            if wd in dw[1]:
                p2 = dw[1][wd] / dw[0]
        last_word = wd
        last_word_exist = last_word in dict_w
        p *= p2 
    return p

def choice_best(query, flag=False):
    #функция генерирует потенциальные исправления запроса и выдает лучшее в соответствии с вероятностной моделью
    #one iteration
    alpha = 5
    words = re.findall(re.compile(r'\w+', re.U), query.lower())
    w_orig = re.findall(re.compile(r'\w+', re.U), query)
    if not words:
        return query
    list_ = []
    res = []
    proba = probability(words, flag)
    if proba:
        list_.append(query)
        res.append(proba)

    for i in range(len(words)):
        gen_words = generate_word(words[i])
        new_words = []
        for word in words:
            new_words.append(word)
        for gen in gen_words:
            if gen == words[i]:
                continue
            new_words[i] = gen
            proba = probability(new_words, flag)
            if proba:
                res.append(proba * (alpha ** -Levenshtein.distance(words[i], gen)))
                
                l = len(w_orig[i])
                if l > len(gen):
                    l = len(gen)
                new_str = ""
                for k in range(l):
                    up = w_orig[i][k].isupper()
                    if up:
                        new_str += gen[k].upper()
                    else:
                        new_str += gen[k]
                for k in range(l, len(gen)):
                    if up:
                        new_str += gen[k].upper()
                    else:
                        new_str += gen[k]

                string = re.sub(w_orig[i], new_str, query)
                list_.append(string)
    
    if not flag:
        for new_words, string in generate_join(words, query, w_orig):
            proba = probability(new_words, flag)
            if proba:
                list_.append(string)
                #res.append(proba * (alpha ** --Levenshtein.distance(query, string)))
                res.append(proba / alpha)

    for new_words, string in generate_split(words, query, w_orig):
        proba = probability(new_words, flag)
        if proba:
            string = ' '.join(new_words)
            list_.append(string)
            res.append(proba / alpha) 


    if not list_:
        return choice_best(query, flag=True)
    return list_[np.argsort(res)[-1]]
    
    if not flag:
        for new_words in generate_join(words):
            proba = probability(new_words, flag)
            if proba:
                string = ' '.join(new_words)
                list_.append(string)
                res.append(proba * (alpha ** -Levenshtein.distance(query, string)))

    for new_words in generate_split(words):
        proba = probability(new_words, flag)
        if proba:
            string = ' '.join(new_words)
            list_.append(string)
            res.append(proba * (alpha ** -Levenshtein.distance(query, string))) 


    if not list_:
        return choice_best(query, flag=True)
    return list_[np.argsort(res)[-1]]

def pred(query):
    #функция выдает итоговое исправление(несколько итераций choice_best)
    l_ans = query
    for i in range(max_iter):
        answer = choice_best(l_ans)
        if answer == l_ans:
            break
        l_ans = answer
    return answer



if __name__ == "__main__":
    max_iter = 7
    alpha = 5
    N = 100
    beta = 0.01
    sys.setrecursionlimit(50000)
    with open("__dict_w__", 'rb') as f:
        dict_w = pickle.load(f)
    with open("__dict_p__", 'rb') as f:
        dict_p = pickle.load(f)
    with open("__count_of_prefix__", 'rb') as f:
        count_of_prefix = pickle.load(f)
    while True:
        try:
            query = input()
            if query:
                l_ans = query
                answer = pred(query)
                print(answer)
            else:
                break
        except:
            break

