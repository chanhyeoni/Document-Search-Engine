"""
    Chang Hyun Lee
    N12218805
    CS6913 - HW03 - search.py

    The APIs for query search and evaluation
"""

import os
import indexer
import math
from re import sub
import heapq


class Heap(object):
# the class Heap uses Python's heapq data structure to store the top k+ scores
# of the pages with regards to the query

    def __init__(self, k, initial_tuple=None):
        # when initializing, it may or may not get the tuple consisting of (score, doc_id)
        # as a parameter. But it must have k as the maximum size of the data to store
        self.__k = k
        if initial_tuple: 
            # if initial tuple has the data, create the data and heapify it
            # if the size of the data is less than k, 
            self.__data = [initial_tuple]
            heapq.heapify(self.__data)
        else:
           self.__data = []

    def push(self, item):
        if(len(self.__data) < self.__k):
            # if the length of the data is less than k, 
            # (the number of data to store is less than k)
            # push the data; item mush be tuple (score, doc_id)
            heapq.heappush(self.__data, (item[0], item[1]))
        else:
            # since the data size is >= k, use heapq's pushpop method
            heapq.heappushpop(self.__data, (item[0], item[1]))

    def returnNLargest(self, n):
        # return the N largest values in the data stored in the heap.
        # if n is less than k, return n largest data
        # if not, return the data of size k
        if(n <= self.__k):
            return heapq.nlargest(n, self.__data)
        else:
            print "n is greater than the size of data"
            return heapq.nlargest(self.__k, self.__data)

    def isEmpty(self): return self.__k == 0

    def getData(self): return self.__data


def getListOfFilesOnFolder(folder_directory):
    # using the folder directory, go to ahtt directory and get the list of all filenames there
    # in case there are no ./ and / at the beginningand end of the directory, add it
    if folder_directory[0] != "/":
        folder_directory = ''.join(('/', folder_directory))

    if folder_directory[len(folder_directory)-1] != "/":
        folder_directory = ''.join((folder_directory, '/'))           

    ls_filenames = [ "."+folder_directory+f for f in os.listdir("."+folder_directory) if os.path.isfile(os.path.join("."+folder_directory,f)) ]

    return ls_filenames
    

def getMaxDocID(filename):
    # get the maximum number of document id
    # the filename must be the name of the file that contains the document hash table
    doc_hash_file = open(filename, 'r')
    lastLine = doc_hash_file.readlines()[-1]
    # readlines() will give you the list of the lines delmited by \n
    # negative indexing in python allows you to access the very last element
    return int(lastLine.split("#")[0])



def openTheDocHashTable(filename):
    # open the doc_hashtable document and return the doc_hashtable
    
    # Parameter
    # filename : the directory to the document hash table file
    # each line consists of the following:
    #                       doc_id#URL#document length

    # Returns
    # the hash table structure whose key is document id and whose value is the list
    # consisting of URL and the length of the page

    a_file = open(filename, 'r')
    doc_hashtable = {}
    for line in a_file:
        elements = line.split("#")
        doc_id = int(elements[0])
        url = elements[1]
        doc_length = int(elements[2][:-1]) # there is a \n, so need to subset this string
        doc_hashtable[doc_id] = [url, doc_length]
    a_file.close()
    return doc_hashtable


def getAllNamesOfFiles(folder_inverted_index):
    # go to the folder indicated by folder_inverted_index, 
    # and read all the names of the inverted index files within that folder
    # and distinguish to _data and _index files using the indexer.distingsuishFile method

    # Parameter:
    # folder_inverted_index: the directory to the inverted indices files 
    # as well as byte information --> word from the beginning of the inverted index file

    # Returns:
    # the list of filenames of inverted index
    # (the filename is the list consisting of starting and ending words)
    # the list of filneames containing byte information
    
    filenames = getListOfFilesOnFolder(folder_inverted_index)
    ls_data = indexer.distinguishFile(filenames, '_data')
    ls_byte = indexer.distinguishFile(filenames, '_byte')
        
    return ls_data, ls_byte
    

