import json

import streamlit as st


def rearrange(word: str) -> str:
    letters = []
    for letter in word:
        if letter not in letters:
            letters.append(letter)
    letters.sort()
    return ''.join(letters)


def sub(a: str, b: str) -> bool:
    for letter in a:
        if letter not in b:
            return False
    return True


def consist(a: str, b: str) -> bool:
    for letter in a:
        if letter in b:
            return True
    return False


def filter_pos(a: [], b: str, c: int) -> []:
    result = []
    for candidate in a:
        if len(candidate) >= c and candidate[c] == b:
            result.append(candidate)
    return result


def filter_pos_not(a: [], b: str, c: int) -> []:
    result = []
    for candidate in a:
        if len(candidate) >= c and candidate[c] not in b:
            result.append(candidate)
    return result


def clean(a: str) -> str:
    return ''.join([x for x in a if x in alphabet])


alphabet = 'abcdefghijklmnopqrstuvwxyz'
wordle = json.load(open('wordle.json', 'r'))

st.title('Wordle Helper')
st.markdown('Help solve [Wordle](https://www.powerlanguage.co.uk/wordle/) alike games.')

word_len = st.number_input(key='word_len', label='Input word length', min_value=1, max_value=10, value=5)

known = st.text_input(key='known_letters', label='Input known letters', max_chars=word_len).lower()
query = rearrange(clean(known))
consist_len = len(query)

known_not = st.text_input(key='known_letters_not',
                          label='Input letters that do not appear', max_chars=len(alphabet)-consist_len).lower()

candidates = wordle[str(word_len)]
valid = []
for w in candidates:
    if sub(query, w) and not consist(query, known_not):
        valid += candidates[w]
for i in range(word_len):
    pos = clean(st.text_input(label=f'Letter at {i + 1} should be', max_chars=1).lower())
    if pos and pos in query:
        valid = filter_pos(valid, pos, i)
    pos_not = clean(st.text_input(label=f'Must not appear at {i+1}', max_chars=consist_len).lower())
    if pos_not and consist(pos_not, query):
        valid = filter_pos_not(valid, pos_not, i)
if known:
    if not valid:
        st.warning('Found nothing against the query')
    else:
        st.write('Pick one below to try')
        st.info(' '.join(valid))
