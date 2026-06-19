from pathlib import Path


class RAGService:

    KB_PATH = Path(
        "datasets/knowledge_base"
    )

    @classmethod
    def retrieve_context(cls, query: str = ""):

        documents = []

        for file in cls.KB_PATH.glob("*.txt"):

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                documents.append(
                    f.read()
                )

        return "\n\n".join(documents)