def findRightFileToRead(term, filenames_inverted_index, filenames_byte):
    # it helps you find the right file you have to read 
    # since the filenames_inverted_index has the starting and ending words in its filename,
    # use it to see whether a particular term is within that range

    # Parameter 
    # term : the term must be used for you to detect which file contains that term
    # filenames_inverted_index : the list of filenames of inverted index
    # filenames_byte : the list of filenames of byte information

    # filenames_inverted_index and filenames_byte have the same 'start-end' with different
    # end word of the file (e.g. the inverted index files end with _data, while
    # the byte files ends with _byte)

    # Returns 
    # the index where the right filenames of the inverted index and byte file
    # that contains the term are located in both lists.
    # both lists (filenames_inverted_index, filenames_byte) have the same locations
    # corresponding to the same file contents 

    idx = len(filenames_inverted_index)
    for filename in filenames_inverted_index:
        ls_words = filename.split("-")
        ls_words[1] = sub('\_data$', '', ls_words[1])
        if(ls_words[0] <= term and ls_words[1] >= term):
            idx = filenames_inverted_index.index(filename)
    
    return idx


def openTheRightFileAndReturn(term, right_inverted_index_file, right_byte_file):
    # after finding the right fielname, open the file and 
    # return the corresponding inverted list using the bytes (offset) of that particular term
    # found in the right_byte_file

    # Parameter 
    # term : the term must be used for you to detect which file contains that term
    # right_inverted_index_file : the name of the inverted index file you are looking for
    # right_byte_file : the name of the byte file file you are looking for

    # Returns
    # the string line that contains the term and its inverted list (e.g. word->{inverted list})
    
    # open both files
    inverted_index_file = open(right_inverted_index_file, 'r')
    byte_file = open(right_byte_file, 'r')
    
    right_line = ''
    right_byte = 0
    # read the byte file
    for line in byte_file:
        ls = line.split(":") # the line format word:byte
        if(term == ls[0]):
            # LOOK UPON THIS!!!!
            right_byte = int(ls[1])
            inverted_index_file.seek(right_byte)
            # seek method enables you to find the line whose offset from the beginning of
            # the file is indicated by right_byte
            right_line =  inverted_index_file.readline()
    
    return right_line


def split_line(line):
    # split the line read from the inverted index file and return word and its associated
    # inverted list

    # Parameter
    # line : formatted as follows:
    # word->{doc_id:[list of positions of the term], doc_id:[...], ...}

    # Returns
    # a word and its associated inverted list

    line = line.split("->")
    word = line[0]
    inverted_list = line[1][1:-1] 
    # since the inverted list structure is {...}, remove the brackets
    inverted_list = inverted_list.split(",")
    
    new_inverted_list = []
    for a_posting in inverted_list:
        a_posting = a_posting.split(":")
        doc_id = int(a_posting[0])
        ls_position = a_posting[1] # it is in the form of '[ ...]'
        ls_position = ls_position[1:-1]
        ls_position = ls_position.split(",")
        real_posting = indexer.Posting(doc_id, ls_position)
        new_inverted_list.append(real_posting)
    
    return word, new_inverted_list
        
MAXDOCID = getMaxDocID("./final_inverted_index_files/doc_hashtable.txt")
k_1 = 1.2
b = 0.75

def getNeededInvertedLists(query, folder_inverted_index):
    # for each term in the query, retreive the corresponding inverted list and return the 
    # inverted index that contains only the terms you need

    # Paramter
    # query : the string containing oen or more terms
    # folder_indverted_index : the folder directory that contains the final inverted index file as well as 
    # the file containing byte information

    # Returns
    # the inverted index that contains only the term

    # clear out some special characters
    query = sub('[^A-Za-z0-9]+', ' ', query.lower())
    # split this into the list of words
    words = query.split(" ")
    # get the names of all files needed to scan
    filenames_inverted_index, filenames_byte = getAllNamesOfFiles(folder_inverted_index)
    
    inverted_index = {}
    right_line = ''
    for term in words:
        # find the right files to read
        idx = findRightFileToRead(term, filenames_inverted_index, filenames_byte)
        # return the right line that contains the right word as well as the corresponding list
        if(idx != len(filenames_inverted_index)):
            right_line = openTheRightFileAndReturn(term, filenames_inverted_index[idx], filenames_byte[idx])
        # the line strucure : word->{doc_id:[inverted_list],doc_id:[inverted_list],...}
        if(right_line != ''):
        # parse the right_line such that it can be added in the hash table
        # but before that always check whether the word exists in the indexer
            word, new_inverted_list = split_line(right_line)
            # add them to the hash table
            if(inverted_index.has_key(word)):
                # this if structure is necessary since when the final inverted index may have two or more inverted lists
                # with the same word
                for i in range(len(new_inverted_list)):
                    inverted_index[word].append(new_inverted_list[i])
            else:
                inverted_index[word] = new_inverted_list
    
    return inverted_index
   

