"""
from transformers import pipeline
reviewer = pipeline('text-generation',
                    model='./gpt2-heb-review',
                    tokenizer='Norod78/hebrew-gpt_neo-small'
                    )

start = 'כדי לשפר את יכולתיך בהיסטוריה אני ממליצה להשתמש להתשמש בסגנון החשיבה מחוץ לקופסא שלך כדי '
start = ' יחד עם זאת הרבית להיעדר והדבר פגע בהישגיך בחלק מהמקצועות. '
res = reviewer(start, min_length=5, max_length=70)
print(res)
"""


from transformers import FeatureExtractionPipeline, AutoTokenizer

# load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("mofawzy/gpt2-base-finetuned-features-extraction", use_auth_token=True,, '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')

# load the feature extraction pipeline
feature_extractor = FeatureExtractionPipeline(model="mofawzy/gpt2-base-finetuned-features-extraction", tokenizer=tokenizer)






# define the text to be analyzed
text = "שאול היקר, אתה ילד חרוץ ושקדן. נוכחותך בכיתה משרה שלווה. עליך לשפר ציונך במתמטיקה לקראת הבגרות. ניכר שאתה מרבה לאחר קח את זה לתשומת לבך. בהצלחה בהמשך."

# use the pipeline to extract features
result = feature_extractor(text)

# print the extracted features
print("Features:")
for item in result:
    print(f"name:{item['word']}\tcategory:{item['entity']}")