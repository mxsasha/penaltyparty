# Loading from Goose's CSV, enhanced with correct answer in K
import sys

import django
import openpyxl

django.setup()

from penaltyparty.pp.models import Answer, Question  # noqa: E402

# Load the workbook and the first sheet
workbook = openpyxl.load_workbook(sys.argv[1])
sheet = workbook.active


def is_bold(cell):
    return cell.font.bold


for row in sheet.iter_rows(min_row=2, values_only=False):  # Assuming the first row is headers
    values = [cell.value for cell in row[:5]]
    rule, section, scenario, last_used, question_text = values
    if not question_text:
        break

    # Create the Question object
    question = Question.objects.create(
        question_text=question_text,
        rule_section=section,
        rule_scenario=scenario,
    )

    # Create the Answer objects
    for cell in row[5:]:
        if cell.value is not None:
            answer_text = cell.value
            is_correct = is_bold(cell)
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=is_correct,
            )
