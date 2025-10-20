import time
from langchain.prompts import PromptTemplate
from typing import List
from utils import S3Client
from schemas.ai_analysis import ResearchPaperSummary, MCQSet
from services.llm_service import LLMService
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    
    def __init__(self):
        self.s3_client = S3Client()
        self.llm_service = LLMService()
        self.settings = get_settings()
        self.llm = self.llm_service.get_llm()
    
    def _fetch_paper_markdown(self, paper_id: str) -> str:
        markdown_s3_key = f"{self.settings.s3_parsed_markdown_prefix}/{paper_id}/paper.md"
        
        if not self.s3_client.file_exists(markdown_s3_key):
            raise Exception(f"Markdown file not found for paper_id: {paper_id}")
        
        markdown_content = self.s3_client.download_file(markdown_s3_key).decode('utf-8')
        logger.info(f"Fetched markdown for paper {paper_id}")
        return markdown_content
    
    def generate_summary(self, paper_id: str) -> dict:
        start_time = time.time()
        
        try:
           
            paper_content = self._fetch_paper_markdown(paper_id)
            
            summary_prompt = """You are an expert academic summarizer and research analyst.

Analyze the following research paper in depth, using the text below:

{paper_markdown}

Your task:
Provide a **comprehensive, detailed, and well-structured analysis** of the paper in **strict JSON format**.
Each field in the JSON must contain **Markdown-formatted content**, written in full academic prose — not bullet-point fragments or one-line summaries.

---

### Output Schema

"summary": "An extended executive summary (6–10 sentences) giving the big picture, context, and contributions.",
"background": "Explain the theoretical or technical background — what prior work or assumptions this research builds on.",
"problem": "Describe the precise research problem, including the motivation and why it matters.",
"methods": "Detailed explanation of the methods, models, or experimental design. Include equations ($$...$$) or tables if relevant.",
"experiments": "Explain experimental setup: datasets, baselines, metrics, ablations. Include Markdown tables if appropriate.",
"results": "Comprehensive description of key quantitative and qualitative findings — not just one line. Discuss patterns, significance, and implications.",
"limitations": "Critical analysis of what the paper does not cover, assumptions, or methodological weaknesses.",
"implications": "Explain how the findings contribute to the broader field — theory, applications, or policy relevance.",
"future_work": "Describe suggested or potential future research directions in depth, not just a single sentence."

---

### Formatting Rules

- Use **Markdown syntax** inside the JSON values.
- Use LaTeX math when relevant (`$...$` or `$$...$$`).
- Include Markdown tables for data, metrics, or comparisons if applicable.
- Be **comprehensive**: each section should be several paragraphs long where needed.
- Avoid repeating generic phrases like "The paper discusses..." — write **substantively**.
- Never shorten the content — err on the side of depth and completeness.

---

Return only valid JSON."""
            
            structured_llm = self.llm.with_structured_output(ResearchPaperSummary)
            
            prompt = PromptTemplate(
                template=summary_prompt,
                input_variables=["paper_markdown"]
            )
            summary_chain = prompt | structured_llm
            
            logger.info(f"Generating summary for paper {paper_id}")
            summary = summary_chain.invoke({"paper_markdown": paper_content})
            
            processing_time = time.time() - start_time
            logger.info(f"Generated summary for paper {paper_id} in {processing_time:.2f}s")
            
            return {
                "paper_id": paper_id,
                "summary": summary.model_dump(),
                "processing_time_seconds": round(processing_time, 2),
                "message": "Summary generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating summary for paper {paper_id}: {e}")
            raise
    
    def generate_quiz(self, paper_id: str, num_questions: int = 10) -> dict:
        """Generate quiz questions for a research paper"""
        start_time = time.time()
        
        try:
            paper_content = self._fetch_paper_markdown(paper_id)
            
            quiz_prompt = """You are an expert educator creating assessment questions for research papers.

Based on the following research paper:

{paper_markdown}

Generate {num_questions} high-quality multiple-choice questions that test deep understanding of the paper.

Each question should:
- Test conceptual understanding, not just memorization
- Have 4 plausible options 
- Have exactly one correct answer 
- Include an explanation of why the correct answer is right

Cover diverse aspects: methodology, results, implications, limitations, and key concepts.


"""
            
           
            structured_llm = self.llm.with_structured_output(MCQSet)
            
            prompt = PromptTemplate(
                template=quiz_prompt,
                input_variables=["paper_markdown", "num_questions"]
            )
            quiz_chain = prompt | structured_llm
            
            logger.info(f"Generating {num_questions} quiz questions for paper {paper_id}")
            quiz_result = quiz_chain.invoke({
                "paper_markdown": paper_content,
                "num_questions": num_questions
            })
            processing_time = time.time() - start_time
            
            return {
                "paper_id": paper_id,
                "questions": quiz_result.questions,  # Changed from 'questions' to 'quiz_result.questions'
                "processing_time_seconds": round(processing_time, 2),
                "message": "Quiz generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating quiz for paper {paper_id}: {e}")
            raise
    
    def generate_mindmap(self, paper_id: str) -> dict:
        """Generate interactive mindmap for a research paper"""
        start_time = time.time()
        
        try:
            paper_content = self._fetch_paper_markdown(paper_id)
            
            mindmap_prompt = """You are an expert at creating structured knowledge representations.

Based on the following research paper:

{paper_markdown}

Create a comprehensive mindmap in Markmap markdown format.

The mindmap should:
- Start with the paper title as the root node
- Include major sections: Background, Problem, Methods, Results, Contributions, Limitations
- Use hierarchical structure with proper indentation
- Include key concepts, equations (using LaTeX), and findings
- Be comprehensive but well-organized

Return ONLY the markdown content for the mindmap, starting with # (the paper title)."""
            
            prompt = PromptTemplate(
                template=mindmap_prompt,
                input_variables=["paper_markdown"]
            )
            mindmap_chain = prompt | self.llm
            
            logger.info(f"Generating mindmap for paper {paper_id}")
            mindmap_markdown = mindmap_chain.invoke({"paper_markdown": paper_content})
            
            print("\n\n\n",mindmap_markdown,"\n\n\n")
            
            html_content = self._create_markmap_html(mindmap_markdown.content)
            
            processing_time = time.time() - start_time
            logger.info(f"Generated mindmap for paper {paper_id} in {processing_time:.2f}s")
            
            return {
                "paper_id": paper_id,
                "html_content": html_content,
                "processing_time_seconds": round(processing_time, 2),
                "message": "Mindmap generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating mindmap for paper {paper_id}: {e}")
            raise
    
    def _create_markmap_html(self, markdown_content: str) -> str:
        """Create HTML page with embedded markmap visualization"""
        import html  # for escaping <, >, &, etc.

        safe_markdown = html.escape(markdown_content)

        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="x-poe-datastore-behavior" content="local_only">
            <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://code.jquery.com https://unpkg.com https://d3js.org https://threejs.org https://cdn.plot.ly https://stackpath.bootstrapcdn.com https://maps.googleapis.com https://cdn.tailwindcss.com https://ajax.googleapis.com https://kit.fontawesome.com https://cdn.datatables.net https://maxcdn.bootstrapcdn.com https://code.highcharts.com https://tako-static-assets-production.s3.amazonaws.com https://www.youtube.com https://fonts.googleapis.com https://fonts.gstatic.com https://pfst.cf2.poecdn.net https://puc.poecdn.net https://i.imgur.com https://wikimedia.org https://*.icons8.com https://*.giphy.com https://picsum.photos https://images.unsplash.com; frame-src 'self' https://www.youtube.com https://trytako.com; child-src 'self'; manifest-src 'self'; worker-src 'self'; upgrade-insecure-requests; block-all-mixed-content;">
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mindmap for PDF</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #ffffff;
                    min-height: 100vh;
                    padding: 20px;
                }}

                h1 {{
                    text-align: center;
                    color: #333;
                    font-size: 2rem;
                    margin-bottom: 20px;
                    font-weight: 600;
                }}

                .markmap {{
                    width: 100%;
                    height: 85vh;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background: #fafafa;
                }}

                @media (max-width: 768px) {{
                    h1 {{
                        font-size: 1.5rem;
                    }}

                    .markmap {{
                        height: 80vh;
                    }}
                }}
            </style>
            <script src="https://puc.poecdn.net/authenticated_preview_page/syncedState.bd4eeeb8e8e02052ee92.js"></script>
        </head>
        <body>
            <h1>MindMap</h1>
            <div class="markmap">
                <pre id="mm-content" style="display:none;">{safe_markdown}</pre>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.18.12/dist/index.js"></script>
            <script>
                // Read escaped markdown and render with Markmap
                const md = document.getElementById("mm-content").textContent;
                markmap.autoLoader.render(document.querySelector(".markmap"), md);
            </script>
        </body>
        </html>
        """
        
        return html_template
