from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import Question, Essay
from .forms import AnswerForm

from .utils.model import *
from .utils.helpers import *


from collections import Counter
from spellchecker import SpellChecker
import re
from textblob import TextBlob, Word
import enchant
from string import punctuation
import language_tool_python

import os
current_path = os.path.abspath(os.path.dirname(__file__))

# Create your views here.
def index(request):
    questions_list = Question.objects.order_by('setn')
    context = {
        'questions_list': questions_list,
    }
    return render(request, 'grader/index.html', context)

def essay(request, question_id, essay_id):
    essay = get_object_or_404(Essay, pk=essay_id)
    context = {
        "essay": essay,
    }
    return render(request, 'grader/essay.html', context)

def question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AnswerForm(request.POST)
        if form.is_valid():

            content = form.cleaned_data.get('answer')

            content = content.strip()
            pdata = content.strip()
            paragraphs = content.split("\n\n")
            paragraphCount = len(paragraphs)
            
            words = content.split(" ")
            mySpecialList = [ '-', '+', '#', '@', '!', '(', ')', '?', '.', ',', ':', ';', '"', "'", '`', '“', " ",' ','']
            wordCount = 0
            for c in words:
                if c not in mySpecialList:
            #         print(c)
                    wordCount += 1
                    
            spellData = content.strip()
            
            correct = 0
            mispelled = 0
            
            noPunc = spellData
            myPunctuation = punctuation.replace("'","")
            
            noPunc = noPunc.translate(str.maketrans("", "", myPunctuation))
            
            stopChar = ['”', '“']
            for word in noPunc:
                if word in stopChar:
                    noPunc = noPunc.replace(word,"")
            noPuncSplit = noPunc.split()
            
            d = enchant.Dict("en_US")
            
            for word in noPuncSplit:
                if d.check(word) == False:
                    print(word)
                    mispelled += 1
                else:
                    correct += 1
            print("mispelled", mispelled)
            
            keyList = "Social media, Facebook, Whatsapp, Youtube, Technology, Distance, Across, World, Places, friends, relatives, abroad Education, Masters, Birthdays, Landline, Letters, Travel, Telephones, Wishes, Updates, groups, Functions, games, Together, Parties, Talk , Physical communication, Occasions, festivals, Cousins, parents, Siblings, Parks, Play, Physical activity"
            keyListLower = keyList.lower()
            keywords = keyListLower.split(", ")
            
            myPunctuation = punctuation.replace("'", "") 
            
            noPunc = noPunc.translate(str.maketrans("", "", myPunctuation))
            nkey = len(keywords)
            print(nkey)
            lowercaseData = noPunc.lower()
            lowercaseDataSplit = lowercaseData.split(" ")
            
            
            for i in range(0, len(lowercaseDataSplit)):
                lowercaseDataSplit[i] = "".join(lowercaseDataSplit[i])
                duplicate = Counter(lowercaseDataSplit)
                new = " ".join(duplicate.keys())
                
                
            keywordCount = 0
            print("\nThese are the matching words in the student's essay:")
            for keyword in keywords:
                if keyword in new.split(" "):
                    print(keyword)
                    keywordCount += 1
                    
            print("\n")
            print("Matching keywords in student's essay = ",keywordCount, "/", nkey)


            taggedSentence = nltk.tag.pos_tag(noPuncSplit)
            print(taggedSentence)
            
            tool = language_tool_python.LanguageTool('en-US')
            
                        
            matches = tool.check(content)
            grammarMistakeCount = len(matches)

            print(grammarMistakeCount)
            
            wordPoints = 40
            if wordCount < 100:
                wordPoints -= (1)*wordPoints
            elif wordCount>100 and wordCount < 150:
                wordPoints -= (1/2)*wordPoints
            elif wordCount >= 150 and wordCount < 191:
                wordPoints -= (1/4)*wordPoints
            elif wordCount >= 191 and wordCount < 200:
                wordPoints -= (1/8)*wordPoints
            else:
                wordPoints -= 0 * wordPoints

            print("Points for words = ", wordPoints)
                    

            spellPoints = 15
            if mispelled >=10:
                spellPoints -= 1*spellPoints
            elif mispelled >=7 and mispelled <=9:
                spellPoints -= (2/3)*spellPoints
            elif mispelled >=4 and mispelled <=6:
                spellPoints -= (1/3)*spellPoints
            else:
                spellPoints -= 0*spellPoints
            print("Points for Spelling Mistakes = ", spellPoints)

            grammarPoints = 20
            if grammarMistakeCount >= 10:
                grammarPoints -= (100/100)*grammarPoints
            elif grammarMistakeCount >= 7 and grammarMistakeCount <=9:
                grammarPoints -= 0.75*grammarPoints
            elif grammarMistakeCount >=4 and grammarMistakeCount <=6:
                grammarPoints -= 0.50*grammarPoints
            elif grammarMistakeCount >=2 and grammarMistakeCount <=3:
                grammarPoints -= 0.25*grammarPoints
            else:
                grammarPoints -= 0*grammarPoints
            print("Points for Grammar Mistakes = ", grammarPoints)


            keywordPoints = 20
            if keywordCount >= (50/100)*nkey:
                keywordPoints -= 0*keywordPoints
            elif keywordCount >= (40/100)*nkey and keywordCount < (50/100)*nkey:
                keywordPoints -= (5/100)*keywordPoints
            elif keywordCount >= (30/100)*nkey and keywordCount < (40/100)*nkey:
                keywordPoints -= (10/100)*keywordPoints
            elif keywordCount >= (20/100)*nkey and keywordCount < (30/100)*nkey:
                keywordPoints -= (15/100)*keywordPoints
            else:
                keywordPoints -= (100/100)*keywordPoints
            print("Points for keyword match = ", keywordPoints)

            
                
            paraPoints = 5
            if paragraphCount == 1:
                paraPoints -= (4/5)*paraPoints
            elif paragraphCount == 2:
                paraPoints -= (2/5)*paraPoints
            elif paragraphCount >= 3 and paragraphCount <= 5:
                paraPoints -= (0)*paraPoints
            print("Points for paragraphs = ", paraPoints)


            preds = wordPoints + keywordPoints + paraPoints + grammarPoints + spellPoints
            print(preds)

            
            
            K.clear_session()
            essay = Essay.objects.create(
                content=content,
                question=question,
                score=preds
            )
        return redirect('essay', question_id=question.setn, essay_id=essay.id)
    else:
        form = AnswerForm()

    context = {
        "question": question,
        "form": form,
    }
    return render(request, 'grader/question.html', context)