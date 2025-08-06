from django.shortcuts import render
from .github_fetcher import analyze_repo
from django.http import JsonResponse
import pandas as pd
from .score import Score
from django.http import HttpResponse
from django.utils.html import format_html
from django.shortcuts import redirect


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

    return redirect("home")

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
def compute_maturity_levels(rows):
    from collections import defaultdict

    focus_area_to_capabilities = defaultdict(list)


    for row in rows:
        focus_area = row["Focus Area"]
        practice_levels = [row[str(col)] for col in range(1, 11)]
        focus_area_to_capabilities[focus_area].append(practice_levels)

    maturity_levels = {}

    for area, capability_rows in focus_area_to_capabilities.items():
        max_level = 0
        for level in range(10):  # columns 1 to 10
            all_pass = all(
                row[level] == "✔" for row in capability_rows if len(row) > level + 2
            )
            if all_pass:
                max_level += 1
            else:
                break
        maturity_levels[area] = max_level

    return maturity_levels


def generate_table(request):
    if request.method == "POST":
        score_definition = request.session.get("score_definition")
        analysis_result = request.session.get("score_data")

        if not score_definition or not analysis_result:
            return HttpResponse("Missing score data. Analyze a repository first.")

        table_data = generate_true_false_matrix(score_definition, analysis_result)
        df = pd.DataFrame(table_data)

        # Remove index column (don't include it in HTML)
        df.reset_index(drop=True, inplace=True)

        # Begin HTML table
        html = '<table class="table table-bordered table-sm" style="border-collapse: collapse; width: 100%;">'

        # Table header
        html += "<thead><tr>"
        for col in df.columns:
            html += f"<th style='border: 1px solid #ccc; text-align:center; padding:8px;'>{col}</th>"
        html += "</tr></thead><tbody>"

        # Prepare for merging "Focus Area" column values
        previous_focus_area = None
        focus_area_counts = df["Focus Area"].value_counts()

        for idx, row in df.iterrows():
            html += "<tr>"

            focus_area = row["Focus Area"]
            if focus_area != previous_focus_area:
                rowspan = focus_area_counts[focus_area]
                html += (
                    f"<td rowspan='{rowspan}' style='border: 1px solid #ccc; vertical-align: middle; padding:8px; background-color: #f9f9f9;'>"
                    f"{focus_area}</td>"
                )
                previous_focus_area = focus_area
            # Else: skip this cell to allow rowspan

            # Capability
            html += f"<td style='border: 1px solid #ccc; padding:8px;'>{row['Capability']}</td>"

            # Remaining columns (scores)
            for col in df.columns[2:]:
                cell_value = row[col]
                bg = "#e6ffe6" if cell_value == "✔" else "#ffe6e6" if cell_value == "✖" else "#fff"
                html += f"<td style='border: 1px solid #ccc; text-align:center; padding:8px; background-color: {bg};'>{cell_value}</td>"

            html += "</tr>"
        
        html += "</tbody></table>"
        maturity_levels = compute_maturity_levels(table_data)
        return render(request, "table_result.html", {"html_table": format_html(html), "maturity_levels": maturity_levels})

    return redirect("check_score")



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


