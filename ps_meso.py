# coding: utf-8

''' P.S.: Meso
    ("poesis spinea")
~created by Nicki Hoffman
~original    2013-04-17 (Python 3.3)
~refactored  2014-12-23 (Python 2.7)
~last update 2014-12-26

For noncommercial use; sharing & modifying welcome with attribution.

This program will generate a mesostic from a given source & seed text
and number of iterations. Its framework should provide default values
for other parameters. If it cannot complete a mesostic (i.e., for at
least one letter in the seed, there is no word in the source that meets
the criteria), it will print a message and the incomplete mesostic.

A true mesostic would use a word no more times than it occurs in the
oracle; this program may, however, when it has to loop back to the
beginning to find suitable words. '''

from random import randrange


class Mesostic(object):
    ''' An instance of a mesostic poem. The poem variable holds the
        mesostic itself; others contain information about the poem's
        construction - source and spine text, number of iterations of
        the spine, where to place line breaks (randomly or between
        words), how sparse to make wing text, and whether creation of
        the mesostic succeeded or failed with these parameters. '''

    def __init__(self, text, seed, iters, sparsity, strip_punct, break_type):
        ''' Initializes a Mesostic object. 
            Takes (str, str, int, int, bool, str). '''
        self.poem = ""
        self.fail = False
        self.iters = iters
        self.sparsity = sparsity
        self.random_br = break_type == 'random'
        PUNCT = u'.,;:?/|\\\'\"-!%^&*()[]{}<>_=+~`@#$%¡¿«»–—‘’“”'

        # self.seed = strip whitespace around seed, strip all punctuation
        self.seed = "".join(filter(lambda x: x not in PUNCT, seed.strip().lower()))
        if self.random_br:
            self.seed = self.seed.replace(' ', '')
        else:
            self.seed += ' '

        # source text - split into list, strip punct if requested
        if strip_punct:
            text = [word.strip(PUNCT) for word in text.lower().split()]
        else:
            text = text.lower().split()
        self.source = filter(None, text)

        self.make_poem()

    def make_poem(self):
        ''' Generates poem text from the Mesostic's instance variables.
            If it cannot find suitable spine words for all spine letters,
            generates as much as possible & sets self.fail True. '''
        word = 0
        for i in range(self.iters):
            for line in range(len(self.seed)):
                word = self.make_line(line, word)
                if self.fail: break
                self.poem += '\n'
                # 7 is a magic #; didn't want stanza breaks tied to sparsity
                if self.random_br and not randrange(7): self.poem += '\n'
            if self.fail: break

    def make_line(self, line, word):
        ''' Creates and appends the next line to the poem.
            Returns the index of the last word considered.
            
            (int, int) -> int '''
        # if spine letter is space, line is blank - add space and return
        if self.seed[line] == ' ':
            self.poem += ' '
            return word
        
        # spine word index, index of spine letter inside spine word
        spine_word, self.fail = self.find_next_spine_word(word, line)
        if self.fail: return spine_word
        i = self.source[spine_word].index(self.seed[line])
        
        # left hand wing words
        limit = 45 - len(self.source[spine_word][:i])
        wing = self.make_wing_words(limit,
                                    word,
                                    spine_word,
                                    self.seed[line],
                                    self.seed[line - 1])[0]
        if wing: self.poem += wing + ' '

        # add spine word
        self.poem += self.source[spine_word]
        
        # find next spine word to know where to stop right wing
        # note: end of subset of words could come before beginning
        word = self.find_next_spine_word((spine_word + 1) % len(self.source),
                                         line)[0]
            
        # right hand wing words
        limit = 45 - len(self.source[spine_word][i+1:])
        wing, word = self.make_wing_words(limit,
                                          (spine_word + 1) % len(self.source),
                                          word,
                                          self.seed[line],
                                          self.seed[(line+1) % len(self.seed)])
        if wing: self.poem += ' ' + wing

        return word

    def find_next_spine_word(self, start, s):
        ''' Finds index of next spine word. Returns index and boolean
            (True if a spine word could not be found, False otherwise).

            (int, int) -> (int, bool) '''
        i = start
        while not self.is_next_spine_word(self.source[i], s):
            i = (i + 1) % len(self.source)
            if i == start: return i, bool("failed")
        return i, bool()        

    def is_next_spine_word(self, word, i):
        ''' Checks whether the word meets requirements for the next
            spine word. Returns True iff the word contains next spine
            letter exactly one time, does not contain previous spine
            letter before the next spine letter, and does not contain
            subsequent spine letter after next spine letter.
            
            (str, int) -> bool '''
        if word.count(self.seed[i]) != 1:
            return False
        elif len(self.seed) > 1:    # don't compare spine letter to itself
            if word.count(self.seed[i-1], 0, word.index(self.seed[i])) > 0:
                return False
            elif word.count(self.seed[(i+1) % len(self.seed)],
                                          word.index(self.seed[i])) > 0:
                return False
        return True

    def make_wing_words(self, length, i, end, char1, char2):
        ''' Generates wing text for half of a line of the mesostic.

            (int, int, int, char, char) -> (str, int)
            
            Takes max length in chars, start and end indices of usable
            subset of source, and the book-end spine letters; returns
            string of wing words and index of last word considered. '''
        wing = ''
        while len(wing) < length and i != end:
            word = self.source[i]
            if word.count(char1) == 0 and \
               word.count(char2) == 0 and \
               len(wing + word + ' ') <= length and \
               not randrange(self.sparsity):
                wing += word + ' '
            i = (i + 1) % len(self.source)
        return wing.strip(), i

    def format_html(self):
        ''' Preformats the mesostic for display in an html page.
            Returns a message saying whether the mesostic was created
            successfully and a list of the mesostic's formatted lines.

            NoneType -> (str, list of str) '''
        text = self.poem.strip().split('\n')
        html = []
        longest = 0
        spaces = []
        s = 0

        for ln in text:
            if ln.strip():
                i = ln.index(self.seed[s])        # find the spine letter
                longest = max(longest, len(ln[:i]))
                spaces.append(len(ln[:i]))        # record pre-spine length
                # capitalize spine letter & clothe it in bold tags; append line
                html.append(ln[:i] + '<b>' + ln[i].upper() + '</b>' + ln[i+1:])
                s = (s + 1) % len(self.seed)
            else:
                spaces.append(0)                  # (else it's a blank line)
                html.append(ln)
                # if line breaks are random, no spine ch will indicate blank
                if self.seed[s] == ' ': s = (s + 1) % len(self.seed)
                
        # left-pad each line with spaces to line up the spine
        # rstrip() to clear the spaces from blank lines
        spaces = [longest - s for s in spaces]
        html = [(' '*spaces[i] + html[i]).rstrip() for i in range(len(html))]
        
        if self.fail:
            message = 'Could not complete the requested mesostic. The spine '+\
                      'may not work with that oracle, or it might work once '+\
                      'but not be able to repeat.<br /><br />I got this far:'
        else:
            message = 'Well glonce-a-day, it worked! Here you go:'

        return (message, html)
