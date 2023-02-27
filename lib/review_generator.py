import openai
import requests
import json
import six
import random
from google.cloud import translate_v2 as translate
import re
from enums.request_enums import StudentFeatures

openai.api_key = '<YOUR_API_KEY>'


class ReviewGenerator:
    def __init__(self, req, target_language='he'):
        self.request = req
        self.translate_client = translate.Client()
        self.target_language = target_language

    def prompt_for_improvment(self, type, mbti, problem):
        if type=='subject_imp':
            prompt =  "give 3 options to improve performance in {} for {} student".format(problem,mbti)
        elif type=='behaviour_imp':
            prompt = "give 3 options to eliminate or reduce {} for {} student".format(problem, mbti)
        else:
            prompt = " give 3 ideas for {} personality type to eliminate {}".format(mbti, problem)
        return prompt

    def suggest_ideas(self,  type, mbti, text):
        print(text)
        result = self.translate_client.translate(text, target_language='en')
        problem = result['translatedText']
        prompt = self.prompt_for_improvment(type, mbti, problem)


        model_engine = "text-davinci-003"
        completions = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        text = completions.choices[0].text


        repl = re.sub('\d\.', '', text)
        lines = repl.split('\n')
        res = []
        for l in lines:
            if len(l.strip())>0:
                res.append(l.strip())
        return res


    def extract_features(self, text):
        prompt = """
        Extract the features from the given text.
        example:
        text: שאול היקר, אתה ילד חרוץ ושקדן.
         נוכחותך בכיתה משרה שלווה. עליך לשפר ציונך במתמטיקה לקראת הבגרות. ניכר שאתה מרבה לאחר קח את זה לתשומת לבך. בהצלחה בהמשך.
        features:
        name:שאול
        gender: זכר
        characteristics: חרוץ, שקדן
        need_improvement : מתמטיקה
        positive: משרה שלווה
        negative: מרבה לאחר
        ###
        
        text: {text}"
        features:  
        """.format(text=text)



        print(text)
        #model_prompt = (f"{prompt}", ["name:", "characteristics:", "achievement","school subjects:", "problematic behavior:"])
        model_engine = "text-davinci-003"
        completions = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        features_text = completions.choices[0].text
        print(features_text)
        pattern = re.compile(r'(.*):(.*)')
        result = {}
        for (key, value) in re.findall(pattern, features_text):
            result[key.replace(" ", "_")] = value.strip()
        return result


    def generate(self, options=2):
        self.translate_request()

        prompt = self.prepare_prompt()
        results = []
        reviews = self.ai_generate_phrase(prompt,options)
        for review in reviews:
            translated = self.translate_response(review)
            results.append({
                    'original':review,
                    'text': translated
                })
        return results


    def generate_school_certificate_review(self, features):

        prompt = self.prepare_prompt_from_school_certificate(features)
        print(prompt)
        results = None

        reviews = self.ai_generate_phrase(prompt,1)
        for review in reviews:
            print(review)
            translated = self.translate_response(review)
            print(translated)
            return {
                'original':review,
                'text': translated
            }

        return {
                'original':'bla',
                'text': 'בלה'
            }


    def ai_generate_phrase(self, prompt,options):
        completions = openai.Completion.create(
            engine="text-davinci-003",
            #engine="text-curie-001",
            prompt=prompt,
            max_tokens=1500,
            n=options,
            stop=None,
            temperature=0.7,
            frequency_penalty=0.38,
            presence_penalty=0
        )
        print(completions.choices)
        choices = [c.text for c in completions.choices]
        return choices

    def translate_response(self, review):
        result = self.translate_client.translate(review, target_language=self.target_language)
        tr = result['translatedText']
        #if self.request.mbti is not None:
        #    tr = tr.replace(self.request.mbti, '')
        return tr

    def translate_request(self):
        text = "{};{};{};{}".format(self.request.good_characteristic if  not empty(self.request.good_characteristic) else '---',
                                    self.request.great_achievement if not empty(self.request.great_achievement) else '---',
                                    self.request.behavior_problem if  not empty(self.request.behavior_problem)  else '---',
                                    self.request.low_subject if  not empty(self.request.low_subject)  else '---')

        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")
        print(text)
        result = self.translate_client.translate(text, target_language='en')
        tr = result['translatedText']

        spl = tr.split(';')

        self.request.good_characteristic = str(spl[0]) if len(spl)<5 and spl[0] != '---' else None,
        self.request.great_achievement = str(spl[1])  if len(spl)<5 and spl[1]  != '---' else None,
        self.request.behavior_problem = str(spl[2])  if len(spl)<5 and spl[2]  != '---' else None,
        self.request.low_subject = str(spl[3])  if len(spl)<5 and spl[3] != '---' else None,

    def prepare_prompt_from_school_certificate(self, features):
        features_str = ''
        del features['full_name']
        for key, value in features.items():
            if key == 'full_name' or key=='id':
                continue
            features_str += "{}: {}\n".format(key, value)

        return  """      
Consider yourself an outstanding educator. write to the following student, a personal feedback for his school certificate, 
based on the following features
{features}
write the phrase in English using the following structure:
assess  his personality type and learning traits,provide feedback about his positive features, suggest how to improve his negative features, 
end with inspiring phrase matching his personality
""".format(features =features_str)

    def prepare_prompt(self):
        print(self.request)
        first_name = self.request.first_name
        mbti = self.request.mbti
        behavior_problem, low_subject, good_characteristic, great_achievement = '', '', '', ''
        if len(self.request.good_characteristic) > 0:
            good_characteristic = 'and specially {} '.format(self.request.good_characteristic)

        if len(self.request.great_achievement) > 0:
            mbti_char = self.mbti_characteristics(mbti,2)
            great_achievement = 'Add your impression regarding his {} activity.'.format(
                self.request.great_achievement)

        if len(self.request.behavior_problem) > 0:
            behavior_problem = 'Express your concern about him being {}, and brainstorm an idea how to change it.'.format(
                self.request.behavior_problem)

        if len(self.request.low_subject) > 0:
            mbti_char = self.mbti_characteristics(mbti, 2)
            low_subject = 'suggest a matching {} strategy to improve his skills in {}.'.format(
                #self.mbti_strategies(mbti), self.request.low_subject)
                mbti, self.request.low_subject)

        fields = {
            'E': 'Extrovert',
            'I': 'Introvert',
            'S': 'Sensing',
            'N': 'Intuition',
            'T': 'Thinking',
            'F': 'Feeling',
            'P': 'Perceiving',
            'J': 'Judging',
        }
        emphasize_mbti = []
        if self.request.grades is not None:
            for field, grade in self.request.grades.items():
                print("%s,%s" % (field, grade))
                if grade == 2:
                    emphasize_mbti.append(fields[field])
        emph_mbti = ' and '.join(emphasize_mbti[:2])
        mbti_characteristics = self.mbti_characteristics(mbti,2)
        prompt_template = """write a diploma review for {mbti} student with the following structure:
1. start with "Dear {first_name},". 
2. short compliment about the way he behaves at class. 
3. add an example how his {mbti_char} {gcph} qualities affected him at school.  
4. {grach} 
5. {lsbj} 
6. {bhvpr} 
7. add inspiring phrase matching his qualities.
                """.format(first_name=first_name,mbti_char= mbti_characteristics, mbti=mbti, gcph=good_characteristic, grach=great_achievement,
                           bhvpr=behavior_problem,emph_mbti= emph_mbti,
                           lsbj=low_subject)
        print(prompt_template)
        return prompt_template

    def mbti_characteristics (self, mbti, limit):
        characteristics =  {
        'ISTJ': ['practical', 'reliable', 'responsible', 'analytical', 'structured', 'cautious', 'diligent', 'logical', 'detail - oriented', 'traditional'],
        'ISFJ': ['nurturing', 'loyal', 'dependable', 'patient', 'organized', 'empathetic', 'sensitive', 'meticulous', 'modest', 'supportive'],
        'INFJ': ['insightful', 'empathetic', 'idealistic', 'creative', 'compassionate', 'intuitive', 'deep', 'private', 'determined', 'moral'],
        'INTJ': ['strategic', 'analytical', 'logical', 'independent', 'visionary', 'innovative', 'knowledgeable', 'confident', 'reserved', 'decisive'],
        'ISTP': ['resourceful', 'practical', 'independent', 'adventurous', 'logical', 'tactical', 'spontaneous', 'flexible', 'observant', 'confident'],
        'ISFP': ['sensitive', 'artistic', 'adaptable', 'gentle', 'loyal', 'empathetic', 'caring', 'modest', 'creative', 'kind'],
        'INFP': ['Idealistic', 'introspective', 'passionate', 'empathetic', 'imaginative', 'insightful', 'curious', 'poetic', 'sensitive', 'dedicated'],
        'INTP': ['Analytical', 'logical', 'inventive', 'curious', 'independent', 'theoretical', 'precise', 'critical', 'original', 'reserved'],
        'ESTP': ['Energetic', 'daring', 'spontaneous', 'adaptable', 'hands - on', 'confident', 'tactical', 'competitive', 'lively', 'practical'],
        'ESFP': ['cheerful', 'warm', 'spontaneous', 'energetic', 'friendly', 'adaptable', 'lively', 'sociable', 'talkative', 'charming'],
        'ENFP': ['Enthusiastic', 'creative', 'curious', 'passionate', 'empathetic', 'expressive', 'spontaneous', 'optimistic', 'imaginative', 'individualistic'],
        'ENTP': ['Clever', 'curious', 'analytical', 'independent', 'innovative', 'resourceful', 'strategic', 'conceptual', 'argumentative', 'confident'],
        'ESTJ': ['Efficient', 'practical', 'logical', 'responsible', 'decisive', 'organized', 'reliable', 'traditional', 'self - confident', 'structured'],
        'ESFJ': ['Nurturing', 'social', 'loyal', 'responsible', 'warm', 'helpful', 'conscientious', 'supportive', 'practical', 'traditional'],
        'ENFJ': ['Charismatic', 'empathetic', 'visionary', 'inspiring', 'social', 'dedicated', 'passionate', 'idealistic', 'insightful', 'supportive'],
        'ENTJ': ['Strategic', 'decisive', 'independent', 'visionary', 'logical', 'confident', 'assertive', 'analytical', 'efficient', 'ambitious'],
            
        }
        chr = characteristics[mbti]  if mbti in characteristics else []
        random.shuffle(chr)
        return ", ".join(chr[:limit])


    def mbti_questions(self, mbti, subject):
        questions= {
            'ESTJ' : 'by stopping {} which problem will be solved in his life ',
            'ISTJ' : 'by knowing {} how he may use it in his life',
            'ENTJ' : 'by knowing {} which general problem will be solved ',
            'INTJ' : 'what are the root causes of {} ',
            'ESTP' : 'by knowing {} how efficient he will be by knowing {} ',
            'ISTP' : 'by knowing {} How does this work? ',
            'ENTP' : 'by knowing {} What are the ways to solve this problem?',
            'INTP' : 'by knowing {} What is the structure of problem?',
            'ESFJ' : 'by knowing {} Will this help me in work with others?',
            'ISFJ ' : 'by knowing {} How it will help me in work? ',
            'ENFJ' : 'by knowing {} How is this good for people?',
            'INFJ ' : 'by knowing {}Will it be useful for people? ',
            'ESFP' : 'by knowing {}Will I enjoy this?',
            'ISFP ' : 'by knowing {}I need it if it’s beautiful',
            'ENFP ' : 'by knowing {}Will people enjoy this?',
            'INFP' : 'by knowing {}Is it a right thing to do?',
        }
        return questions[mbti].format(subject) if mbti in questions else ""


    def mbti_strategies(self, mbti, limit=1):
        mbti_strategies = {
            'ISTJ': [
                'Develop a structured study schedule and stick to it',
                'Take detailed notes during class and review them regularly',
                'Use visual aids such as flashcards, diagrams, and graphs to help with memorization',
                'Create a study group with classmates to review and discuss course material',
                'Utilize past exams and textbooks to practice problem-solving skills'
            ],
            'ISFJ': [
                'Establish a comfortable and quiet study environment',
                'Take comprehensive notes during class and review them regularly',
                'Use past exams and textbooks to practice problem-solving skills',
                'Study with a study group or a study partner to reinforce understanding',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'INFJ': [
                'Create a study schedule that accommodates both work and rest',
                'Connect course material to personal values and goals',
                'Use visual aids such as mind maps, diagrams, and flowcharts to organize information',
                'Join a study group or work with a study partner to review course material',
                'Identify and overcome any emotional blocks or distractions that may interfere with studying'
            ],
            'INTJ': [
                'Develop a study schedule that accommodates both work and rest',
                'Analyze and understand course material on a deep level',
                'Formulate and test theories based on course material',
                'Study with a study group or a study partner to engage in intellectual discussions',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'ISTP': [
                'Establish a comfortable and quiet study environment',
                'Use hands-on learning techniques such as projects, simulations, and experiments',
                'Use visual aids such as graphs, charts, and diagrams to help with memorization',
                'Join a study group or work with a study partner to review course material',
                'Utilize past exams and textbooks to practice problem-solving skills'
            ],
            'ISFP': [
                'Establish a comfortable and quiet study environment',
                'Use hands-on learning techniques such as projects, simulations, and experiments',
                'Use visual aids such as graphs, charts, and diagrams to help with memorization',
                'Join a study group or work with a study partner to review course material',
                'Utilize past exams and textbooks to practice problem-solving skills'
            ],
            'INFP': [
                'Create a study schedule that accommodates both work and rest',
                'Connect course material to personal values and goals',
                'Use visual aids such as mind maps, diagrams, and flowcharts to organize information',
                'Join a study group or work with a study partner to review course material',
                'Identify and overcome any emotional blocks or distractions that may interfere with studying'
            ],
            'INTP': [
                'Develop a study schedule that accommodates both work and rest',
                'Analyze and understand course material on a deep level',
                'Formulate and test theories based on course material',
                'Study with a study group or a study partner to engage in intellectual discussions',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'ESTJ': [
                'Develop a structured study schedule and stick to it',
                'Take detailed notes during class and review them regularly',
                'Use visual aids such as flashcards, diagrams, and graphs to help with memorization',
                'Create a study group with classmates to review and discuss course material',
                'Utilize past exams and textbooks to practice problem-solving skills'
            ],
            'ESFJ': [
                'Establish a comfortable and quiet study environment',
                'Take comprehensive notes during class and review them regularly',
                'Use past exams and textbooks to practice problem-solving skills',
                'Study with a study group or a study partner to reinforce understanding',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'ENFJ': [
                'Create a study schedule that accommodates both work and rest',
                'Connect course material to personal values and goals',
                'Use visual aids such as mind maps, diagrams, and flowcharts to organize information',
                'Join a study group or work with a study partner to review course material',
                'Identify and overcome any emotional blocks or distractions that may interfere with studying'
            ],
            'ENTJ': [
                'Develop a study schedule that accommodates both work and rest',
                'Analyze and understand course material on a deep level',
                'Formulate and test theories based on course material',
                'Study with a study group or a study partner to engage in intellectual discussions',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'ESTP': [
                'Establish a comfortable and quiet study environment',
                'Use hands-on learning techniques such as projects, simulations, and experiments',
                'Use visual aids such as graphs, charts, and diagrams to help with memorization',
                'Join a study group or work with a study partner to review course material',
                'Utilize past exams and textbooks to practice problem-solving skills'
            ],
            'ESFP': [
                'Establish a comfortable and quiet study environment',
                'Use hands-on learning techniques such as projects, simulations, and experiments',
                'Use visual aids such as graphs, charts, and diagrams to help with memorization',
                'Join a study group or work with a study partner to review course material',
                'Utilize past exams and textbooks to practice problem-solving skills'
            ],
            'ENFP': [
                'Create a study schedule that accommodates both work and rest',
                'Connect course material to personal values and goals',
                'Use visual aids such as mind maps, diagrams, and flowcharts to organize information',
                'Join a study group or work with a study partner to review course material',
                'Identify and overcome any emotional blocks or distractions that may interfere with studying'
            ],
            'ENTP': [
                'Develop a study schedule that accommodates both work and rest',
                'Analyze and understand course material on a deep level',
                'Formulate and test theories based on course material',
                'Study with a study group or a study partner to engage in intellectual discussions',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'INFJ': [
                'Establish a comfortable and quiet study environment',
                'Take comprehensive notes during class and review them regularly',
                'Use past exams and textbooks to practice problem-solving skills',
                'Study with a study group or a study partner to reinforce understanding',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'INTJ': [
                'Develop a study schedule that accommodates both work and rest',
                'Analyze and understand course material on a deep level',
                'Formulate and test theories based on course material',
                'Study with a study group or a study partner to engage in intellectual discussions',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ],
            'INFP': [
                'Create a study schedule that accommodates both work and rest',
                'Connect course material to personal values and goals',
                'Use visual aids such as mind maps, diagrams, and flowcharts to organize information',
                'Join a study group or work with a study partner to review course material',
                'Identify and overcome any emotional blocks or distractions that may interfere with studying'
            ],
            'INTP': [
                'Develop a study schedule that accommodates both work and rest',
                'Analyze and understand course material on a deep level',
                'Formulate and test theories based on course material',
                'Study with a study group or a study partner to engage in intellectual discussions',
                'Use study techniques such as summarizing, mnemonics, or visualization to retain information'
            ]
        }
        strg = mbti_strategies[mbti] if mbti in mbti_strategies else []
        random.shuffle(strg)
        return ", ".join(strg[:limit])

def empty(txt):
    return txt is None or len(txt.strip()) == 0