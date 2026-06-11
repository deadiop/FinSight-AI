def categorize_transaction(description):

    description = description.lower()

    if "salary" in description:
        return "Income"

    elif "freelance" in description:
        return "Income"

    elif "swiggy" in description:
        return "Food"

    elif "zomato" in description:
        return "Food"

    elif "amazon" in description:
        return "Shopping"

    elif "flipkart" in description:
        return "Shopping"

    elif "petrol" in description:
        return "Fuel"

    elif "electricity" in description:
        return "Utilities"

    elif "netflix" in description:
        return "Entertainment"

    elif "upi" in description:
        return "Transfer"

    return "Other"