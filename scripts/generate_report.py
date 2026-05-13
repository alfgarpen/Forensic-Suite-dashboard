import click
import json
import os
from jinja2 import Environment, FileSystemLoader

class ReportGenerator:
    def __init__(self, templates_dir):
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def generate(self, results_path, output_html, evidence_info=None):
        if not os.path.exists(results_path):
            click.echo(f"Error: Results file {results_path} not found.")
            return False

        with open(results_path, 'r') as f:
            data = json.load(f)

        click.echo("Loaded results successfully. Rendering template...")
        
        try:
            template = self.env.get_template('report_template.html')
            
            # Prepare context
            context = {
                "dump_file": data.get('dump_file', data.get('source_dump', 'N/A')),
                "os_profile": data.get('os_profile', 'N/A'),
                "plugins_run": data.get('plugins_run', []),
                "findings": data.get('findings', {}),
                "generation_time": data.get('analysis_time', 'N/A')
            }

            # Add evidence metadata if provided
            if evidence_info:
                context.update({
                    "dump_hashes": {"sha256": evidence_info.get('hash')},
                    "dump_size": evidence_info.get('size_bytes'),
                    "acquisition_source": evidence_info.get('source'),
                    "acquisition_time": evidence_info.get('timestamp')
                })

            html_content = template.render(**context)
            
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            click.echo(f"Error generating report: {e}")
            return False

import datetime

@click.command()
@click.option('--results', '-r', default='artifacts/results.json', help='Path to analysis results JSON.')
@click.option('--output', '-o', help='Path to output HTML report. Defaults to reports/reporte_TIMESTAMP.html')
@click.option('--templates', '-t', default='frontend/templates', help='Path to Jinja2 templates directory.')
def main(results, output, templates):
    """Generates an HTML report from analysis results."""
    click.echo("--- Digital Forensics: Report Generation ---")
    
    if not output:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f'reports/reporte_{timestamp}.html'
    
    data_dir = 'artifacts'
    state_file = os.path.join(data_dir, 'current_dump.json')
    evidence_info = None
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            evidence_info = json.load(f)
            click.echo(f"Loaded evidence metadata for: {evidence_info.get('filename')}")

    generator = ReportGenerator(templates)
    
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    if generator.generate(results, output, evidence_info):
        click.echo(f"Report generated successfully: {output}")

if __name__ == '__main__':
    main()
