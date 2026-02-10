import os
import re

import markdown
from bs4 import BeautifulSoup


class MarkdownHelper:
    def get_markdown_files(self, root_dir: str) -> list:
        markdown_files = []
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".md"):
                    markdown_files.append(os.path.join(root, file))
        return markdown_files

    def markdown_to_plaintext(self, md_text: str) -> str:
        # Convert Markdown -> HTML
        html = markdown.markdown(md_text)
        # Parse HTML and extract clean text
        soup = BeautifulSoup(html, "html.parser").get_text(separator="\n")
        text = re.sub(r"\s+", " ", soup)
        return text
