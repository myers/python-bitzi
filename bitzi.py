#!/usr/bin/env python

__version__ = "0.2"

import os 

from ctypes import * # http://sourceforge.net/projects/ctypes

if os.name == "nt":
    dll = cdll.LoadLibrary("bitcoll.dll")
else:
    dll = cdll.LoadLibrary("libbitcollider.so.1")

class Error(Exception):
    pass

CALLBACKFUNC = CFUNCTYPE(c_void_p, c_int, c_char_p, c_char_p)

class Attribute(Structure):
    _fields_ = [
        ("key", c_char_p),
        ("value", c_char_p),]
Attribute_p = POINTER(Attribute)
Attribute_p_p = POINTER(Attribute_p)

class Submission(Structure):
    _fields_ = [
        ("bc", c_void_p),
        ("attrList", Attribute_p_p),
        ("numBitprints", c_int),
        ("numItems", c_int),
        ]
Submission_p = POINTER(Submission)    

class Bitcollider:
    def __init__(self):
        self._dll = dll
        self._bc = dll.bitcollider_init(False)
    
    def __del__(self):
        self._dll.bitcollider_shutdown(self._bc)
        
    def analyze(self, filepath, callback=None):
        if callback:
            callback = CALLBACKFUNC(callback)
            self._dll.set_progress_callback(self._bc, callback)
        
        self._dll.create_submission.restype = Submission_p
        submission = self._dll.create_submission(self._bc)
        errstatus = self._dll.analyze_file(submission, filepath, False)
        if not errstatus:
            self._dll.delete_submission(submission)
            msg = self._dll.get_error(self._bc)
            
            raise Error(msg)
        
        ret = {}
        for ii in xrange(submission.contents.numItems):
            attr = submission.contents.attrList[ii].contents
            ret[attr.key] = attr.value
        if callback:
            self._dll.set_progress_callback(self._bc, None)
        return ret        

def analyze2triples(analyzeResults):
    """
    Returns a list of triples in the form of
      (URI, fileURI,), attribURI, (Literal, value,)
    or
      (URI, fileURI,), attribURI, (BNode, bnodeURI,)
    or 
      (BNode, bnodeURI,), attribURI, (Literal, value,)
     
    Where URI = 0, Literal = 1, BNode = 3
    
    This is for use for things that implement the tristero interface:
        http://tristero.sourceforge.net/search-xml-rpc.html
    """
    ret = []
    URI = 0
    Literal = 1
    BNode = 3
    
    subject = (URI, "file:///" + os.path.abspath(analyzeResults["tag.filename.filename"]),)
    
    dc = "http://purl.org/dc/elements/1.1/"    
    bz = "http://bitzi.com/xmlns/2002/01/bz-core#"
    mm = "http://musicbrainz.org/mm/mm-2.0#"
    lookupTable = {
        "tag.file.length": bz + "fileLength",
        "tag.file.first20": bz + "fileFirst20Bytes",
        "tag.kzhash.kzhash": bz + "fileKZHash",
        "tag.ed2k.ed2khash": bz + "fileED2kHash",
        "tag.video.duration": mm + "duration",
        "tag.audio.duration": mm + "duration",
        "tag.video.width": bz + "videoWidth",
        "tag.video.height": bz + "videoHeight",
        "tag.video.fps": bz + "videoFPS",
    }
    for key in analyzeResults.keys():
        if lookupTable.has_key(key):
            ret.append( (subject, lookupTable[key], (Literal, analyzeResults[key],),) )
        if key == "tag.filename.filename":
            ret.append( (subject, bz + "fileName", (BNode, "_:id0",),) )
            ret.append( ((BNode, "_:id0",), dc + "title", (Literal, analyzeResults[key],),) ) 
    return ret
