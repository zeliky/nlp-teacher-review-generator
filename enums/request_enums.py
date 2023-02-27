from pydantic import BaseModel
from typing import Union,Optional


class StudentGrade(BaseModel):
    course_id: Optional[int]
    grade: Optional[float]
    grade_classification: Optional[float]
    review: Optional[str]

    def __init__(self, course_id):
        super(StudentGrade, self).__init__()
        self.course_id = course_id

    # overload < operator
    def __lt__(self, other):
        if  self.grade_classification is None or  other.grade_classification is None:
            return False
        if self.grade_classification == other.grade_classification:
            return self.grade < other.grade
        return self.grade_classification < other.grade_classification


    # overload > operator
    def __gt__(self, other):
        if  self.grade_classification is None or  other.grade_classification is None:
            return False
        if self.grade_classification == other.grade_classification:
            return self.grade > other.grade
        return self.grade_classification > other.grade_classification



class StudentFeatures(BaseModel):
    id: Optional[str]
    full_name: Optional[str]
    gender: Optional[str]
    grades: Optional[dict[str,StudentGrade ]]
    characteristic:  Optional[list[str]]
    good_course: Optional[StudentGrade]
    bad_course: Optional[StudentGrade]
    improve:Optional[set[str]]
    praise: Optional[set[str]]

    def to_improve(self,value):
        if self.improve is None:
            self.improve = set()
        value = value.strip()
        if len(value) > 0:
            self.improve.add(value)

    def to_praise(self,value):

        if self.praise is None:
            self.praise = set()
        value = value.strip()
        if len(value)>0:
            self.praise.add(value)


    def list_features(self,id,courses_map, as_text=True):
        name_parts = self.full_name.split(" ")
        first_name = name_parts[-1]
        features = {
            'id': id,
            'name': first_name,
            'full_name': self.full_name,
            'gender': self.gender,
        }
        if  self.improve is not None:
            features['to_improve'] = " ".join(self.improve)
        if  self.praise is not None:
            features['good_feedback'] = " ".join(self.praise)
        if  self.characteristic is not None:
            features['characteristic'] = " ".join(self.characteristic)
        if self.good_course is not None:
            if self.good_course.grade_classification==1:
                features['above_average_subject'] =  courses_map[self.good_course.course_id]
            if self.good_course.grade_classification>1:
                features['excellent_subject'] =  courses_map[self.good_course.course_id]
        if self.bad_course is not None:
            if self.bad_course.grade_classification==-1:
                features['bellow_average_subject'] =  courses_map[self.bad_course.course_id]
            if self.bad_course.grade_classification<-1:
                features['very_low_subject'] =  courses_map[self.bad_course.course_id]


        if not as_text:
            return features

        features_str = ''
        del features['full_name']
        for key, value in features.items():
            if key == 'full_name' or key=='id':
                continue
            features_str += "{}: {}\n".format(key, value)

        return features_str



class ReviewRequest(BaseModel):
    first_name: Optional[str]
    gender: Optional[str]
    mbti: Optional[str]
    grades: Optional[dict]
    good_characteristic: Optional[str]
    great_achievement: Optional[str]
    behavior_problem: Optional[str]
    low_subject: Optional[str]
    high_subject: Optional[str]


class SuggestionRequest(BaseModel):
    type: str
    mbti: str
    problem: str
