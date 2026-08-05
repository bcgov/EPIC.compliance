"""Warning Letter Constant."""

WARNING_LETTER_CONTENT = """<p class='editor-paragraph' dir='ltr'>
<strong>SENT VIA EMAIL</strong></p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<div class="address-block">
    <p>
        NAME<br>
        TITLE<br>
        COMPANY<br>
        ADDRESS<br>
        CITY PROVINCE POSTAL CODE
    </p>
</div>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr">Dear [NAME],</p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr"><strong>RE: Warning for Non-Compliance with
 {{requirement_details[0].requirement_source_number}}
 of Environmental Assessment Certificate # {{project_details.eac_certificate}}</strong></p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr">
    On {{ inspection_details.start_date }}, {{inspection_details.officer_position}}
     {{ inspection_details.primary_officer_name }} conducted a {{inspection_details.inspection_type | lower }}
     inspection (Inspection) of the {{ project_details.name }} (Project) against the requirements of
      {{ requirement_sources }}.
      {% if condition_lines %}
      Based on review of information obtained during the Inspection, it was determined
       that the {{project_details.proponent_label}}, {{ project_details.proponent }} (the Holder) is not compliant
        with {{condition_lines[0]}}.
        {% if condition_lines|length > 1 %}
        {% for line in condition_lines[1:] %}
        It was also determined that the {{project_details.proponent_label}},
         {{project_details.proponent}} (the Holder) is not compliant with {{line}}.
        {% endfor %}
        {% endif %}
      {% endif %}
</p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
{% for requirement in requirement_details %}
<p class="editor-paragraph" dir="ltr">
    {{requirement.requirement_source_number}} requires the Holder to {{requirement.requirement_summary}}.
</p>
{% endfor %}
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr">
    The inspection findings are documented in Inspection Record {{ inspection_details.ir_number }}.
</p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr">
    The Holder is hereby <strong>WARNED</strong> that the Project is not compliant with {{', '.join(condition_lines)}}.
    The maximum penalty for failure to comply with an Environmental Assessment Certificate is $1,000,000 and, on each
    subsequent conviction, a fine of not more than $2,000,000.
</p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr">
    Environmental Assessment Compliance &amp; Enforcement will continue to monitor this issue and may
    follow-up with further inspections as required. Future or continuing non-compliance may result in additional
    enforcement action as warranted.
</p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr">
    Please contact me at {{department_details.phone}} or via email at <a href="mailto:{{ department_details.email }}">
    {{ department_details.email }}
    </a> if you have any questions.
</p>
"""
