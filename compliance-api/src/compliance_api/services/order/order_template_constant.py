"""Order template constants."""

WHERE_AS = """<p class="com-order-title" style="text-align: center;font-weight: bold">
<strong class="editor-text-bold"
            style="white-space: pre-wrap;">
IN THE MATTER OF THE ENVIRONMENTAL ASSESSMENT ACT S.B.C. {{order_details.act}}, c.{{order_details.chapter}}
<br />
(ACT)<br />
AND<br />
# NON-COMPLIANCES<br />
WITH {% if order_details.has_certificate %}ENVIRONMENTAL ASSESSMENT CERTIFICATE
 {{order_details.ea_certificate}}{%else%}(reference Act or Exemption Order, as appropriate){% endif %}<br />
<u>ORDER UNDER SECTION {{order_details.section}}</u>
    </strong></p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr" style="text-align: left;"><b><strong class="editor-text-bold"
            style="white-space: pre-wrap;">WHEREAS:</strong></b></p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr" style="text-align: left;"><span style="white-space: pre-wrap;">
{% if project_details.has_certificate %}
A. The {{project_details.name}} (Project) is a reviewable project under the </span><i>
<em class="editor-text-italic" style="white-space: pre-wrap;">Environmental Assessment Act</em></i>
<span style="white-space: pre-wrap;"> (the Act).</span></p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr" style="text-align: left;"><span style="white-space: pre-wrap;">
B. Environmental Assessment (EA) Certificate {{project_details.eac_certificate}} held by
 {{project_details.proponent}} ({{project_details.proponent_label}}) for the Project has
 requirements in {{requirement_details.requirement_numbers}} of {{requirement_details.requirement_sources}}
  with respect to {{requirement_details.requirement_summaries}}.</span>
</p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
{% endif %}
<p class="editor-paragraph" dir="ltr" style="text-align: left;"><span style="white-space: pre-wrap;">
{% if project_details.has_certificate %}
C. {% else %}A. {% endif %}On
{% if inspection_details.start_date == inspection_details.end_date %}
 {{inspection_details.start_date}}
{% else %}
 {{inspection_details.start_date}} and {{inspection_details.end_date}}
{% endif %}, the Environmental Assessment
 Office Compliance and Enforcement Branch (EAO CEB) conducted a {{inspection_details.inspection_type | lower }}
 inspection of the Project. The inspection found that the {{project_details.proponent_label}} was not compliant
 with {{requirement_details.requirement_numbers}} with respect to {{requirement_details.requirement_summaries}}.
 The inspection findings are documented in Inspection Record {{inspection_details.ir_number}}.</span></p>
<p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr" style="text-align: left;"><span style="white-space: pre-wrap;">
{% if project_details.has_certificate %}D. {% else %}B. {% endif %}Section
 {{order_details.section}} of the Act specifies that the Chief Executive Assessment Officer may order the
  {{project_details.proponent_label}} to</span></p><p class="editor-paragraph" style="text-align: left;"><br></p>
<p class="editor-paragraph" dir="ltr" style="text-align: left;"><i><em class="editor-text-italic"
style="white-space: pre-wrap;">stop doing something that is or is likely to be in contravention of the Act,
 the certificate or the order, or cause it to be stopped</em></i><br><i><em class="editor-text-italic"
style="white-space: pre-wrap;">OR</em></i><br><i><em class="editor-text-italic"
style="white-space: pre-wrap;">take any measure that the Chief Executive Assessment Officer considers
 necessary in order to comply with the Act, the certificate or exemption order to mitigate the effects of
 non-compliance.</em></i><br><i><em class="editor-text-italic"
style="white-space: pre-wrap;">OR</em></i><br><i><em class="editor-text-italic"
style="white-space: pre-wrap;">cease, either altogether or to the extent specified by the Chief Executive
 Assessment Officer.</em></i></p>"""
NOW_THEREFORE = """
<p class="editor-paragraph" dir="ltr" style="text-align: left;"><span style="white-space: pre-wrap;">
Pursuant to Section {{order_details.section}} of the Act, I order that the {{project_details.proponent_label}}
 must by [YYYY-DD-MM]</span></p>
<ol class="editor-list-ol">
    <li value="1" class="editor-listitem"><span style="white-space: pre-wrap;">XX</span></li>
    <li value="2" class="editor-listitem"><span style="white-space: pre-wrap;">XX</span></li>
    <li value="3" class="editor-listitem"><span style="white-space: pre-wrap;">XX</span></li>
    <li value="4" class="editor-listitem"><span style="white-space: pre-wrap;">Complete the measures in clauses 1, 2
 and 3 above to the satisfaction of, and unless otherwise authorized by, the EAO Compliance and Enforcement Branch.
 </span></li>
</ol>"""
