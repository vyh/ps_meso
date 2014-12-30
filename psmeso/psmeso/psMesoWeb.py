# coding: utf-8

''' P.S.: Meso
    ("poesis spinea")
~created by Nicki Hoffman, 2013-04-17 (Python 3.3)
For noncommercial use; sharing & modifying welcome with attribution.

This program will generate a mesostic from a given source file, seed text,
and number of iterations. If it cannot complete a mesostic (i.e., for at
least one letter in the seed, there is no word in the source that meets
the criteria), it will print a message and the incomplete mesostic.

A true mesostic would use a word no more times than it occurs in the
oracle; this program may, however, when it has to loop back to the
beginning to find suitable words.
'''

import random

# create global variables
ORACLE, SEED, ITERS, ODDS = [], '', 1, 2
OLENGTH, SEEDLIM = 0, 0
lastCap, nowCap, nextCap = ' ', ' ', ' '
BRTYPE = ''


def mesosticize(words, seed, iters, odds, strip_punct, brtype):
    initializeVars(words, seed, iters, odds, strip_punct, brtype)

    meso, fail = mesostic()
    message, meso = formatHtml(meso, fail)

    return (message, meso)


def initializeVars(words, seed, iters, odds, strip_punct, brtype):
    """ (str, str, int, int, bool) -> NoneType

    Cleans the inputs and uses them to initialize the global variables.
    """
    global ORACLE, SEED, ITERS, ODDS, OLENGTH, SEEDLIM, lastCap, nowCap, nextCap
    global BRTYPE
    PUNCT = u'.,;:?/|\\\'\"-!%^&*()[]{}<>_=+~`@#$%¡¿«»–—‘’“”'

    ''' Initialize the stanza break type - random or after words '''
    BRTYPE = brtype

    ''' Initialize the number of times to repeat the seed text (spine)'''
    ITERS = iters

    ''' Initialize the odds determining sparsity of fill text '''
    ODDS = odds

    ''' Initialize the oracle text '''
    words = words.lower().split()

    # If the user checked the "strip punctuation" box, do so (oracle only)
    if strip_punct:
        for i in range(len(words)):
            words[i] = words[i].strip(PUNCT)

    # Copy non-empty-string items to the final list, excluding numbers
    # (this is to remove section numbers like those in Song of Myself)
    parsed = []
    for i in words:
        if i and not i.isdigit():
            parsed.append(i.lower())
    ORACLE = parsed

    ''' Initialize the seed text, stripping punctuation and spaces,
        and modifying for random or word stanza breaks '''
    SEED = seed.strip().lower()
    for ch in PUNCT:
        SEED = SEED.replace(ch, '')
    if BRTYPE == 'random':
        SEED = SEED.replace(' ', '')
    else:
        SEED += ' '

    ''' Set the oracle list length and seed index limit constants '''
    OLENGTH = len(ORACLE)
    SEEDLIM = len(SEED) - 1

    ''' Initialize the vars tracking last, current, & next spine letter '''
    lastCap, nowCap, nextCap = ' ', SEED[0], SEED[1]


def mesostic():
    ''' (list of str, int) -> str
    Given an oracle, seed text (global), and the number of iterations,
    make a mesostic.
    '''

    place, k, spine = 0, 0, ''
    meso = ''
    fail = False

    # Runs the generator iters times on the seed text.
    # If it cannot complete a single iteration, it will error out
    for i in range(ITERS):
        for j in range(len(SEED)):
            oldPlace = place
            oldSpine = spine
            oldK = k
            spine, place, k, fail = nextSpineWord(j, place, i)
            if fail:
                break
            fill = fillText(oldPlace, place-1, oldSpine, spine, oldK, k)
            meso += (fill + spine)
        if fail:
            break

    return (meso, fail)


