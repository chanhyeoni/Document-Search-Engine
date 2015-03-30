"""
    Chang Hyun Lee
    N12218805
    CS6913 - HW03 - indexer.py

    The APIs for building an inverted index
"""

import urllib2, sets, bs4, os, re, gzip, subprocess, sys

class Document:
    # the class for the Document object
    # after parsing the _data and _index files, the Document object will 
    # be created in order to store the url (with 'http://' appended) and
    # and the html raw text
    def __init__(self, url, text):
        # get the address needed
        self.__url = 'http://' + url
        self.__text = text
            
    def getURL(self):
        # return the url of the Document page
        return self.__url
    
    def getListOfWords(self):
        # get the list of normalized words using the regular expression as well as 
        # the BeautifulSoup 
        soup = bs4.BeautifulSoup(self.__text)
        raw_text = soup.get_text()
        ls_words = re.split('\W+', raw_text.encode('ascii', 'ignore').lower())
        
        return ls_words
  
      
class Intermediate_Posting:
    # the class for the intermedaite Posting
    # the attributes are the word id, the document id, and the list of positions 
    # where that particular term occurs in the list of words that the document has
    # in this case, the list of words contains all the terms from the plain text fields
    # of the html (whether it is in header or <p> tag part)
    # and the list of words is the list data structure
    def __init__(self, doc_id, word_id, ls_positions=None):
        self.__doc_id = doc_id
        self.__word_id = word_id
        self.__ls_positions = ls_positions
        
    def getDocID(self): return self.__doc_id
    def addPosition(self, pos):
        # add the postion of the word to the document
        self.__ls_positions.append(pos)

    def getPositionOfWord(self, word):
        try:
            return self.__ls_positions.index(word)
        except ValueError:
            return -1

    def getListPositions(self): return self.__ls_positions
    def getFrequency(self): return len(self.__ls_positions)


class Posting:
    # the class for Posting
    # will be used for the sorting phase, and 
    def __init__(self, doc_id, ls_positions=None):
        self.__doc_id = doc_id
        self.__ls_positions = ls_positions
    
    def getDocID(self): return self.__doc_id
    def getListPositions(self): return self.__ls_positions


class Pointer:
    # the class for pointers. This will be used to make 
    # the lexicon have the pointers to the inverted list
    def __init__(self, inverted_list): self.__obj = inverted_list
    def get(self):    return self.__obj
    def set(self, new_inverted_list):      self.__obj = new_inverted_list


class Lexicon_Object:
    # the class for Lexicon dictionary
    def __init__(self, word_id, inverted_list):
        # the inverted list whose key is the word_id must be wrapped in the Pointer object
        # to make a reference to it, not the copy of it
        self.__ptr_inverted_list = Pointer(inverted_list)
        self.__word_id = word_id

    def getWordID(self): return self.__word_id
    def getPtrInvertedList(self): return self.__ptr_inverted_list


def distinguishFile(filenames, pattern):
    # since there are different types of files, you need to distinguish the files using 
    # the pattern of the name.
    # e.g. : the files ending with __index just contains the byte length
    # and since it may contain duplicate files, use Set instead of list
    # but in the final version, return list
    aSet = sets.Set()
    for aFileName in filenames:
	if pattern in aFileName:
		aSet.add(aFileName)
    a_ls = list(aSet)
    a_ls.sort()
    
    return a_ls
    # sort it such that the elements in the __data and __index files are matched with each other 


def parse_url_and_web_page_according_to_byte(web_pages, indexes):
    # parse the __data and __index pages so that you can obtain a set of invidiual pages
    # and their corresponding URLs. The __index files contain the length of each page
    # in byte (one character), so we can utilize it when splitting the content (string) 
    # the __data page into multiple web pages
    # in the end, it returns two lists, one that has the web page contents (html text)
    # and the other that has the URLs
    
    # web_pages and indexes (parameters) must be gzip object
    
    ls_addresses = indexes.read().split("\n") 
    # get the list of addresses along with its page length, and other stuffss
    web_pages_contents = web_pages.read()
    # read the web pages
    
    # create empty lists for URLs as well as their pages
    url_ls = []
    web_page_ls = []    
    
    start = 0 # the start index of the web page
    for address in ls_addresses:
        if (address != ''):
            obj = address.split(" ")
            url = obj[0]
            page_length = int(obj[3])
                    
            a_web_page = web_pages_contents[start:page_length]
            # since page_length is in bytes (one character), and the string
            # as a list of chracters, considers one char as one element, indexing 
            # will give the correct amount of content
            
            url_ls.append(url)
            web_page_ls.append(a_web_page)
            
            start = page_length 
            # assign page length to start so that the next web page
            # will start from that page length value

    return url_ls, web_page_ls


