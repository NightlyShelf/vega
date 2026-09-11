from json import loads


class FormatHelper:
    @staticmethod
    def parse_sse_chunk(content: str) -> str | None:
        if content.startswith('data: {"text": "') and content.endswith("}\n"):
            return loads(content[6:-1])["text"]
        else:
            return None
