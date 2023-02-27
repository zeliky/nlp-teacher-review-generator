import re
import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from enums.request_enums import StudentFeatures, StudentGrade, ReviewRequest


class GradesImporter:
    ID = 'ת.ז'
    NAME = 'שם התלמיד'
    GENDER = 'מין'
    ACHIEVEMENT = 'ראוי לציון'
    IMPROVEMENT = 'ראוי לשיפור'
    MALE = 'ז'
    FEMALE = 'נ'
    CODE_PATTERN = r'\[קוד: \d+ *\]'
    COURSE_ID_PATTERN = r'^([^\d]+)\d'

    def __init__(self):
        self.class_info = {}
        self.course_map = {}
        self.means = {}
        self.stds = {}

    def import_mashov_file(self, file_path, header_line=2):
        df = pd.read_excel(file_path, header=header_line, na_values=None)
        self.calculate_means_and_stds(df)
        # Iterate over the rows of the DataFrame and create a dictionary from each row
        for index, row in df.iterrows():

            if pd.isna(row[self.ID]):
                continue
            id = int(row[self.ID])
            if id in self.class_info:
                sf = self.class_info[id]
            else:
                sf = StudentFeatures()
                sf.id = id
                sf.full_name = row[self.NAME]
                sf.gender = 'male' if row[self.GENDER] == self.MALE else 'female'
                sf.grades = {}


            for col, value in row.items():

                if col == self.IMPROVEMENT and not pd.isna(row[self.IMPROVEMENT]):
                    sf.to_improve(row[col])
                if col == self.ACHIEVEMENT and not pd.isna(row[self.ACHIEVEMENT]):
                    sf.to_praise(row[col])


                header = col.split("\n")
                if len(header) == 3:
                    course_name = header[0].strip()
                    match = re.search(self.COURSE_ID_PATTERN, course_name)
                    if match:
                        course_name = match.group(1).strip()

                    course_id = re.sub('[\[\]]', '', header[2]).strip()
                    self.course_map[course_id] = course_name
                    if pd.notna(value):
                        if course_id not in sf.grades:
                            sf.grades[course_id] = StudentGrade(course_id)
                        if type(value) == str:
                            value = re.sub(self.CODE_PATTERN, '', value).strip()
                            sf.grades[course_id].review = value
                            if sf.grades[course_id].grade_classification is not None and sf.grades[course_id].grade_classification <0:
                                sf.to_improve("{}: {}".format(self.course_map[course_id], value))

                        else:
                            grade_classification = (value - self.means[course_id]) / self.stds[course_id] if self.stds[
                                                                                                                 course_id] > 0 else 0
                            sf.grades[course_id].grade_classification = round((grade_classification * 2) / 2)
                            sf.grades[course_id].grade = value
                            if grade_classification < 0 and (  sf.bad_course is None or sf.grades[course_id] < sf.bad_course):
                                sf.bad_course = sf.grades[course_id]

                            if grade_classification > 0 and ( sf.good_course is None or sf.grades[course_id] > sf.good_course):
                                sf.good_course = sf.grades[course_id]


            if sf.good_course is not None and sf.good_course.review is not None:
                sf.to_praise("{}: {}".format(self.course_map[sf.good_course.course_id],sf.good_course.review))
            if sf.bad_course is not None and sf.bad_course.review is not None:
                sf.to_improve("{}: {}".format(self.course_map[sf.bad_course.course_id], sf.bad_course.review))


            self.class_info[id] = sf



    def calculate_means_and_stds(self, df):
        for col in df.columns:
            header = col.split("\n")
            if len(header) == 3:
                course_id = re.sub('[\[\]]', '', header[2]).strip()
                numeric_values = df[col].loc[df[col].apply(lambda x: pd.notna(x) and type(x) != str)]
                if len(numeric_values.values) > 0:
                    self.means[course_id] = np.mean(numeric_values.values)
                    self.stds[course_id] = np.std(numeric_values.values)

    def student_summary(self, id):
        res = ReviewRequest()
        if id in self.class_info:
            sf = self.class_info[id]
            name_parts = sf.full_name.split(" ")
            res.first_name = name_parts[-1]
            res.gender = sf.gender
            res.high_subject = self.course_map[sf.good_course.course_id] if sf.good_course is not None else ''
            res.low_subject = self.course_map[sf.bad_course.course_id] if sf.bad_course is not None else ''

            if sf.improve is not None:
                res.behavior_problem = " ".join(sf.improve)
            if sf.praise is not None:
                res.great_achievement = ",".join(sf.praise)

        return res





