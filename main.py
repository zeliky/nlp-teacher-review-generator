

from fastapi import FastAPI,File, UploadFile
from lib.grades_importer import GradesImporter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from lib.review_generator import ReviewGenerator
from fastapi.staticfiles import StaticFiles
from enums.request_enums import  ReviewRequest,StudentFeatures, SuggestionRequest
import tempfile



from starlette.responses import FileResponse

app = FastAPI()
app.mount("/js", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
async def index():  
    return FileResponse('frontend/class_file.html')

@app.get("/extended_review")
async def index():
    return FileResponse('frontend/index.html')    
    
    
@app.post("/generate_grades_review/")
async def generate_grades_review(features: dict):
    review =  await prepare_grades_review(features)
    return {
        'review': review
    }


@app.post("/generate_review/")
async def generate_review(req: ReviewRequest):
    reviews =  await prepare_review(req)
    return {
        'reviews': reviews
    }

@app.post("/suggest/")
async def suggest(req: SuggestionRequest):
    ideas =  await suggest_idea(req)
    return {
        'ideas': ideas
    }


@app.get("/mbti_characteristics/")
async def mbti_characteristics(mbti: str):
    rg = ReviewGenerator(None)
    chrs = rg.mbti_characteristics(mbti, 10)

    return {
        'characteristics': chrs.split(', ')
    }


@app.post("/upload/")
async def upload_grades_list(file: UploadFile = File(...)):

    # Load the file into a pandas dataframe
    data = await import_mashov_file(file)
    # Return the dataframe as a JSON response
    return data


async def prepare_grades_review(features):
    rg = ReviewGenerator(None)
    return rg.generate_school_certificate_review(features)


async def prepare_review(req):

    rg = ReviewGenerator(req)
    return rg.generate()


async def suggest_idea(req:SuggestionRequest):
    #return "", ""
    rg = ReviewGenerator(req)
    return rg.suggest_ideas(req.type, req.mbti, req.problem)

async def import_mashov_file(file):
    fp = tempfile.NamedTemporaryFile(prefix="mshv_", delete=False)
    fp.write(file.file.read())
    fp.close()



    print(fp.name)
    tmp_file = fp.name

    gr = GradesImporter()
    gr.import_mashov_file(tmp_file)
    data = {}
    print(gr.class_info)
    for id, sf in gr.class_info.items():
        data[str(id)] = sf.list_features(id,gr.course_map,as_text=False)

    return data



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(str(exc))
    return PlainTextResponse(str(exc), status_code=400)
