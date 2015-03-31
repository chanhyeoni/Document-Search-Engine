"""
  Chang Hyun Lee
  N12218805
  CS6913 - HW03 - main.py

   Given the final inverted index folder (made after the indexing process)
   You must put the main.py and the search.py in the same directory to enable the execution
   You must also put the final_inverted_index_files folder in the same directory that is included in this zipped file

   Open the command shell. Make it such that you are in the same directory as where this file is.

   Then, type python main.py

   And answer the questions
   
   When executed, it will show you the URL and the BM25 score of each document
"""


import tarfile
import indexer
import time

def index(zipped_filename):
    # read the files in the tar file
    tar = tarfile.open(zipped_filename, 'r')
    tar.extractall()
    filenames = tar.getnames() # get the name of the folder that has been unzipped
    # get the file containing only the actual web pages
    ls_data = indexer.distinguishFile(filenames, '_data')
    ls_index = indexer.distinguishFile(filenames, '_index')
        
    # create the three data structures (intermediate postings, document hashtable, and lexicon)
    # and save to the disk
    intermeidate_file_size_limit = 1000000
    indexer.create_intermediate_postings_N_document_hashtable_N_lexicon(ls_data, ls_index, intermeidate_file_size_limit)
    
    # use the unix sort command to sort the in the intermediate postings files
    # and write to the disk again to the final folder
    file_size_limit = intermeidate_file_size_limit*4
    indexer.final_sort_and_write_to_the_disk(file_size_limit)
    

from search import *

def search(query, k, how_many):
    # the main function for search query and display the relevant document pages

    # open the file containing document hash table and return the document hash table
    doc_hashtable = openTheDocHashTable("./final_inverted_index_files/doc_hashtable.txt")

    # get the necessary inverted index that contains only the terms in the query
    inverted_index = getNeededInvertedLists(query,'./final_inverted_index_files/')

    # return the heap that has the scores of the top k documents
    a_heap = evaluateQuery(inverted_index, doc_hashtable, k)
    if(a_heap.isEmpty() != True):
      a_heap_k_largest = a_heap.returnNLargest(how_many)
      # display
      for a_tuple in a_heap_k_largest:
        doc_id = a_tuple[1]
        print doc_hashtable[doc_id], a_tuple[0]
    else:
      print "No document is found!"


if __name__=="__main__":
    """
    print "==============INDEXING=============="
    zipped_filename = raw_input("type the zipped filename : ")
    start_time =  time.clock()
    index(zipped_filename)
    end_time = time.clock()
    print "run-time : " + str((end_time - start_time)/float(60)) + " minutes."
    """
    #doc_hashtable = openTheDocHashTable("./final_inverted_index_files/doc_hashtable.txt")

    #for i in doc_hashtable.keys():
    #  print i

    
    print "===============SEARCH==============="
    print MAXDOCID
    query = raw_input("what do you want to look for? ")
    how_many = int(raw_input("how many documents do you want to see? "))
    k = 30
    start_time = time.clock()
    search(query, k, how_many)
    end_time = time.clock()
    print "run-time : " + str((end_time - start_time)) + " seconds."    
    # k is the number of data to be stored in the heap structure, how_many is the number of data you want to see
    
    
    
    