def nextGEQ(inverted_list, doc_id):
    # here the inverted list is already sorted out when the indexer is formed
    # so all that is needed to be done is to 
    # increment the doc_id by 1 and return the corresponding postings list.
    for a_posting in inverted_list:
        if(a_posting.getDocID() >= doc_id): return int(a_posting.getDocID())
    return MAXDOCID
         

def getFrequencyofTermInDoc(inverted_list, doc_id):
    # returns the frequency of the term in a particular document
    # inverted list contains a number of Posting objects
    
    for a_posting in inverted_list:
        if(a_posting.getDocID()==doc_id):
            return len(a_posting.getListPositions())
    return -1


def getLengthDoc(doc_id, doc_hashtable):
    # using the document hash table, access the value whose key is the doc_id
    # and accees the second element, which is the length of the document
    # just in case, always make it absolute value
    try:
        return math.fabs(int(doc_hashtable[doc_id][1]))
    except KeyError:
        return 0


def getAverageLengthDoc(doc_hashtable):
    # using the document hash table, estimate the average of the lengths of all the documents
    doc_length_sum = 0
    counter = 0 # counter will be the number of documents in the collection
    for doc_id in doc_hashtable.keys():
        # ls_elements = [url, document length]
        ls_elements = doc_hashtable[doc_id]
        doc_length = ls_elements[1]
        doc_length_sum = doc_length_sum + int(doc_length)
        counter = counter + 1
    return math.fabs(doc_length_sum/counter), counter


def getBigK(k_1, b, doc_length, avr_doc_length):
    # estimate the big K
    # K = k_1 *((1-b)+b*|d|/|d_avr|)
    return k_1 * ((1-b)*b*(doc_length/avr_doc_length))


def get_BM_25_formula(N, f_t, f_d_t, big_K, k_1):
    # use the BM25 formula to return the value of BM25 for a particular term
    return math.log((N-f_t+0.5)/(f_t+0.5)) * ((k_1+1)*f_d_t)/(big_K+f_d_t)


def evaluateQuery(inverted_index, doc_hashtable, k):
    # get the average estimate of all the documents'lengths and return the heap data structures
    # that contains the tuples consisting of document id and the score

    # Parmater
    # inverted_index : the inverted index whose keys are the terms of the query and whose values
    # are the associated inverted list with regards to each term
    # doc_hashtable : the hash table whose key is doc_id and whose value is URL of the document
    # k : the number of the largest scores and documents to report after evaluating the query

    # Returns
    # heap data structure that stores the top k tuples consisting of BM25 score and
    # the document id

    avr_doc_length, N = getAverageLengthDoc(doc_hashtable)
    
    # using the already made hash table, evaluate the queries using BM25 and return the rankings
    doc_id = 0
    new_doc_id = 0
    """ MUST USE BINARY HEAP INSTEAD OF HASH TABLE"""
    a_heap = Heap(k)
    if(inverted_index.keys()!=[]): 
    # this must be checked, since the query term may not be contained in all the document collections
        while(doc_id < MAXDOCID):
            doc_id = nextGEQ(inverted_index[inverted_index.keys()[0]], doc_id)
            if len(inverted_index.keys()) > 1:
                for a_word in inverted_index.keys()[1:]:
                # search for the doc_id that contains all the terms
                    next_doc_id = nextGEQ(inverted_index[a_word], doc_id)
                    if(next_doc_id==doc_id): continue

            if (new_doc_id <= doc_id):
                BM_25_doc = 0 # BM25 scores for each document
                for a_word in inverted_index.keys():
                    # f_t is the number of documents that contain term (a_word) 
                    # inverted_index[word_id] will return the list of Postings
                    # and the length of this list means the number of documents that have this term
                    f_t = len(inverted_index[a_word])
                    f_d_t = getFrequencyofTermInDoc(inverted_index[a_word], doc_id)
                    doc_length = getLengthDoc(doc_id, doc_hashtable)
                    big_K = getBigK(k_1, b, doc_length, avr_doc_length)
                    BM_25_doc = BM_25_doc + get_BM_25_formula(N, f_t, f_d_t, big_K, k_1)
                    a_tuple = (BM_25_doc, doc_id)
                    a_heap.push(a_tuple)
                    doc_id = doc_id + 1
            else: 
                new_doc_id = doc_id
              
    return a_heap