def getNecessaryIntermediatePosting(inverted_list, doc_id):
	for i in range(len(inverted_list)):
		if(inverted_list[i].getDocID() == doc_id):
			return inverted_list[i], i
	return None, len(inverted_list)


def create_lexicon_and_inverted_list(lexicon, ls_words, word_id, doc_id):
    # the function that creates the inverted list for each corresponding word and document 
    # the raw_text should be normalized before putting into text
    
    for a_word in ls_words:
        if(a_word != ''):
            if lexicon.has_key(a_word):
            # if the lexicon already has the word, just add the position of that word
            # in that particular document to the inverted index
            # lexicon[a_word].getPtrInvertedList().get() is inverted list
                inverted_list = lexicon[a_word].getPtrInvertedList().get()
                intermediate_posting, idx = getNecessaryIntermediatePosting(inverted_list, doc_id)
                if(intermediate_posting !=None):
                    if ls_words.index(a_word) not in intermediate_posting.getListPositions(): # this means there is no word on that thing
                        intermediate_posting.addPosition(ls_words.index(a_word))
                        inverted_list[idx] = intermediate_posting
                        lexicon[a_word].getPtrInvertedList().set(inverted_list)
                else:
                    a_new_intermediate_posting = Intermediate_Posting(doc_id, word_id, [ls_words.index(a_word)])
                    inverted_list.append(a_new_intermediate_posting)
                    lexicon[a_word].getPtrInvertedList().set(inverted_list)

            else:
                # if the lexicon doesn't have the word, create a new one for lexicon object
                # as well as new Posting for the inverted index
                # the inverted index has the word as the key
                inverted_list = [Intermediate_Posting(doc_id, word_id, [ls_words.index(a_word)])]
                lexicon[a_word] = Lexicon_Object(word_id, inverted_list)
                word_id = word_id + 1
        else: continue

    return lexicon, word_id


def write_intermediate_file_to_the_disk(lexicon):
    # the fucntion that lets you write to the path directory that you have 
    # the files that were written here will be used for merge sorting the dictionary
    
    # this function will be used for the following task: storing the intermediate posting
    # and return the name of the new file in the end
    
    # check whether the path already exists; if not, create a new one
    if not os.path.exists("./intermediate_postings_folder/"): os.makedirs("./intermediate_postings_folder/")
    """ write to the disk, and the sorting phase will be done in """
    
    # open a new file
    # the filename must be the range from the starting word to the last word
    # e.g : its filename --> a-cz.txt
    # will be beneficial when querying (it can help us access the files that are only necessary)
    
    start_word = lexicon.keys().sort()[0]
    end_word = lexicon.keys().sort()[len(lexicon.keys())-1]
    aFile = gzip.open("./intermediate_postings_folder/" + start_word + '-' + end_word+"_temp", 'wb')
    # since this new intermdatie file will be deleted after the sorthing phase, 
    # (the sorted file will be the new file and will be used for final merge)
    # the newly sorted file don't have _temp at the end
    new_filename = aFile.name

    # when writing to the file, the word_id does not need to be stored
    # as this will cause more complexity when it goes to the sorting phase
    for i in range(len(lexicon.keys())):
        word = lexicon.keys()[i]
        inverted_list = lexicon[word].getPtrInvertedList().get()
        # things_to_write is the word and the list of itermediate postings
        things_to_write = str(word) + "->{" 
        for idx in range(len(inverted_list)):
            things_to_write = things_to_write + str(inverted_list[idx].getDocID()) + ":" + str(inverted_list[idx].getListPositions())
            if(idx != len(inverted_list)-1): things_to_write = things_to_write + ","
        things_to_write = things_to_write + "}"
        aFile.write(things_to_write + "\n")

    aFile.close()

    return new_filename


def sort_intermediate_file(new_filename):
    # using the new_filename above, open that intermediate file
    # and sort the file using the unix sort command
    # since the sorted content must be stored somewhere,
    # this function creates a new file whose filename is in the formate of 
    # 'start word'-'end word'

    a_temp_file = gzip.open(new_filename, 'rb')
    a_temp_file_content = a_temp_file.read()

    unzipped_filename = new_filename + "_unzipped"
    a_unzipped_file = open(unzipped_filename, 'wb')
    a_unzipped_file.write(a_temp_file_content)

    a_temp_file.close()
    a_unzipped_file.close()

    # sort is done by calling unix sort command
    sort_command_line = 'sort ' + unzipped_filename
    another_new_filename = re.sub('\_temp$', '', new_filename)
    # another_new_filename does not have _temp at the end
    subprocess.call(sort_command_line.split(), stdout=open(another_new_filename, 'w'))

    # delete the old file (including the temporary and unzipped ones) using the rm command 
    delete_command_line = 'rm -Rf ' + new_filename
    subprocess.call(delete_command_line, shell=True)

    delete_command_line = 'rm -Rf ' + unzipped_filename
    subprocess.call(delete_command_line, shell=True)


