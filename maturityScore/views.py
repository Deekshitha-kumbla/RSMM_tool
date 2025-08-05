from django.shortcuts import render
from .github_fetcher import analyze_repo
from django.http import JsonResponse
import pandas as pd
from .score import Score
from django.http import HttpResponse
from django.utils.html import format_html

def home(request):
    return render(request, "home.html")
def check_score(request):
    if request.method == "POST":
        repo_url = request.POST.get("repo_url")
        if repo_url:
            try:
                result = analyze_repo(repo_url)  # returns {capability: {practice_name: bool}}
                request.session["score_data"] = result
                request.session["score_definition"] = Score
                return render(request, "result.html", {"score": result})
            except Exception as e:
                return render(request, "result.html", {"score": {"Error": str(e)}})

    return redirect("home.html")

def generate_true_false_matrix(score_definition, analysis_result):
    rows = []
    breakdown = analysis_result.get("breakdown", {})  

    for focus_area, capabilities in score_definition.items():
        focus_data = breakdown.get(focus_area, {}) 

        for capability, col_map in capabilities.items():
            analysis_values = focus_data.get(capability, {})

            
            
            
            # Normalize keys in analysis values
            normalized_analysis = {k.strip().lower(): v for k, v in analysis_values.items()}

            row = {
                "Focus Area": focus_area,
                "Capability": capability
            }

            for col in range(1, 11):
                col_str = str(col)
                practice = col_map.get(col_str)
                if not practice:
                    row[col_str] = ""
                else:
                    normalized_practice = practice.strip().lower()
                    is_passed = normalized_analysis.get(normalized_practice, False)
                    row[str(col)] = "✔" if is_passed else "✖"
            rows.append(row)

    return rows







def generate_table(request):
    if request.method == "POST":
        score_definition = request.session.get("score_definition")
        analysis_result = request.session.get("score_data")

        if not score_definition or not analysis_result:
            return HttpResponse("Missing score data. Analyze a repository first.")

        table_data = generate_true_false_matrix(score_definition, analysis_result)
        df = pd.DataFrame(table_data)

        # Prepare HTML table
        html = '<table class="table table-bordered" style="border-collapse: collapse; width: 100%;">'

        # Table header
        html += "<thead><tr>"
        for col in df.columns:
            html += f"<th style='border: 1px solid black; text-align:center; padding:6px;'>{col}</th>"
        html += "</tr></thead><tbody>"

        previous_focus_area = None
        focus_area_counts = df["Focus Area"].value_counts()

        for idx, row in df.iterrows():
            html += "<tr>"

            focus_area = row["Focus Area"]
            if focus_area != previous_focus_area:
                rowspan = focus_area_counts[focus_area]
                html += (
                    f"<td rowspan='{rowspan}' style='border: 1px solid black; vertical-align: middle; padding:6px;'>"
                    f"{focus_area}</td>"
                )
                previous_focus_area = focus_area
            # Else: skip this cell to allow rowspan

            # Capability column
            html += f"<td style='border: 1px solid black; padding:6px;'>{row['Capability']}</td>"

            # Remaining columns
            for col in df.columns[2:]:
                html += f"<td style='border: 1px solid black; text-align:center; padding:6px;'>{row[col]}</td>"

            html += "</tr>"

        html += "</tbody></table>"

        return render(request, "table_result.html", {"html_table": format_html(html)})

    return redirect("result.html")

def index(request):
    return render(request, 'index.html')

def userinputs(request):
    return render(request, 'userinputs.html')

def calculate_score(request):
    if request.method == 'POST':
        user_answers = {
            'has_tests': request.POST.get('has_tests') == 'yes',
            'has_ci': request.POST.get('has_ci') == 'yes',
            'has_docs': request.POST.get('has_docs') == 'yes',
        }

        score = 0
        breakdown = {}

        if user_answers['has_tests']:
            breakdown['Test Coverage'] = 10
            score += 10
        else:
            breakdown['Test Coverage'] = 0

        if user_answers['has_ci']:
            breakdown['CI/CD Setup'] = 10
            score += 10
        else:
            breakdown['CI/CD Setup'] = 0

        if user_answers['has_docs']:
            breakdown['Developer Docs'] = 10
            score += 10
        else:
            breakdown['Developer Docs'] = 0

        return JsonResponse({'total': score, 'breakdown': breakdown})
    return JsonResponse({'error': 'POST required'}, status=405)


