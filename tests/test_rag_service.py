from app.rag.service import RAGService


if __name__ == "__main__":

    rag = RAGService()

    try:
        role = input(
            "Test as which role (employee/manager/ceo)? "
        ).strip().lower()

        question = input(
            "Ask a company-policy question: "
        )

        result = rag.answer_question(
            question=question,
            role=role
        )

        print("\nANSWER:\n")
        print(result["answer"])

        print("\nSOURCES:\n")
        for source in result["sources"]:
            print("-", source)

    finally:
        rag.close()