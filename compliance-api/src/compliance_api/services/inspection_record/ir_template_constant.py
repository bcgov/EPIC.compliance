"""IR template related constants."""

INSPECTION_SCOPE = """<p class="editor-paragraph" dir="ltr">
    <span>The Officer inspected {{ area_inspected }}.</span>
</p>
<p class="editor-paragraph">&nbsp;</p>
<p class="editor-paragraph" dir="ltr">
    <span>The inspection included a debrief of observations with Project staff on {{ debrief_date }}.</span>
</p>
<p class="editor-paragraph">
    <br>
</p>
<p class="editor-paragraph" dir="ltr">
    <span>The following requirements were inspected against:</span>
</p>
<ol class="editor-list-ol">
    {% for req in requirements %}
    <li class="editor-listitem" style="margin-bottom: 4px;">
        <span>{{ req }}.</span>
    </li>
    {% endfor %}
</ol>
<p class="editor-paragraph">
    <br>
</p>
"""

FINDING_STATEMENT = """<p class="editor-paragraph" dir="ltr">
    <span>Additional detail regarding these findings may be found in the sections below.</span>
</p>
<p class="editor-paragraph">
    <br>
</p>
<p class="editor-paragraph" dir="ltr">
    <span>
        The compliance findings in this report reflect the analysis based on the information obtained
        during the inspection commenced on the date noted above. These findings can change at any time
        upon information gathered through future inspections or if new information is obtained by the
        EAO Compliance and Enforcement Branch (CEB).
    </span>
</p>
"""

PRELIMINARY_REVIEW_DETAILS = """<div>
    <p class="editor-paragraph" dir="ltr">
        <span>
            On {{ date_report_sent}}, Officer {{ primary_last_name }} provided the preliminary
            inspection record to the {{ proponent_label }}.
        AND</span><br><span>On {{ date_response }}, the {{ proponent_label }}
            provided comments pertaining to the preliminary inspection record. These comments were reviewed, and edits
            were made to the record by the EAO Compliance and Enforcement Branch (CEB) to correct identified errors of
            fact or omission prior to finalizing. </span>
    </p>
    <p class="editor-paragraph" dir="ltr"><span>OR</span></p>
    <p class="editor-paragraph" dir="ltr"><span>On {{ date_response }}, the {{ proponent_label }} provided comments
            pertaining to the preliminary inspection record. These comments were reviewed by the EAO Compliance and
            Enforcement Branch (CEB). No errors of fact or omission were identified.</span></p>
    <p class="editor-paragraph" dir="ltr"><span>OR</span></p>
    <p class="editor-paragraph" dir="ltr"><span>No comments were received from the {{ proponent_label }} prior to
            finalizing the record.</span></p>
    <p class="editor-paragraph">
        <br>
    </p>
</div>
"""

ACTION_REQUIRED_BY_RP = """<p class="editor-paragraph" dir="ltr"><b><strong class="editor-text-bold">Please review
 this inspection record for errors or omissions and provide a response to Officer {{ primary_officer }}
 by</strong></b>
{% if date_expected_return %}
    {{ date_expected_return }}
{% else %}
    <span style="color: gray;">date will appear once due date is set.</span>
{% endif %}
</p>"""

ENFORCEMENT_SUMMARY = {
    "NOTICE_OF_NON_COMPLIANCE": """<p class="editor-paragraph" dir="ltr">{{ regulated_party }} is
    not compliant with {{ number }} of {{ req_source_name }} of {{ eac }}. {{ regulated_party }} has
    been issued a Notice of Non-Compliance. See Requirement {{ req_sort_order }} for
    further information.</p>""",
    "WARNING_LETTER": """<p class="editor-paragraph" dir="ltr">{{ regulated_party }} is not
    compliant with {{ ','.join(condition_lines)}} of {{ eac }}. Warning Letter
    {{ warning_letter_no }} has been issued for the non-compliance. See {{ sort_order_line }} for
    further information.</p>""",
    "ORDER": """<p class="editor-paragraph" dir="ltr">In Addition, {{ regulated_party }} is not
    compliant with {{ ','.join(condition_lines)}} of {{ eac }}. Order
    {{ order_no }} has been issued under {{ section_no }} of the <i>{{ act }}</i> ({{ act_year }}).
    See {{ sort_order_line }} for further information.</p>""",
    "ADMINISTRATIVE_PENALTY": """<p class="editor-paragraph" dir="ltr">In Addition, the findings
    for {{ sort_order_line }} may be referred to a decision maker for consideration of
    an Administrative Penalty.</p>""",
    "AGENCY": """<p class="editor-paragraph" dir="ltr">{{ number }} of {{ req_source_name }} of
    {{ eac }} was refered to {{ agency_name }}. See Requirement {{ req_sort_order }} for further
    information.</p>""",
    "DEFAULT": """<p class="editor-paragraph" dir="ltr">The EAO CEB may inspect to determine if
    {{ project_name }} has been brought into compliance with these requirements. Continued non-compliance
    with these requirements may result in additional enforcement under the <i>{{ act }}</i> ({{ act_year }}).</p>""",
}

AREA_INSPECTED = "[Brief description of Project Components  / Area inspected]"
