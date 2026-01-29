def build_sales_response(
    language: str,
    products: list
) -> dict:
    if not products:
        return {
            "message": (
                "Non ho trovato prodotti adatti."
                if language == "it"
                else "I couldn't find suitable products."
            ),
            "products": [],
            "follow_up": None
        }

    intro = (
        "Ecco alcune opzioni che potrebbero fare al caso tuo:"
        if language == "it"
        else "Here are some options that might fit your needs:"
    )

    follow_up = (
        "Hai un budget massimo o un uso specifico?"
        if language == "it"
        else "Do you have a budget range or a specific use case?"
    )

    return {
        "message": intro,
        "products": products,
        "follow_up": follow_up
    }
