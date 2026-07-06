"""PDF内容提取模块 - 从PDF书籍中提取文本内容"""
import fitz  # PyMuPDF
from pathlib import Path
from loguru import logger
from typing import List, Dict
import json
import re


class PDFExtractor:
    """PDF文本提取器"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        self.pdf = fitz.open(str(pdf_path))
        logger.info(f"已加载PDF: {pdf_path}, 共{len(self.pdf)}页")

    def extract_all_text(self) -> str:
        """提取全部文本"""
        text_parts = []
        for page_num in range(len(self.pdf)):
            page = self.pdf[page_num]
            text = page.get_text("text")
            if text.strip():
                text_parts.append(f"--- 第{page_num + 1}页 ---\n{text}")
        return "\n\n".join(text_parts)

    def extract_by_pages(self) -> List[Dict]:
        """按页提取文本"""
        pages = []
        for page_num in range(len(self.pdf)):
            page = self.pdf[page_num]
            text = page.get_text("text")
            if text.strip():
                pages.append({
                    "page_num": page_num + 1,
                    "text": text.strip()
                })
        return pages

    def extract_chapters(self) -> List[Dict]:
        """提取章节结构"""
        chapters = []
        current_chapter = None

        for page_num in range(len(self.pdf)):
            page = self.pdf[page_num]
            text = page.get_text("text")
            if not text.strip():
                continue

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if self._is_chapter_title(line):
                    if current_chapter:
                        chapters.append(current_chapter)
                    current_chapter = {
                        "title": line,
                        "start_page": page_num + 1,
                        "content": []
                    }

            if current_chapter:
                current_chapter["content"].append(text)
                current_chapter["end_page"] = page_num + 1

        if current_chapter:
            chapters.append(current_chapter)

        return chapters

    def _is_chapter_title(self, line: str) -> bool:
        """判断是否为章节标题"""
        patterns = [
            r"^第[一二三四五六七八九十\d]+[章篇]",
            r"^\d+\.\d*\s*\S+",
            r"^Chapter\s+\d+",
        ]
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        return False

    def extract_paragraphs(self) -> List[str]:
        """提取段落"""
        paragraphs = []
        for page_num in range(len(self.pdf)):
            page = self.pdf[page_num]
            blocks = page.get_text("blocks")
            for block in blocks:
                if block[4]:  # 文本块
                    text = block[4].strip()
                    if len(text) > 10:
                        paragraphs.append(text)
        return paragraphs

    def extract_to_file(self, output_path: str):
        """提取并保存到文件"""
        text = self.extract_all_text()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        logger.info(f"文本已保存到: {output_path}")
        return output_path

    def get_metadata(self) -> Dict:
        """获取PDF元数据"""
        metadata = self.pdf.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "page_count": len(self.pdf)
        }

    def close(self):
        """关闭PDF"""
        self.pdf.close()


def extract_pdf_content(pdf_path: str, output_dir: str = None) -> Dict:
    """提取PDF内容的主函数"""
    extractor = PDFExtractor(pdf_path)

    result = {
        "metadata": extractor.get_metadata(),
        "full_text": extractor.extract_all_text(),
        "chapters": extractor.extract_chapters(),
        "paragraphs": extractor.extract_paragraphs()
    }

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "full_text.txt", "w", encoding="utf-8") as f:
            f.write(result["full_text"])

        with open(output_dir / "chapters.json", "w", encoding="utf-8") as f:
            json.dump(result["chapters"], f, ensure_ascii=False, indent=2)

        with open(output_dir / "paragraphs.json", "w", encoding="utf-8") as f:
            json.dump(result["paragraphs"], f, ensure_ascii=False, indent=2)

        logger.info(f"内容已保存到: {output_dir}")

    extractor.close()
    return result


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "../data/book.pdf"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "../output"
    result = extract_pdf_content(pdf_path, output_dir)
    print(f"提取完成: {result['metadata']['page_count']}页")
