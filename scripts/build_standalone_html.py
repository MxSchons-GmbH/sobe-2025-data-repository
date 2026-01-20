#!/usr/bin/env python3
"""
Build standalone HTML files for iframe embedding.
Inlines all CSS (including base variables) and JS into the HTML files.
"""

from pathlib import Path
from paths import OUTPUT_ROOT, OUTPUT_CSS, OUTPUT_JS

# Base CSS variables needed for all pages
BASE_CSS_VARIABLES = """
/* ============================================================================
   CSS VARIABLES - Base theme for standalone pages
   ============================================================================ */
:root {
    /* Colors */
    --bg: #FAF9F6;
    --bg-card: #FFFFFF;
    --bg-darker: #F5F3EF;
    --text: #2D2D2D;
    --text-heading: #1A1A1A;
    --text-muted: #6B6B6B;
    --text-light: #8B8B8B;
    --border: #D4D4D4;
    --border-light: #E8E6E1;

    /* Accent colors */
    --accent-purple: #6B5B95;
    --accent-purple-dark: #574B7A;
    --accent-translucent: rgba(107, 91, 149, 0.1);
    --accent-gold: #D4A84B;
    --accent-teal: #4A90A4;
    --data-teal: #4A90A4;

    /* Spacing */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --space-2xl: 48px;
    --space-3xl: 64px;

    /* Typography */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-serif: 'Playfair Display', Georgia, serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

    /* Layout */
    --container-width: 1200px;

    /* Transitions */
    --transition-fast: 0.15s ease;
    --transition-normal: 0.25s ease;
}

/* Base reset and typography */
*, *::before, *::after {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: var(--font-sans);
    font-size: 16px;
    line-height: 1.6;
    color: var(--text);
    background: var(--bg);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
    margin: 0;
    font-weight: 600;
    line-height: 1.3;
    color: var(--text-heading);
}

p {
    margin: 0 0 1em;
}

a {
    color: var(--accent-purple);
    text-decoration: none;
    transition: color var(--transition-fast);
}

a:hover {
    color: var(--accent-purple-dark);
    text-decoration: underline;
}

img {
    max-width: 100%;
    height: auto;
}

button {
    font-family: inherit;
}
"""

def read_file(path):
    """Read a file and return its contents."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def build_standalone_html(html_path, css_path, js_path, output_path):
    """Build a standalone HTML file with inlined CSS and JS."""
    html = read_file(html_path)
    css = read_file(css_path)
    js = read_file(js_path)

    # Combine base CSS with page-specific CSS
    full_css = BASE_CSS_VARIABLES + "\n\n" + css

    # Create inline style tag
    style_tag = f"<style>\n{full_css}\n</style>"

    # Create inline script tag
    script_tag = f"<script>\n{js}\n</script>"

    # Replace external CSS link with inline style
    # Find and replace the CSS link
    import re
    html = re.sub(
        r'<link rel="stylesheet" href="css/[^"]+\.css">',
        style_tag,
        html
    )

    # Replace external JS with inline script
    html = re.sub(
        r'<script src="js/[^"]+\.js"></script>',
        script_tag,
        html
    )

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Built: {output_path}")

def main():
    # Build figures.html
    build_standalone_html(
        html_path=OUTPUT_ROOT / 'figures.html',
        css_path=OUTPUT_CSS / 'figures.css',
        js_path=OUTPUT_JS / 'figures.js',
        output_path=OUTPUT_ROOT / 'figures.html'
    )

    # Build data.html
    build_standalone_html(
        html_path=OUTPUT_ROOT / 'data.html',
        css_path=OUTPUT_CSS / 'data.css',
        js_path=OUTPUT_JS / 'data.js',
        output_path=OUTPUT_ROOT / 'data.html'
    )

    print("\nStandalone HTML files built successfully!")

if __name__ == '__main__':
    main()
