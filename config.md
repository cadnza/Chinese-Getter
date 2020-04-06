# Chinese Getter

This add-on provides a very quick way to get Chinese metadata from either characters or pinyin. Operation is simple:

1. Input either characters or pinyin
2. Unfocus the field (hit tab)
3. Give it a couple of seconds to collect the metadata and position it neatly in your note

## Fields

Specifically, Chinese Getter gets the following:

### Chinese characters

If you input pinyin, Chinese Getter will pull the corresponding characters from Wiktionary.

### Chinese pinyin

Conversely, if you input pinyin, Chinese Getter will fill in the characters.

### Animations of Chinese characters

These come from MDBG.net and are invaluable for learning stroke order.

### Audio pronunciation

Of course, this comes from Forvo, which means that **you'll need an API key**. You can get one at https://api.forvo.com/.

## Configuration

Chinese Getter has six configurable fields. The first represents the title of the note type being used for Chinese vocabulary. Even though Chinese Getter is built to minimize unnecessary operations, it can still take a fraction of a second to realize that the current note type doesn't have any Chinese fields, so it will only try to run if the current note type matches configuration.

The next four represent the titles of the fields you'd like Anki to fill, e.g. Chinese Getter defaults to putting Chinese characters in the *Chinese characters* field in your note. If any of the fields are missing from your note, Chinese Getter won't try to fill them, so you don't need to turn it off when working with non-Chinese decks.

The last configurable field stores your API key from Forvo. Since it defaults to blank, **you'll need to get a key for Chinese Getter to get audio.**. If you don't have a key, Chinese Getter won't try to get audio, and if your key is invalid or expired, it'll let you know.

### "Chinese vocab note type"

*Defaults to "Chinese - Vocab"*

### "Chinese characters field"

*Defaults to "Chinese characters"*

### "Chinese animations field"

*Defaults to "Chinese characters - Animated"*

### "Chinese pinyin field"

*Defaults to "Chinese pinyin"*

### "Chinese sound field"

*Defaults to "Chinese sound"*

### "Forvo API key"

*Defaults to blank*