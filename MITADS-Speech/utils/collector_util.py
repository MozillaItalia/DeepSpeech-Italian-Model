#from keras.preprocessing.text import text_to_word_sequence

maketrans = str.maketrans

def text_to_word_sequence(text,
                          filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n',
                          lower=True, split=" "):
    """Converts a text to a sequence of words (or tokens).
    # Arguments
        text: Input text (string).
        filters: list (or concatenation) of characters to filter out, such as
            punctuation. Default: ``!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\\t\\n``,
            includes basic punctuation, tabs, and newlines.
        lower: boolean. Whether to convert the input to lowercase.
        split: str. Separator for word splitting.
    # Returns
        A list of words (or tokens).
    """

    if lower:
        text = text.lower()

    translate_dict = {c: split for c in filters}
    translate_map = maketrans(translate_dict)
    text = text.translate(translate_map)

    seq = text.split(split)
    return [i for i in seq if i]


def create_vocabulary(rows):

 
    # estimate the size of the vocabulary
    words = set()
    for row in rows:
        transcript = row[2]## row['transcript']
        _words = set(text_to_word_sequence(transcript))
        words.update(_words)

    vocab_size = len(words)
    print('Generated vocab, size {}'.format(vocab_size))
    # integer encode the document
    #result = one_hot(text, round(vocab_size*1.3))
    #print(result)

    return words


def save_vocabulary(vocab,file_path):
    with open(file_path, 'w',encoding='utf-8') as out:
        for word in vocab:
            out.write(word + '\n')
     


def get_min_corpus_cover_vocab(corpus_rows,vocab,max_speaker=1):

    consumed_words = set()
    output_rows = []
    for row in corpus_rows:

        transcript = row[2] ## row['transcript']
        #speaker_id = row[3]
        words = set(text_to_word_sequence(transcript))

        ##se ci sono elementi da consumare
        if(not words.issubset(consumed_words)):
            ##OK - PRESO - ancora non incluso
            output_rows.append(row)
            consumed_words.update(words)
        else:
            pass

    
    return output_rows