def nextSpineWord(j, place, iteration):
    ''' (int, int) -> str

    Finds the spine word for the next line of the mesostic.

    Go through the letters of the seed one by one.
`   If a word contains the current letter ONCE, check that it meets
    rule 1; if the the prev letter doesn't appear before the current
    AND the next don't appear after the current, it is the word.
    '''

    global lastCap, nowCap, nextCap
    nowCap = SEED[j]
    # On the first seed letter of the first iteration, leave lastCap a space;
    # after, it's the prev. char
    if iteration != 0 or j != 0:
        lastCap = SEED[j-1]
    # On the last seed letter in the last iteration, make nextCap a space;
    # before, it's the next char
    if iteration != ITERS-1 or j != SEEDLIM:
        nextCap = SEED[(j+1)%(SEEDLIM+1)]
    else:
        nextCap = ' '

    incomplete = False
    i = 0
    start = place

    # Find the next word with one instance of the spine letter
    fits = False

    # but if the spine char is a space, return a blank spine word
    if nowCap == ' ':
        word = ' '
        fits = True
    
    while fits == False:
        word = ORACLE[place]
        while word.count(nowCap) != 1:
            place += 1
            if place == OLENGTH:
                place = 0
            if place == start:
                incomplete = True
                break
            word = ORACLE[place]

        # Move past the current word so it's not checked repeatedly
        place += 1
        if place == OLENGTH:
            place = 0

        if incomplete:
            word = ''
            break

        # Check that it meets mesostic rule #1
        i = word.index(nowCap)
        if word.find(lastCap, 0, i)==-1 and word.find(nextCap, i+1)==-1:
            fits = True

    return (word, place, i, incomplete)


def fillText(place1, place2, spine1, spine2, k1, k2):
    ''' (int*6) -> str

    After the spine word on one line and before the spine word on the next
    add some words that meet rules #1 and #2. Make it a bit random
    (qualified words to include and line breaks to place).
    '''

    limit1 = 45 - len(spine1[k1+1:])
    limit2 = 45 - len(spine2[:k2])
    line1, line2 = '', ''

    # correct for possibility that place2 is at the beginning of
    # the oracle and place1 at the end
    effectiveP1 = place1
    if place1 > place2:
        effectiveP1 -= OLENGTH

    # Old line (only if there's a previous spine word):
    # Word must appear between prev & next spine words in oracle;
    # user-defined odds determine whether to try to add the word; if yes,
    # the word must not contain the prev or next spine letter and
    # must be short enough to fit within the line limit. If yes, it's added.
    if spine1 and spine1 != ' ':
        while effectiveP1 < place2 and random.randrange(ODDS) == 0:
            word = ORACLE[place1]
            if lastCap not in word and nowCap not in word:
                if len(line1) + len(word) <= limit1:
                    line1 += ' '+word
            effectiveP1 += 1
            place1 += 1
            if place1 == OLENGTH:
                place1 = 0

    # Old line done. Add line break.
    line1 += '\n'

    # Randomly add another line break (new stanza). Odds: 1 in 7.
    # Only if stanza break type is random.
    if BRTYPE == 'random' and random.randrange(1, 8) < 2:
        line1 += '\n'

    # If next spine word is blank & break type is after words, add break.
    if spine2 == ' ':
        line2 += ' '
    # New line (only if there's a next spine word).
    # Same rules, new line. Should these be a subfunction?
    elif spine2:
        while effectiveP1 < place2 and random.randrange(ODDS) == 0:
            word = ORACLE[place1]
            if lastCap not in word and nowCap not in word:
                if len(line2) + len(word) <= limit2:
                    line2 += word+' '
            effectiveP1 += 1
            place1 += 1
            if place1 == OLENGTH:
                place1 = 0

    return (line1 + line2)


def formatHtml(text, fail):
    """ (str) -> list of str

    Clothes the capitalized letter in each line with html bold tags,
    converts the mesostic string to a list splitting \n new lines into
    new empty-string elements (which will be displayed as blank lines
    by the template) so that it is ready to print in html <pre> tags.

    The Django template will use a for loop to display the list element
    by element (one element per line), as the pure Python version does.
    """

    text = list(text.strip().split('\n'))
    output = []
    longest = 0
    lineLen = []
    s = 0

    for line in text:
        if line:
            # Find the spine letter
            i = line.index(SEED[s])
            s += 1
            if s > SEEDLIM:
                s = 0
            # Record pre-spine length and update longest length;
            # for adding spaces later so the spine lines up
            length = len(line[:i])
            lineLen.append(length)
            longest = max(longest, length)
            # Capitalize the spine letter and clothe it in bold tags
            spine = '<b>' + line[i].upper() + '</b>'
            output.append(line[:i] + spine + line[i+1:])
        else:
            # (It's a blank line)
            lineLen.append(0)
            output.append(line)

    # Now, add spaces to line up the spine
    for i in range(len(output)):
        spaces = ' ' * (longest - lineLen[i])
        output[i] = spaces + output[i]

    # Now create the introductory message (blank if successful)
    message = 'Well glonce-a-day, it worked! Here you go:'
    if fail:
        message = 'Could not complete the requested mesostic. The spine '+ \
                  'might not work with that oracle, or it might work once '+ \
                  'but not be able to repeat.<br /><br />I got this far:'

    return (message, output)