def create(doc_id, word_id, doc_hash, lexicon, url_ls, a_web_page_ls):
    # the function create creates all the necessary data structures
    # a_document is Document class
    for i in range(len(url_ls)):
        # create a document object
        a_document = Document(url_ls[i], a_web_page_ls[i])
        # used the Document class's getListofWords function to return the list of words contained
        ls_words = a_document.getListOfWords()
        doc_length = len(ls_words) 
        # this is necessary. Although document passed the URLError and ValueError test, the document may not have the content
        # so if the above condition is true, you create the postings
        # add the new document to the hash table of the document and increment the doc_id
        doc_hash[doc_id]=[a_document.getURL(), doc_length]

        # call the function that creates the lexicon and inverted index  
        lexicon, word_id = create_lexicon_and_inverted_list(lexicon, ls_words, word_id, doc_id)
        print " document " + str(doc_id) + " is done!"
        # increment the document id number    
        doc_id = doc_id + 1
    
    return lexicon, doc_hash, doc_id
    

def create_intermediate_postings_N_document_hashtable_N_lexicon(ls_data, ls_index, file_size_limit):
    # after getting the filenames of data and indices, this function parses them such that
    # you would be given the list of URLs and associated web pages
    # and build the intermediate postings as well as the document hash file and lexicon

    # read the web pages and return the list of the pointers pointing to the web pages

    # initalize the empty hash tables
    doc_hash = {}
    lexicon = {}
    doc_id = 0
    word_id = 0
    new_inverted_index = {}
    intermediate_posting_doc_num_ls = []

    for i in range(len(ls_data)):
        # uncompress the gzipped file
        web_pages = gzip.open(ls_data[i], 'r')
        indexes = gzip.open(ls_index[i], 'r')         
        
        # parse the _data and _index pages so that you get a list of the URLs as well as
        # the corresponding contents to the URLs
        url_ls, a_web_page_ls = parse_url_and_web_page_according_to_byte(web_pages, indexes)
        
        for a_url in url_ls:
            try:
                # try to open the url and if it doens't throw any status error, 
                # start creating the positings, lexicon, etc.
                url_check = urllib2.urlopen(a_url)
            except urllib2.HTTPError:
                # if url opening is causing an HTTP error, skip it
                a_web_page_ls.remove(a_web_page_ls[url_ls.index(a_url)])
                url_ls.remove(a_url)
            except ValueError:
                # even though the valueError is raised, since this is 
                # about the unknown url type error, continue
                continue
            except urllib2.URLError:
                a_web_page_ls.remove(a_web_page_ls[url_ls.index(a_url)])
                url_ls.remove(a_url)

        print "finished filtering "+ str(i) + "!"
        # create the data structures
        lexicon, doc_hash, doc_id = create(doc_id, word_id, doc_hash, lexicon, url_ls, a_web_page_ls)
        # if the size of lexicon is over the number indicated by the parameter file_size_limit, 
        # sort and write the intermedaite postings into the file
        if(sys.getsizeof(lexicon) >= file_size_limit):
            # once the size of lexicon exceeds 1000000 bytes, create a new file
            # write the content to the temporary file
            # sort the file using the unix sort command
            
            # write to the disk
            new_filename = write_intermediate_file_to_the_disk(lexicon)

            print "start sorting "+ new_filename + "!"
            # sort the file's content, write this to the new file, and remove it
            sort_intermediate_file(new_filename)
            print "finished sorting "+ new_filename + "!"
                     
            lexicon = {}
            new_inverted_index = {} 
            # empty the new_inverted_index and lexicon so that we can flush the data to the disk
            # and start the new one
        
        web_pages.close()
        indexes.close()
    
    new_filename =  write_intermediate_file_to_the_disk(lexicon)
    print "start sorting "+ new_filename + "!"
    # sort the file's content, write this to the new file, and remove it
    sort_intermediate_file(new_filename)
    print "finished sorting "+ new_filename + "!"
    
    # create the final folder (final_inverted_index_files)
    directory_final_folder = "./final_inverted_index_files/"
    if not os.path.exists(directory_final_folder): os.makedirs(directory_final_folder)    
    
    # write the document hash table to the final folder directory
    doc_hashfile = open(directory_final_folder + 'doc_hashtable.txt', 'w')
    for doc_id in doc_hash.keys():
        # the first object of the value of the doc_hash is URL
        # the second object is the length of the document
        doc_hashfile.write(str(doc_id) + "#" + str(doc_hash[doc_id][0]) + "#" + str(doc_hash[doc_id][1]) + "\n")
    doc_hashfile.close()
        
    # write the lexicon hash table to the final folder directory
    lexicon_file = open(directory_final_folder + 'lexicon.txt', 'w')
    for aWord in lexicon.keys():
        lexicon_file.write(aWord + ":" + str(lexicon[aWord].getWordID()) + "\n")

    lexicon_file.close()


