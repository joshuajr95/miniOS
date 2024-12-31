#! /usr/bin/python3


import argparse
from typing import List

from tokenizer import Tokenizer, Token, TokenType
from parser import RecursiveDescentParser, ParseError







def getFileContents(file) -> str:
    fileString: str = None

    fileHandle = open(file, "r")
    fileString = fileHandle.read()
    fileHandle.close()

    return fileString



'''
This is the core functionality of the compiler.
'''
def runCompilerCore(inputFile, outputFile=None):
    
    fileString: str = getFileContents(inputFile)



    #####################
    # Run the Tokenizer #
    #####################

    tokenList: List[Token] = []
    tokenizer: Tokenizer = Tokenizer(fileString)
    parser: RecursiveDescentParser = RecursiveDescentParser(tokenizer, inputFile, lookAhead=1)


    parser.parseDeviceTree()

    parseTree = parser.getParseTree()
    parseTree.output()


    '''
    nextToken: Token = tokenizer.getNextToken()

    while nextToken.type != TokenType.TOKEN_TYPE_END_OF_FILE:
        tokenList.append(nextToken)
        nextToken: Token = tokenizer.getNextToken()

    tokenList.append(nextToken)
    '''





def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    runCompilerCore(args.file)



if __name__ == "__main__":
    main()




