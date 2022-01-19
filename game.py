import json
import random
from datetime import datetime
from typing import List

import streamlit as st


@st.cache
def get_word(candidates, game, today) -> str:
    random.seed(f'{today}_{game}')
    target_value = random.choice(candidates)
    invalid = True
    while invalid:
        invalid = False
        for letter in target_value:
            if letter not in alphabet:
                invalid = True
        if invalid:
            target_value = random.choice(candidates)
    return target_value


def clean(a: str) -> str:
    return ''.join([x for x in a if x in alphabet])


def guess_result(t: str, g: str) -> List[str]:
    result = ['red'] * len(t)
    for index in range(len(t)):
        if g[index] == t[index]:
            result[index] = 'green'
        elif g[index] in t:
            result[index] = 'yellow'
    return result


alphabet = 'abcdefghijklmnopqrstuvwxyz'
wordle = json.load(open('wordle.json', 'r'))
st.session_state.candidates = {}
for i in range(10):
    queries = wordle[str(i+1)]
    candidates = []
    for q in queries.values():
        candidates += q
    st.session_state.candidates[i+1] = candidates

st.title('Wordle game clone')
st.markdown('[Wordle](https://www.powerlanguage.co.uk/wordle/) alike but you can try without limit.')

word_len = st.number_input(key='word_len', label='Input word length', min_value=1, max_value=10, value=5)
candidates = st.session_state['candidates'][word_len]


if 'game' not in st.session_state.keys():
    st.session_state.game = 1
st.session_state.target = get_word(candidates, st.session_state.game, datetime.today().date().strftime('%Y%m%d'))

if 'history' not in st.session_state.keys():
    st.session_state.history = {st.session_state.target: {}}

if st.button('Another word'):
    st.write('You can try a different word, but the whole batch will start over once the webpage is refreshed. It will refresh each day.')
    while st.session_state.target in st.session_state.history.keys():
        st.session_state.game = st.session_state.game + 1
        st.session_state.target = get_word(candidates, st.session_state.game, datetime.today().date().strftime('%Y%m%d'))

if st.session_state.target not in st.session_state.history.keys():
    st.session_state.history[st.session_state.target] = {}

current_len = len(st.session_state.target)
guess = [''] * current_len
cols = st.columns(current_len)
for i in range(current_len):
    with cols[i]:
        guess[i] = clean(st.text_input(key=f'guess_{st.session_state.game}_{i}', label=f'letter {i+1}', max_chars=1).lower())
        if guess[i] not in alphabet:
            st.warning('Not valid input')
guessed = ''.join(guess)
if guessed not in candidates:
    st.warning(f'Not a known word')
else:
    if guessed not in st.session_state.history[st.session_state.target].keys():
        st.session_state.history[st.session_state.target][guessed] = guess_result(st.session_state.target, guessed)

for word, result in st.session_state.history[st.session_state.target].items():
    result_cols = st.columns(current_len)
    for i in range(current_len):
        with result_cols[i]:
            if result[i] == 'green':
                st.success(word[i].upper())
            elif result[i] == 'yellow':
                st.warning(word[i].upper())
            else:
                st.error(word[i].upper())

if st.button('Reveal word') or guessed == st.session_state.target:
    st.write(f'Target is {st.session_state.target}')