def makeByteFile(final_inverted_index_file_filename):
    # using the file directory passed as parameter (it is the inverted index file name),
    # open the file, read it, and estiamte the offset of each word, and store that information into a new file
    # the newly created file must be in the same directory (./final_inverted_index_files)

    byte = 0
    # final_inverted_index_file_filename ends with _data, so for the byte filename, this part has to be replaced with _byte
    byte_filename = re.sub('\_data$', '_byte', final_inverted_index_file_filename)
    a_byte_file  = open(byte_filename, 'w')
    with open(final_inverted_index_file_filename, 'r') as f:
        for line in f:
            # line : word->{doc_id:[list of positions], ...}
            ls_components = line.split("->") 
            word = ls_components[0] 
            # next, wrtie the offset of each word to the a_byte_file
            byte_things_to_write = word + ":" + str(byte) + "\n"
            a_byte_file.write(byte_things_to_write)        
            # incremet the byte for the next word
            byte = byte + len(line)

    a_byte_file.close()

    
def final_sort_and_write_to_the_disk(file_size_limit):
    # after storing all the intermeidate files, do the final sort and store the data
    # under the directory "./final_inverted_index_files", which also contains the 
    # document hashtable as well as lexicon file

    # the final inverted index file must end with _data
    # the name of the final inverted index file must in the formate of 'start word'-'end word'
    # e.g. a-cz_data

    # if the data is too large to be stored in one file, set the data limit
    # if the file size exceeds the number indicated by file_size_limit, create a new file and do the final sort

    # after getting the final inverted index files, create another files whose names end 
    # with _byte
    # this file stores the informmation about the file 
    # the byte file name should also be in the following format 'start word'-'end word'
    # e.g. a-cz_index

    # here the approach is to use unix merge sort.
    # after storing all the intermediate positings into the disk, 
    # the unix sort will be carried out to execute sorting


    # get the names of all the files
    intermediate_path = "./intermediate_postings_folder/"
    intermediate_filenames = [ intermediate_path+f for f in os.listdir(intermediate_path) if os.path.isfile(os.path.join(intermediate_path,f)) ]
    if ('.DS_Store' in intermediate_filenames): intermediate_filenames.remove('.DS_Store')

    # make the argument 
    command_line = 'sort '
    if(len(intermediate_filenames)>=2): # if there is only more than one file, use merge sort option
        command_line = command_line + '-n -m '

    file_size_sum = 0 # will be used to check the size of the files to be written to one final inverted index file
    start_word = []
    end_word = []
    for i in range(len(intermediate_filenames)):
        command_line = command_line + intermediate_filenames[i] + ' '
        ls_words = intermediate_filenames[i].split("-")
        start_word.append(ls_words[0])
        end_word.append(ls_words[1])

        # sum up all the size of files to read 
        file_size_sum = file_size_sum + os.path.getsize(intermediate_filenames[i])

        if(file_size_sum >= file_size_limit):
            # always check whether the final_inverted_index_files directory exists
            if not os.path.exists('./final_inverted_index_files/'): os.makedirs('./final_inverted_index_files/')  
            # create a new final inverted index file and store the inverted index file
            final_inverted_index_filename = start_word[0]+'-'+end_word[len(end_word)-1]+"_data" 
            # MAKE SURE YOU PUT _data AT THE END
            subprocess.call(command_line.split(), stdout=open('./final_inverted_index_files/'+final_inverted_index_filename, 'w'))

            # call the byte file to store the infromation about offset of each word from the beginning of its inverted index file
            makeByteFile('./final_inverted_index_files/'+final_inverted_index_filename)

            file_size_sum = 0

    # you still have to call sorting command to sort the remaining files of the files whose size is less than file_size_limit
    if not os.path.exists('./final_inverted_index_files/'): os.makedirs('./final_inverted_index_files/')  
    # create a new final inverted index file and store the inverted index file
    final_inverted_index_filename = start_word[0]+'-'+end_word[len(end_word)-1]+"_data"
    subprocess.call(command_line.split(), stdout=open('./final_inverted_index_files/'+final_inverted_index_filename, 'w'))
    # call the byte file to store the infromation about offset of each word from the beginning of its inverted index file
    makeByteFile('./final_inverted_index_files/'+final_inverted_index_filename)

