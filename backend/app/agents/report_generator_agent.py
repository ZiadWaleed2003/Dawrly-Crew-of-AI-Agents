import json
import html

def json_to_html_table(json_file_path="./backend/results/step_4_evaluator_fixed_results.json", output_html_path="./backend/results/final_result.html"):
    """
    Convert JSON job data to a clean sheet-like HTML table
    
    Args:
        json_file_path (str): Path to the JSON file
        output_html_path (str): Path where HTML file will be saved
    """
    
    # Read JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Sort jobs by recommendation rank (descending - higher ranks first)
    jobs = data.get('jobs', [])
    jobs_sorted = sorted(jobs, key=lambda x: x.get('agent_recommendation_rank', 0), reverse=True)
    
    # Start building HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Job Report</title>
  <style>
    table {{ border-collapse: collapse; }}
    table, th, td {{ border: 1px solid #e5e7eb; }}
    ul {{ margin: 0; padding-left: 1.5rem; }}
  </style>
</head>
<body style='background-color: #f9fafb; font-family: Arial, sans-serif; margin: 0; padding: 0;'>
  <div style='max-width: 1200px; margin: 0 auto; padding: 1rem;'>
    <div style='background-color: #ffffff; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 3rem;'>
      <h1 style='font-size: 1.5rem; font-weight: 600; color: #374151; margin-bottom: 1rem;'>Job Report</h1>
      <p style='color: #4b5563; font-size: 0.875rem; margin-bottom: 1rem;'>Sorted by recommendation rank descending</p>
    </div>
    
    <div style='background-color: #ffffff; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);'>
      <h2 style='font-size: 1.5rem; font-weight: 600; color: #374151; margin-bottom: 1rem;'>Recommended Jobs</h2>
      <div style='overflow-x: auto;'>
        <table style='width: 100%; background-color: #ffffff; border-collapse: collapse; border-radius: 0.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);'>
          <thead>
            <tr style='background-color: #f3f4f6;'>
              <th style='padding: 0.75rem 1rem; text-align: left; font-size: 0.875rem; font-weight: 600; color: #4b5563;'>Job Title</th>
              <th style='padding: 0.75rem 1rem; text-align: left; font-size: 0.875rem; font-weight: 600; color: #4b5563;'>Job Description</th>
              <th style='padding: 0.75rem 1rem; text-align: left; font-size: 0.875rem; font-weight: 600; color: #4b5563;'>Recommendation Rank</th>
              <th style='padding: 0.75rem 1rem; text-align: left; font-size: 0.875rem; font-weight: 600; color: #4b5563;'>Agent Notes</th>
              <th style='padding: 0.75rem 1rem; text-align: left; font-size: 0.875rem; font-weight: 600; color: #4b5563;'>Apply</th>
            </tr>
          </thead>
          <tbody>"""
    
    # Add job rows
    for job in jobs_sorted:
        title = html.escape(job.get('job_title', 'N/A'))
        description = html.escape(job.get('job_description', 'N/A'))
        url = job.get('job_url', '#')
        rank = job.get('agent_recommendation_rank', 'N/A')
        notes = job.get('agent_recommendation_notes', [])
        
        # Format notes as a bulleted list
        notes_html = ""
        if notes:
            notes_html = "<ul style='margin: 0; padding-left: 1.5rem;'>"
            for note in notes:
                notes_html += f"<li>{html.escape(note)}</li>"
            notes_html += "</ul>"
        else:
            notes_html = "No recommendations available"
        
        html_content += f"""
            <tr style='border-bottom: 1px solid #e5e7eb;'>
              <td style='padding: 0.75rem 1rem; font-size: 0.875rem; color: #374151;'>{title}</td>
              <td style='padding: 0.75rem 1rem; font-size: 0.875rem; color: #374151;'>{description}</td>
              <td style='padding: 0.75rem 1rem; font-size: 0.875rem; color: #374151;'>{rank}</td>
              <td style='padding: 0.75rem 1rem; font-size: 0.875rem; color: #374151;'>{notes_html}</td>
              <td style='padding: 0.75rem 1rem; font-size: 0.875rem; color: #374151;'><a href='{html.escape(url)}' style='color: #3b82f6; text-decoration: underline;' target='_blank'>Apply Link</a></td>
            </tr>"""
    
    # Close HTML
    html_content += """
          </tbody>
        </table>
      </div>
    </div>
  </div>
</body>
</html>"""

    try:
    
        # Write HTML file
        with open(output_html_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        
        print(f"HTML table successfully created: {output_html_path}")
        print(f"Total jobs processed: {len(jobs_sorted)}")
    
        return True
    
    except IOError as e:

        print(f"couldn't write the HTML file {e}")

        return False
