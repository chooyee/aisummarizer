InstructionList = {}

# summary="****Instructions: Summarize content given, ensuring the summary is concise with date and NER are preserved. Grounded in the original material."
# InstructionList["summary"] = summary

disect="***Instruction: For the given text, extract only the topic, summary, and relationships between the topic and named entities"
InstructionList["disect"] = disect

# promptAnalyzer = """
# Analyze the prompt text given, then Draft response outline that able to be use for searching against vector database. Reply in json format as below only:
# {
#    "promptanalysis":prompt-analysis,
#    "outline": title-description
# }
# """

# promptAnalyzer = """
# Context: the given text is the question to query the vector database. 
# Based on the analysis of given text, propose list of items for response  
# Reply the proposed items according to below format, do not add additional advise, content, comment:
# 1. [title - description]
# 2. [title - description]
# """

# promptAnalyzer = """
# Context: the given text is the question to query the vector database. 
# Task: Based on the analysis of given text, draft outline items for response. Ensure each item is concise and on single line.  
# Reply according to below format, do not add additional advise, content, comment:
# 1. [title - description]
# 2. 
# """

promptAnalyzer = """
Prompt:

    Please dissect the following prompt:

    [prompttext]

Breakdown:

    User Intent:
        What is the primary goal or purpose of the user's request? If the prompt related to NER, ensure the NER is in the outline for searching purpose
        classify the intent into one of the category [action | inquiry | greeting | general inquiry | reasoning]
    ***separator***
    Context:
        What relevant background knowledge or information is necessary to understand the prompt?
        Are there any specific terms, acronyms, or references that need to be clarified?
    ***separator***
    Outline of Response:
        Based on the user intent and context, what are the key points that should be addressed in the response?
        Create one level outline that can be used to organize the content.
    ***separator***
Use short, succinct sentence, do not add additional comment, advice, content out of above structure
Generate a JSON object representing with the following properties:
- user_primary_goal: a string
- user_intent: a string
- context: a string
- outline_of_response: an array of strings
return final json object only, must be only valid json object
"""

InstructionList["promptAnalyzer"] = promptAnalyzer

summarySystemInstruction = "You are task to answer question based on given content, be concise, succint and grounded on given content"
InstructionList["summarySystemInstruction"] = summarySystemInstruction