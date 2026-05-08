import click
import json
import os
from jinja2 import Environment, FileSystemLoader

class ReportGenerator:
    def __init__(self, templates_dir):
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def generate(self, results_path, output_html):
        if not os.path.exists(results_path):
            click.echo(f"Error: Results file {results_path} not found.")
            return False

        with open(results_path, 'r') as f:
            data = json.load(f)

        click.echo("Loaded results successfully. Rendering template...")
        
        try:
            template = self.env.get_template('report_template.html')
            
            # Additional context like generation time could be added here
            html_content = template.render(
                dump_file=data.get('dump_file', 'N/A'),
                os_profile=data.get('os_profile', 'N/A'),
                plugins_run=data.get('plugins_run', []),
                findings=data.get('findings', {})
            )
            
            with open(output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            click.echo(f"Error generating report: {e}")
            return False

@click.command()
@click.option('--results', '-r', default='data/results.json', help='Path to analysis results JSON.')
@click.option('--output', '-o', default='data/report.html', help='Path to output HTML report.')
@click.option('--templates', '-t', default='templates', help='Path to Jinja2 templates directory.')
def main(results, output, templates):
    """Generates an HTML report from analysis results."""
    click.echo("--- Digital Forensics: Report Generation ---")
    generator = ReportGenerator(templates)
    
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    if generator.generate(results, output):
        click.echo(f"Report generated successfully: {output}")

if __name__ == '__main__':
    main()
