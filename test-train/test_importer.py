from lib.grades_importer import GradesImporter


gr = GradesImporter()
gr.import_mashov_file('data/grades_with_reviews4.xlsx')
#print(gr.student_summary(329210223))
for id in gr.class_info:
    print(gr.student_summary(id))
